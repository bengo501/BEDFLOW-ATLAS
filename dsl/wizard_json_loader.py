# leitura e normalizacao de json para o bed wizard e para a linha de comandos
# o compilador antlr gera json a partir do texto bed mas a gramatica nao inclui gap nem random seed
# por isso patch_compiled_json_packing reescreve o json depois da compilacao com campos cientificos
# export_formats_for_blender traduz nomes stl binary para stl que o script blender aceita
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# caminho deste ficheiro dentro da pasta dsl
_DSL = Path(__file__).resolve().parent
# raiz do repositorio um nivel acima de dsl
_REPO_ROOT = _DSL.parent
# pasta scripts blender_scripts onde vive packed_bed_science
_BLENDER_SCRIPTS = _REPO_ROOT / "scripts" / "blender_scripts"
if str(_BLENDER_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_BLENDER_SCRIPTS))

from packed_bed_science.packing_modes import (  # noqa: E402
    merge_root_packing_mode,
    normalize_packing_mode,
    packing_method_from_section,
)

# bed_config vive em scripts python modeling geometria e generation backend
_PM = _REPO_ROOT / "scripts" / "python_modeling"
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from bed_internal_modes import (  # noqa: E402
    default_visibility_for_mode,
    normalize_internal_cylinder_mode,
)
from bed_config import (  # noqa: E402
    bed_section_for_wizard,
    merge_root_generation_backend,
    normalize_generation_backend,
)


def resolve_repo_path(path_str: str, base: Optional[Path] = None) -> Path:
    # path_str e texto que o utilizador escreveu pode ser relativo ou absoluto
    # base opcional permite resolver relativo a uma pasta conhecida
    # expanduser trata til home em unix
    p = Path(path_str).expanduser()
    if not p.is_absolute():
        if base is not None:
            p = (base / p).resolve()
        else:
            p = p.resolve()
    else:
        p = p.resolve()
    return p


def parse_spec(spec: str, base: Optional[Path] = None) -> Tuple[str, Path]:
    # formato pedido label arroba caminho
    # label serve so para nomear o bed de saida no cli
    # caminho e o json real a carregar
    # partition divide so na primeira arroba para caminhos com arroba raros
    spec = spec.strip()
    if "@" in spec:
        label, _, path_part = spec.partition("@")
        label = label.strip() or "config"
        path_part = path_part.strip()
    else:
        path_part = spec
        label = Path(path_part).stem or "config"
    return label, resolve_repo_path(path_part, base=base)


def load_wizard_json(path: Path) -> Dict[str, Any]:
    # abre utf8 e faz load do json
    # exige dict na raiz porque o resto do codigo assume chaves bed packing etc
    # normalize_loaded_dict aplica merge packing mode no topo
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("json raiz deve ser um objeto")
    normalize_loaded_dict(data)
    return data


def normalize_loaded_dict(data: Dict[str, Any]) -> None:
    # alias fino para merge_root_packing_mode
    # packing_mode no topo passa a packing method quando method falta
    merge_root_packing_mode(data)
    # esta linha garante que se o usuario usar generation no formato interno
    # a raiz passa a ter generation_backend
    # isso e importante porque o gerador pure python decide o modo com base nesse valor
    merge_root_generation_backend(data)


