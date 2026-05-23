# corre blender ou script python conforme MODELING_PROFILE para gerar geometria
# atualiza objeto job mutavel partilhado pelo router e pela tarefa em background
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from backend.app.services.mesh_job_runner import (
    acquire_mesh_slot,
    release_mesh_slot,
    run_command_async,
    should_open_blender_gui,
)

from bedflow_local_paths import models_3d_dir, resolve_existing_artifact

from backend.app.services.blender_launch import (
    BLENDER_IMPORT_LOG_HINT,
    default_subprocess_log,
    pick_mesh_to_open_in_gui,
    popen_blender_mesh,
)
from backend.app.api.models import JobStatus
from backend.app import config as app_config
from backend.app.services.job_persistence import persist_job

try:
    from bedflow_export_metadata import enrich_export_metadata, file_content_hash
except ImportError:
    enrich_export_metadata = None  # type: ignore
    file_content_hash = None  # type: ignore


def _profile_from_bed_json(json_path: Path, modeling_profile: Optional[str]) -> str:
    try:
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError, ValueError):
        return _normalize_modeling_profile(modeling_profile)

    packing = data.get("packing") if isinstance(data.get("packing"), dict) else {}
    method = str(packing.get("method") or data.get("packing_mode") or "").lower()
    gm = str(data.get("geometry_mode") or "").lower()

    if modeling_profile not in (None, ""):
        profile = _normalize_modeling_profile(modeling_profile)
    else:
        gb = str(data.get("generation_backend") or "").strip().lower()
        if gb in ("python_engine", "pure_python", "python"):
            profile = "python"
        else:
            profile = _normalize_modeling_profile(None)

    if method == "dem" and profile == "blender":
        profile = "python"
    if gm in ("pseudo_2d_statistical", "statistical") and profile == "blender":
        profile = "python"
    return profile


def _export_formats_cli_from_json(json_path: Path) -> str:
    try:
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError, ValueError):
        return "blend,stl,obj"
    exp = data.get("export") if isinstance(data, dict) else None
    if not isinstance(exp, dict):
        return "blend,stl,obj"
    raw = exp.get("formats")
    tokens: list[str] = []
    if isinstance(raw, list):
        for item in raw:
            s = str(item).strip().lower()
            if s in ("stl_binary", "stl"):
                tokens.append("stl")
            elif s in ("blend", "obj", "gltf", "glb", "fbx"):
                tokens.append(s)
    if not tokens:
        return "blend,stl,obj"
    return ",".join(dict.fromkeys(tokens))


def _normalize_modeling_profile(modeling_profile: Optional[str]) -> str:
    # converte texto da api ou do config para um de dois motores internos
    # modeling profile pode ser none entao cai no default global
    # raw fica em minusculas sem espacos laterais
    # pure python e python disparam o script packed bed stl sem blender
    # blender python e blender disparam leito extracao com blender
    # qualquer outro valor levanta erro cedo para o cliente corrigir o json
    raw = (modeling_profile or app_config.MODELING_PROFILE or "blender").strip().lower()
    if raw in ("pure_python", "python"):
        return "python"
    if raw in ("blender_python", "blender"):
        return "blender"
    raise ValueError(
        f"modeling_profile invalido: {raw} "
        "(use blender blender_python python ou pure_python)"
    )


