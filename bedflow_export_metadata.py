# metadados partilhados de export (sidecar, jobs, viewer)
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, Optional

GEOMETRY_2D_MODES = frozenset(
    {"pseudo_2d_thin_slice", "pseudo_2d_statistical"}
)


def representation_dimension(geometry_mode: Optional[str]) -> str:
    gm = (geometry_mode or "full_3d").strip().lower()
    return "2d" if gm in GEOMETRY_2D_MODES else "3d"


def bed_particle_layout_from_internal_mode(internal_cylinder_mode: Optional[str]) -> str:
    m = (internal_cylinder_mode or "").strip().lower()
    if m in (
        "hollow_boolean_applied",
        "solid_internal_cylinder_with_particle_holes",
    ):
        return "boolean_holes"
    if m == "internal_cylinder_visible_no_boolean":
        return "solid_fill"
    return "unknown"


def file_content_hash(path: Path, *, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(chunk_size)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def enrich_export_metadata(
    extra: Dict[str, Any],
    *,
    bed_data: Optional[Dict[str, Any]] = None,
    job_id: Optional[str] = None,
    modeling_profile: Optional[str] = None,
    mesh_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """preenche campos de contrato unificado no sidecar."""
    out = dict(extra)
    gm = out.get("geometry_mode")
    if not gm and bed_data:
        gm = bed_data.get("geometry_mode")
    if gm:
        out["geometry_mode"] = str(gm)
    out["representation_dimension"] = representation_dimension(
        out.get("geometry_mode")
    )
    icm = out.get("internal_cylinder_mode")
    if not icm and bed_data:
        bed = bed_data.get("bed") if isinstance(bed_data.get("bed"), dict) else {}
        icm = bed.get("internal_cylinder_mode")
    if icm:
        out["internal_cylinder_mode"] = str(icm)
    out["bed_particle_layout"] = bed_particle_layout_from_internal_mode(
        out.get("internal_cylinder_mode")
    )
    if job_id:
        out["job_id"] = str(job_id)
    if modeling_profile:
        out["modeling_profile"] = str(modeling_profile)
    if bed_data:
        packing = bed_data.get("packing") if isinstance(bed_data.get("packing"), dict) else {}
        seed = packing.get("random_seed")
        if seed is None:
            seed = bed_data.get("random_seed")
        if seed is not None:
            out["packing_random_seed"] = seed
        particles = (
            bed_data.get("particles")
            if isinstance(bed_data.get("particles"), dict)
            else {}
        )
        pseed = particles.get("seed")
        if pseed is not None:
            out["particles_seed"] = pseed
    if mesh_path is not None and mesh_path.is_file():
        try:
            out["content_hash"] = file_content_hash(mesh_path)
        except OSError:
            pass
    gb = out.get("generation_backend")
    if not gb or str(gb).strip().lower() == "blender" and modeling_profile in (
        "python",
        "pure_python",
    ):
        out["generation_backend"] = "python_engine"
    return out