def json_to_wizard_params(data: Dict[str, Any]) -> Dict[str, Any]:
    # converte o json plano das fixtures para o formato interno self params do BedWizard
    # generate_bed_content le self params e escreve texto bed
    # cada subdict usa get com default para nao rebentar se a chave faltar
    merge_root_generation_backend(data)
    bed = bed_section_for_wizard(dict(data.get("bed") or {}))
    particles = dict(data.get("particles") or {})
    lids = dict(data.get("lids") or {})
    packing = dict(data.get("packing") or {})
    export = dict(data.get("export") or {})
    cfd_raw = data.get("cfd") or {}
    cfd = dict(cfd_raw) if cfd_raw else {}

    # se o json trouxe packing mode na raiz e method vazio preenche aqui tambem
    if packing.get("method") in (None, "") and data.get("packing_mode"):
        packing["method"] = normalize_packing_mode(data.get("packing_mode"))

    kind = str(particles.get("kind") or "sphere").strip().strip('"')
    icm = normalize_internal_cylinder_mode(bed.get("internal_cylinder_mode"))
    vis_raw = bed.get("visibility")
    vis = default_visibility_for_mode(icm)
    if isinstance(vis_raw, dict):
        for k in vis:
            if k in vis_raw:
                vis[k] = bool(vis_raw[k]) if isinstance(vis_raw[k], bool) else str(vis_raw[k]).lower() in ("true", "1", "yes")
    params: Dict[str, Any] = {
        "bed": {
            "diameter": bed.get("diameter", 0.05),
            "height": bed.get("height", 0.1),
            "wall_thickness": bed.get("wall_thickness", 0.002),
            "clearance": bed.get("clearance", 0.01),
            "material": bed.get("material", "steel"),
            "roughness": bed.get("roughness", 0.0),
            "internal_cylinder_mode": icm,
            "visibility": vis,
        },
        "lids": {
            "top_type": str(lids.get("top_type") or "flat").strip().strip('"'),
            "bottom_type": str(lids.get("bottom_type") or "flat").strip().strip('"'),
            "top_thickness": lids.get("top_thickness", 0.003),
            "bottom_thickness": lids.get("bottom_thickness", 0.003),
            "seal_clearance": lids.get("seal_clearance", 0.001),
        },
        "particles": {
            "kind": kind,
            "diameter": particles.get("diameter", 0.005),
            "count": int(particles.get("count", 100)),
            "target_porosity": particles.get("target_porosity", 0.4),
            "density": particles.get("density", 2500.0),
            "mass": particles.get("mass", 0.0),
            "restitution": particles.get("restitution", 0.3),
            "friction": particles.get("friction", 0.5),
            "rolling_friction": particles.get("rolling_friction", 0.1),
            "linear_damping": particles.get("linear_damping", 0.1),
            "angular_damping": particles.get("angular_damping", 0.1),
            "seed": particles.get("seed", 42),
        },
        "packing": {
            "method": packing_method_from_section(packing),
            "gravity": packing.get("gravity", -9.81),
            "substeps": int(packing.get("substeps", 10)),
            "iterations": int(packing.get("iterations", 10)),
            "damping": packing.get("damping", 0.1),
            "rest_velocity": packing.get("rest_velocity", 0.01),
            "max_time": packing.get("max_time", 5.0),
            "collision_margin": packing.get("collision_margin", 0.001),
        },
        "export": {
            "formats": export.get("formats", ["blend", "stl"]),
            "units": export.get("units", "m"),
            "scale": export.get("scale", 1.0),
            "wall_mode": export.get("wall_mode", "surface"),
            "fluid_mode": export.get("fluid_mode", "none"),
            "manifold_check": export.get("manifold_check", True),
            "merge_distance": export.get("merge_distance", 0.001),
        },
    }
    # estes campos so existem nos modos spherical packing e hexagonal 3d
    # o compilador bed nao os grava no json por limitacao da gramatica
    for key in (
        "gap",
        "random_seed",
        "max_placement_attempts",
        "strict_validation",
        "step_x",
        "mesh_segmentos",
        "sphere_lat",
        "sphere_lon",
        "dem",
        "use_legacy_drop",
    ):
        if key in packing:
            params["packing"][key] = packing[key]
    # secao cfd so entra se o json original tiver algo em cfd
    if cfd:
        params["cfd"] = {
            "regime": str(cfd.get("regime", "laminar")).strip().strip('"'),
            "inlet_velocity": cfd.get("inlet_velocity", 0.1),
            "fluid_density": cfd.get("fluid_density", 1.225),
            "fluid_viscosity": cfd.get("fluid_viscosity", 1.8e-5),
            "max_iterations": int(cfd.get("max_iterations", 1000)),
            "convergence_criteria": cfd.get("convergence_criteria", 1e-6),
            "write_fields": cfd.get("write_fields", False),
        }
    # packing_mode e um resumo simples do modo de empacotamento
    # este resumo e usado por varios fluxos como menues e patches
    pm_final = str(params["packing"]["method"])
    params["packing_mode"] = pm_final

    # generation_backend e o resumo do modo de geracao de geometria
    # pure python significa que usamos o gerador de stl sem blender
    # blender significa que o pipeline usa o leito extracao dentro do blender
    params["generation_backend"] = normalize_generation_backend(data.get("generation_backend"))

    try:
        _gm_dir = _REPO_ROOT / "scripts" / "python_modeling"
        if str(_gm_dir) not in sys.path:
            sys.path.insert(0, str(_gm_dir))
        from geometry_modes import (  # noqa: WPS433
            geometry_mode_from_data,
            resolve_slice_config,
            resolve_statistical_config,
        )

        params["geometry_mode"] = geometry_mode_from_data(data)
        sl = resolve_slice_config(data)
        if sl:
            params["slice"] = sl
        else:
            params.pop("slice", None)
        st = resolve_statistical_config(data)
        if st:
            params["statistical_2d"] = st
        else:
            params.pop("statistical_2d", None)
    except ImportError:
        params["geometry_mode"] = str(data.get("geometry_mode") or "full_3d")
        if data.get("slice"):
            params["slice"] = dict(data.get("slice") or {})
        if data.get("statistical_2d"):
            params["statistical_2d"] = dict(data.get("statistical_2d") or {})

    return params