class BlenderService:
    # prepara caminhos de saida tipicos generated 3d output
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.scripts_dir = self.project_root / "scripts" / "blender_scripts"
        self.leito_script = self.scripts_dir / "leito_extracao.py"
        self.output_dir = models_3d_dir()
        self.python_stl_script = (
            self.project_root / "scripts" / "python_modeling" / "packed_bed_stl.py"
        )
        
        # detectar blender
        self.blender_exe = self._find_blender()
    
    def _find_blender(self) -> str:
        """encontra executável do blender"""
        import platform
        
        system = platform.system()
        
        # caminhos comuns
        if system == "Windows":
            common_paths = [
                r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            ]
        elif system == "Linux":
            common_paths = [
                "/usr/bin/blender",
                "/usr/local/bin/blender",
            ]
        else:  # macOS
            common_paths = [
                "/Applications/Blender.app/Contents/MacOS/Blender",
            ]
        
        for path in common_paths:
            if Path(path).exists():
                return path
        
        # tentar comando simples
        return "blender"
    
    def check_availability(self) -> bool:
        """verifica se blender está disponível"""
        try:
            result = subprocess.run(
                [self.blender_exe, "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def _validate_stl_nonempty(self, stl_path: Path) -> None:
        if not stl_path.is_file():
            raise FileNotFoundError(f"stl não encontrado: {stl_path}")
        if stl_path.stat().st_size < 84:
            raise ValueError("stl vazio ou corrupto (ficheiro demasiado pequeno)")
        data = stl_path.read_bytes()
        if data[:5].lower() == b"solid":
            if b"vertex" not in data[:8000].lower():
                raise ValueError("stl ascii sem vértices")
            return
        if len(data) >= 84:
            n_tri = int.from_bytes(data[80:84], "little")
            if n_tri < 1:
                raise ValueError("stl binário sem triângulos")

    def _finalize_python_stl_metadata(
        self,
        job,
        stl_path: Path,
        json_path: Path,
        *,
        job_id: str,
    ) -> None:
        self._validate_stl_nonempty(stl_path)
        try:
            bed_data = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            bed_data = {}
        if file_content_hash is not None:
            job.metadata["content_hash"] = file_content_hash(stl_path)
        packing = bed_data.get("packing") if isinstance(bed_data.get("packing"), dict) else {}
        if packing.get("random_seed") is not None:
            job.metadata["packing_random_seed"] = packing["random_seed"]
        particles = bed_data.get("particles") if isinstance(bed_data.get("particles"), dict) else {}
        if particles.get("seed") is not None:
            job.metadata["particles_seed"] = particles["seed"]
        gm = bed_data.get("geometry_mode")
        if gm:
            job.metadata["geometry_mode"] = gm
        sidecar = stl_path.parent / f"{stl_path.stem}_pure_bed.json"
        if sidecar.is_file():
            try:
                sc = json.loads(sidecar.read_text(encoding="utf-8"))
                if enrich_export_metadata is not None:
                    sc = enrich_export_metadata(
                        sc,
                        bed_data=bed_data,
                        job_id=job_id,
                        modeling_profile="python",
                        mesh_path=stl_path,
                    )
                else:
                    sc["generation_backend"] = "python_engine"
                    sc["job_id"] = job_id
                sidecar.write_text(
                    json.dumps(sc, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                job.metadata["geometry_mode"] = sc.get(
                    "geometry_mode", job.metadata.get("geometry_mode")
                )
                job.metadata["representation_dimension"] = sc.get(
                    "representation_dimension"
                )
                job.metadata["bed_particle_layout"] = sc.get("bed_particle_layout")
            except (OSError, json.JSONDecodeError):
                pass
        elif enrich_export_metadata is not None:
            sc = enrich_export_metadata(
                {"generation_backend": "python_engine", "geometry_mode": gm},
                bed_data=bed_data,
                job_id=job_id,
                modeling_profile="python",
                mesh_path=stl_path,
            )
            sidecar.write_text(
                json.dumps(sc, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    def _finalize_blender_export_metadata(
        self,
        job,
        blend_path: Path,
        json_path: Path,
        *,
        job_id: str,
    ) -> None:
        try:
            bed_data = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            bed_data = {}
        packing = (
            bed_data.get("packing") if isinstance(bed_data.get("packing"), dict) else {}
        )
        if packing.get("random_seed") is not None:
            job.metadata["packing_random_seed"] = packing["random_seed"]
        particles = (
            bed_data.get("particles")
            if isinstance(bed_data.get("particles"), dict)
            else {}
        )
        if particles.get("seed") is not None:
            job.metadata["particles_seed"] = particles["seed"]
        gm = bed_data.get("geometry_mode")
        if gm:
            job.metadata["geometry_mode"] = gm
        job.metadata["generation_backend"] = str(
            bed_data.get("generation_backend") or "blender"
        )
        job.metadata["job_id"] = job_id
        job.metadata["modeling_profile"] = "blender"

        stl_path = blend_path.with_suffix(".stl")
        if stl_path.is_file():
            rel_stl = str(stl_path.relative_to(self.project_root)).replace("\\", "/")
            job.metadata["stl_path"] = rel_stl
            if rel_stl not in (job.output_files or []):
                job.output_files = list(job.output_files or []) + [rel_stl]
            try:
                self._validate_stl_nonempty(stl_path)
            except ValueError:
                pass
            if file_content_hash is not None:
                job.metadata["content_hash"] = file_content_hash(stl_path)

        sidecar = blend_path.parent / f"{blend_path.stem}_pure_bed.json"
        mesh_for_sidecar = stl_path if stl_path.is_file() else None
        if sidecar.is_file():
            try:
                sc = json.loads(sidecar.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                sc = {}
        else:
            sc = {}
        if enrich_export_metadata is not None:
            sc = enrich_export_metadata(
                sc,
                bed_data=bed_data,
                job_id=job_id,
                modeling_profile="blender",
                mesh_path=mesh_for_sidecar,
            )
            try:
                sidecar.write_text(
                    json.dumps(sc, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
            except OSError:
                pass
        for key in (
            "geometry_mode",
            "representation_dimension",
            "bed_particle_layout",
            "internal_cylinder_mode",
            "content_hash",
            "packing_random_seed",
            "particles_seed",
            "slice",
            "slice_particle_summary",
        ):
            if sc.get(key) is not None:
                job.metadata[key] = sc[key]
    
    async def generate_model(
        self,
        job_id: str,
        json_file: str,
        open_blender: bool,
        jobs_store: Dict[str, Any],
        bed_id: Optional[int] = None,
        db_session = None,
        modeling_profile: Optional[str] = None,
    ):
        """
        gera modelo 3d (executado em background)
        
        args:
            job_id: id do job
            json_file: caminho do arquivo json
            open_blender: abrir blender gui após gerar
            jobs_store: armazenamento de jobs
        """
        job = jobs_store[job_id]

        if not await acquire_mesh_slot(job_id):
            job.status = JobStatus.FAILED
            job.error_message = (
                "outra geração de modelo já está em curso; aguarde o job anterior terminar"
            )
            job.updated_at = datetime.now()
            persist_job(job)
            return

        try:
            job.status = JobStatus.RUNNING
            job.progress = 10
            job.updated_at = datetime.now()
            persist_job(job)

            json_path = self.project_root / json_file
            if not json_path.exists():
                alt = resolve_existing_artifact(str(json_file).replace("\\", "/").lstrip("/"))
                if alt and alt.is_file():
                    json_path = alt
            if not json_path.exists():
                raise FileNotFoundError(f"arquivo json não encontrado: {json_file}")

            profile = _profile_from_bed_json(json_path, modeling_profile)
            job.metadata["modeling_profile"] = profile
            persist_job(job)

            def _touch_progress(pct: float, _line: str = "") -> None:
                job.progress = max(float(job.progress or 0), min(99.0, float(pct)))
                job.updated_at = datetime.now()
                persist_job(job)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if profile == "python":
                if not self.python_stl_script.exists():
                    raise FileNotFoundError(f"script python modeling nao encontrado: {self.python_stl_script}")
                stl_filename = f"leito_{timestamp}.stl"
                stl_path = self.output_dir / stl_filename
                job.progress = 30
                job.updated_at = datetime.now()
                persist_job(job)
                run_env = {
                    **os.environ,
                    "BEDFLOW_PROGRESS_UI": "0",
                    "BEDFLOW_JOB_ID": job_id,
                }
                py_cmd = [
                    sys.executable,
                    str(self.python_stl_script),
                    str(json_path),
                    str(stl_path),
                    "--no-progress",
                ]
                rc, out = await run_command_async(
                    py_cmd,
                    cwd=str(self.project_root),
                    env=run_env,
                    timeout_sec=600.0,
                    on_progress=_touch_progress,
                )
                job.progress = 80
                job.updated_at = datetime.now()
                persist_job(job)
                if rc != 0:
                    raise Exception(f"erro na geracao python/stl: {out[-4000:]}")
                if not stl_path.exists():
                    raise Exception("arquivo .stl nao foi gerado")
                rel = str(stl_path.relative_to(self.project_root)).replace("\\", "/")
                job.status = JobStatus.COMPLETED
                job.progress = 100
                job.updated_at = datetime.now()
                job.output_files = [rel]
                job.metadata["geometry_file"] = rel
                job.metadata["stl_path"] = rel
                job.metadata["generation_backend"] = "python_engine"
                job.metadata["modeling_profile"] = "python"
                job.metadata["job_id"] = job_id
                self._finalize_python_stl_metadata(
                    job, stl_path, json_path, job_id=job_id
                )
            else:
                if not self.check_availability():
                    raise RuntimeError(
                        "perfil blender mas blender nao disponivel; use MODELING_PROFILE=python ou instale blender"
                    )
                blend_filename = f"leito_{timestamp}.blend"
                blend_path = self.output_dir / blend_filename
                job.progress = 30
                job.updated_at = datetime.now()
                persist_job(job)
                cmd = [
                    self.blender_exe,
                    "--background",
                    "--python", str(self.leito_script),
                    "--",
                    "--params", str(json_path),
                    "--output", str(blend_path)
                ]
                run_env = {**os.environ, "BEDFLOW_JOB_ID": job_id}
                rc, out = await run_command_async(
                    cmd,
                    cwd=str(self.project_root),
                    env=run_env,
                    timeout_sec=600.0,
                    on_progress=_touch_progress,
                )
                job.progress = 80
                job.updated_at = datetime.now()
                persist_job(job)
                if rc != 0:
                    raise Exception(f"erro no blender: {out[-4000:]}")
                if not blend_path.exists():
                    raise Exception("arquivo .blend não foi gerado")
                rel = str(blend_path.relative_to(self.project_root))
                job.status = JobStatus.COMPLETED
                job.progress = 100
                job.updated_at = datetime.now()
                job.output_files = [rel]
                job.metadata["geometry_file"] = rel
                job.metadata["blend_file"] = rel
                self._finalize_blender_export_metadata(
                    job, blend_path, json_path, job_id=job_id
                )
            
            # atualizar bed no banco se fornecido
            if bed_id:
                from backend.app.database import crud, schemas
                from backend.app.database.connection import DatabaseConnection

                own_session = None
                session = db_session
                if session is None:
                    own_session = DatabaseConnection.get_session()
                    session = own_session

                geom_rel = job.metadata.get("geometry_file") or job.metadata.get("blend_file")
                update_kwargs: Dict[str, Any] = {}
                stl_rel = job.metadata.get("stl_path")
                if stl_rel and str(stl_rel).lower().endswith(".stl"):
                    update_kwargs["stl_file_path"] = stl_rel
                if geom_rel:
                    if str(geom_rel).lower().endswith(".stl"):
                        update_kwargs["stl_file_path"] = geom_rel
                    elif str(geom_rel).lower().endswith(".blend"):
                        update_kwargs["blend_file_path"] = geom_rel
                if geom_rel and str(geom_rel).lower().endswith(".stl"):
                    geom_path = self.project_root / geom_rel
                    sidecar = geom_path.parent / f"{geom_path.stem}_pure_bed.json"
                    report = geom_path.parent / f"{geom_path.stem}_packing_report.json"
                    meta_extra: Dict[str, Any] = {}
                    if sidecar.is_file():
                        try:
                            meta_extra = json.loads(sidecar.read_text(encoding="utf-8"))
                        except json.JSONDecodeError:
                            meta_extra = {}
                    porosity = meta_extra.get("porosity_estimate")
                    if porosity is not None:
                        update_kwargs["porosity"] = float(porosity)
                    bed_row = crud.BedCRUD.get(session, bed_id)
                    params = dict(bed_row.parameters_json or {}) if bed_row else {}
                    params["porosity_result"] = porosity
                    params["packing_report_path"] = (
                        str(report.relative_to(self.project_root))
                        if report.is_file()
                        else meta_extra.get("packing_report_path")
                    )
                    params["geometry_mode"] = meta_extra.get("geometry_mode")
                    params["generation_backend"] = meta_extra.get("generation_backend")
                    params["packing_method"] = meta_extra.get("packing_method")
                    update_kwargs["parameters_json"] = params
                if update_kwargs:
                    update_data = schemas.BedUpdate(**update_kwargs)
                    crud.BedCRUD.update(session, bed_id, update_data)
                if own_session is not None:
                    own_session.close()
            
            open_gui = should_open_blender_gui(open_blender)
            if open_blender and not open_gui:
                job.metadata["open_blender_skipped"] = (
                    "gui ignorada no servidor (defina BEDFLOW_ALLOW_BLENDER_GUI=1 para permitir)"
                )
            if open_gui:
                stl_rel = job.metadata.get("stl_path")
                blend_rel = job.metadata.get("blend_file")
                stl_p = (
                    (self.project_root / str(stl_rel)).resolve()
                    if stl_rel
                    else None
                )
                blend_p = (
                    (self.project_root / str(blend_rel)).resolve()
                    if blend_rel
                    else None
                )
                to_open = pick_mesh_to_open_in_gui(
                    blend_path=blend_p, stl_path=stl_p
                )
                if to_open is not None:
                    popen_blender_mesh(
                        self.blender_exe,
                        to_open,
                        project_root=self.project_root,
                        log_file=default_subprocess_log(self.project_root),
                    )
                    try:
                        rel_open = str(
                            to_open.relative_to(self.project_root)
                        ).replace("\\", "/")
                    except ValueError:
                        rel_open = str(to_open)
                    job.metadata["blender_gui_opened"] = rel_open
                    job.metadata["blender_import_log_hint"] = BLENDER_IMPORT_LOG_HINT
            
        except asyncio.TimeoutError:
            job.status = JobStatus.FAILED
            job.error_message = "timeout na geração do modelo (limite 10 min)"
            job.updated_at = datetime.now()

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.updated_at = datetime.now()
        finally:
            await release_mesh_slot(job_id)
            persist_job(job)

