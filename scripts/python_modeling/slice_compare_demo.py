#!/usr/bin/env python3
"""
demonstração da validação do corte 2d: gera a fatia 2d + o modelo 3d (antes do
corte) + os arquivos de comparação (lado a lado e sobreposto).

uso (gera tudo em generated/3d/slice_compare_demo/):
    python scripts/python_modeling/slice_compare_demo.py
    python scripts/python_modeling/slice_compare_demo.py overlay   # só um modo
"""
from __future__ import annotations

import sys
from pathlib import Path

_PM = Path(__file__).resolve().parent
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from engine.pipeline import generate_packed_bed  # noqa: E402


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    repo = _PM.parent.parent
    out_dir = repo / "generated" / "3d" / "slice_compare_demo"
    out_dir.mkdir(parents=True, exist_ok=True)

    params = dict(
        diameter=0.05, wall_thickness=0.003, height=0.08, bottom_thickness=0.004,
        top_thickness=0.004, gap=0.0005, particle_diameter=0.009, particle_kind="sphere",
        particle_count=40, packing_method="hexagonal_3d", mesh_segmentos=24,
        sphere_lat=5, sphere_lon=8, strict_validation=False,
        geometry_mode="pseudo_2d_thin_slice", particles_seed=11, packing={"seed": 11},
        slice={
            "slice_enabled": True,
            "slice_axis": "y",
            "slice_thickness": 0.004,
            "slice_position": 0.0,
            "compare_mode": mode,
        },
    )
    generate_packed_bed(params, out_dir / "leito.stl")

    print("=" * 64)
    print(f"  VALIDAÇÃO DO CORTE 2D — compare_mode = {mode}")
    print("=" * 64)
    print(f"saída em: {out_dir}\n")
    for f in sorted(out_dir.iterdir()):
        print(f"  {f.name:28s} {f.stat().st_size:>9} bytes")
    print(
        "\nabra os arquivos para validar o corte:\n"
        "  - leito.stl            = fatia 2D\n"
        "  - leito_full3d.stl     = leito 3D (antes do corte)\n"
        "  - leito_compare.obj    = 2D e 3D lado a lado (colorido)\n"
        "  - leito_overlay.obj    = 2D dentro do 3D translúcido (na posição do corte)"
    )


if __name__ == "__main__":
    main()