def apply_quick_test_overrides(
    json_path: Path,
    *,
    packing_method: Optional[str] = None,
    generation_backend: Optional[str] = None,
) -> None:
    # objetivo escrever no disco o mesmo json que o utilizador veria depois do menu testes rapidos
    # packing method quando nao e none vira o campo packing method canonico
    # generation backend quando nao e none vira pure python ou blender na raiz
    # o ficheiro e lido inteiro alterado em memoria e gravado de volta com indentacao estavel
    # normalize loaded dict recalcula campos derivados como packing mode resumo e backend
    path = Path(json_path).resolve()
    # leitura utf8 evita surpresas com caracteres nao ascii em caminhos ou notas
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # raiz tem de ser objeto para podermos atribuir chaves packing e generation backend
    if not isinstance(data, dict):
        raise ValueError("json raiz deve ser um objeto")
    # ramo packing so corre se o chamador pediu mudanca explicita
    if packing_method is not None:
        # pm e a string final aceite pelo motor spherical packing hexagonal 3d ou rigid body
        pm = normalize_packing_mode(packing_method)
        # copia dict existente para nao partilhar referencia acidental com outras estruturas
        pack = dict(data.get("packing") or {})
        # method dentro de packing e o que pure generation e blender leem primeiro
        pack["method"] = pm
        data["packing"] = pack
        # packing mode na raiz e redundancia util para menus e patches rapidos
        data["packing_mode"] = pm
    # ramo backend alinha gerador stl local versus cena blender
    if generation_backend is not None:
        data["generation_backend"] = normalize_generation_backend(generation_backend)
    # reforca coerencia entre dicts internos e campos resumo no topo do json
    normalize_loaded_dict(data)
    # grava pretty print sem escapar unicode em nomes de ficheiro ou strings livres
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _load_compiled_json(json_path: Path) -> Dict[str, Any]:
    with json_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_compiled_json(json_path: Path, data: Dict[str, Any]) -> None:
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def patch_compiled_json_bed(json_path: Path, wizard_params: Dict[str, Any]) -> None:
    wbed = wizard_params.get("bed") or {}
    if not wbed:
        return
    data = _load_compiled_json(json_path)
    bed = dict(data.get("bed") or {})
    if not bed.get("internal_cylinder_mode") and wbed.get("internal_cylinder_mode"):
        bed["internal_cylinder_mode"] = wbed["internal_cylinder_mode"]
    wvis = wbed.get("visibility")
    if isinstance(wvis, dict) and wvis:
        cur = bed.get("visibility") if isinstance(bed.get("visibility"), dict) else {}
        for k, v in wvis.items():
            if k not in cur and v is not None:
                cur[k] = v
        if cur:
            bed["visibility"] = cur
    data["bed"] = bed
    _save_compiled_json(json_path, data)


def patch_compiled_json_packing(
    json_path: Path, wizard_params: Dict[str, Any]
) -> None:
    wpack = wizard_params.get("packing") or {}
    if not wpack:
        return
    data = _load_compiled_json(json_path)
    pack = dict(data.get("packing") or {})
    if not pack.get("method") and wpack.get("method"):
        pack["method"] = str(wpack["method"])
    for key in (
        "gap",
        "random_seed",
        "max_placement_attempts",
        "strict_validation",
        "step_x",
        "mesh_segmentos",
        "sphere_lat",
        "sphere_lon",
        "dem",
        "use_legacy_drop",
    ):
        if key in wpack and wpack[key] is not None and pack.get(key) is None:
            pack[key] = wpack[key]
    data["packing"] = pack
    _save_compiled_json(json_path, data)


def patch_compiled_json_export(
    json_path: Path, wizard_params: Dict[str, Any]
) -> None:
    # alinha export formats entre wizard e json compilado
    # necessario porque lista de formatos pode ter stl binary no wizard
    wexp = wizard_params.get("export")
    if not wexp or "formats" not in wexp:
        return
    data = _load_compiled_json(json_path)
    exp = dict(data.get("export") or {})
    if not exp.get("formats"):
        exp["formats"] = wexp["formats"]
    for key in ("units", "scale", "wall_mode", "fluid_mode", "manifold_check", "merge_distance"):
        if key in wexp and exp.get(key) is None:
            exp[key] = wexp[key]
    data["export"] = exp
    _save_compiled_json(json_path, data)


def patch_compiled_json_metadata(
    json_path: Path, wizard_params: Dict[str, Any]
) -> None:
    # grava generation_backend e packing_mode na raiz para consumo do motor pure python
    # este patch e necessario porque o compilador antlr
    # trabalha com a gramatica do arquivo bed
    # e essa gramatica nao necessariamente serializa campos novos como generation_backend
    # entao garantimos que os motores downstream tenham os metadados necessarios
    gb = wizard_params.get("generation_backend")
    gm = wizard_params.get("geometry_mode")
    pm = wizard_params.get("packing_mode") or (wizard_params.get("packing") or {}).get(
        "method"
    )
    if gb is None and gm is None and not pm:
        return
    data = _load_compiled_json(json_path)
    if gb is not None and not data.get("generation_backend"):
        data["generation_backend"] = gb
    if gm is not None and not data.get("geometry_mode"):
        data["geometry_mode"] = gm
    if pm and not data.get("packing_mode"):
        data["packing_mode"] = str(pm)
    _save_compiled_json(json_path, data)


def patch_compiled_json_slice(json_path: Path, wizard_params: Dict[str, Any]) -> None:
    # guarda configuracao de thin slice no json compilado
    # a gramatica bed nao conhece esta secao, entao ela so existe se o wizard a adicionou
    ws = wizard_params.get("slice")
    if not isinstance(ws, dict) or not ws:
        return
    data = _load_compiled_json(json_path)
    if not data.get("slice"):
        data["slice"] = ws
    _save_compiled_json(json_path, data)


def patch_compiled_json_statistical(json_path: Path, wizard_params: Dict[str, Any]) -> None:
    ws = wizard_params.get("statistical_2d")
    gm = wizard_params.get("geometry_mode")
    data = _load_compiled_json(json_path)
    if gm is not None and not data.get("geometry_mode"):
        data["geometry_mode"] = gm
    if isinstance(ws, dict) and ws and not data.get("statistical_2d"):
        data["statistical_2d"] = ws
        if gm == "pseudo_2d_statistical":
            data.pop("slice", None)
    elif gm == "full_3d" and "statistical_2d" not in (wizard_params.get("statistical_2d") or {}):
        pass
    _save_compiled_json(json_path, data)


def export_formats_for_blender(export_section: Dict[str, Any]) -> str:
    # o argparse do leito_extracao espera uma string com formatos separados por virgula
    # nomes validos incluem blend stl gltf glb obj fbx
    # stl binary e nome do dsl mas o export scene no blender usa stl
    fmts = export_section.get("formats") or ["blend", "stl"]
    if isinstance(fmts, str):
        raw = [x.strip() for x in fmts.split(",")]
    else:
        raw = list(fmts)
    out: list[str] = []
    for f in raw:
        s = str(f).strip().lower().strip('"')
        if s in ("stl_binary", "stl_ascii"):
            s = "stl"
        if s and s not in out:
            out.append(s)
    if not out:
        out = ["blend", "stl"]
    return ",".join(out)
