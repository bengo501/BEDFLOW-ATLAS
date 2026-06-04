#!/usr/bin/env python3
"""
demonstração + validação do modo m2 (internal_cylinder_visible_no_boolean):
leito com interior SÓLIDO e as partículas FIXAS/embutidas dentro do sólido.

gera, em generated/3d/m2_demo/:
  - m2_leito.stl        : malha m2 real (parede anelar + tampas + núcleo + partículas)
  - m2_validacao.obj/.mtl: dois objetos coloridos — núcleo sólido TRANSLÚCIDO +
                           partículas SÓLIDAS — para VER as partículas dentro do sólido
                           (sem precisar cortar).

uso:
    python scripts/python_modeling/m2_demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_PM = Path(__file__).resolve().parent
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from bed_internal_modes import MODE_VISIBLE_INNER  # noqa: E402
from bed_shell_build import (  # noqa: E402
    _interior_span,
    _solid_cylinder_mesh,
    build_bed_shell,
    build_bed_with_internal_mode,
)
from stl_mesh_utils import merge_mesh, uv_sphere, write_stl_binary  # noqa: E402
from slice_compare import write_obj_multi  # noqa: E402


def main() -> None:
    repo = _PM.parent.parent
    out_dir = repo / "generated" / "3d" / "m2_demo"
    out_dir.mkdir(parents=True, exist_ok=True)

    r_ext, r_int, h, tb, tt = 0.025, 0.020, 0.08, 0.004, 0.004
    d_part = 0.010
    # partículas espalhadas dentro do interior (todas dentro do núcleo)
    centers = [
        (0.0, 0.0, 0.018), (0.010, 0.0, 0.028), (-0.010, 0.0, 0.040),
        (0.0, 0.010, 0.052), (0.0, -0.010, 0.064), (0.008, 0.008, 0.034),
        (-0.008, -0.008, 0.058),
    ]
    vis = {"show_internal_cylinder": True, "show_particles": True}

    # 1) malha m2 real (merge de parede+tampas+núcleo+partículas embutidas)
    v, f, meta = build_bed_with_internal_mode(
        {"bed": {"internal_cylinder_mode": MODE_VISIBLE_INNER, "visibility": vis}},
        r_ext, r_int, h, tb, tt, centers, d_part, "sphere", segmentos=32,
    )
    write_stl_binary(out_dir / "m2_leito.stl", v, f)

    # 2) validação: separa em "leito sólido" (parede+tampas+núcleo) e "partículas"
    sv, sf, _ = build_bed_shell(
        MODE_VISIBLE_INNER, r_ext, r_int, h, vis,
        segmentos=32, bottom_cap_thickness=tb, top_cap_thickness=tt,
    )
    z0, z1 = _interior_span(h, tb, tt)
    cv, cf = _solid_cylinder_mesh(r_int, h, 32, z_bottom=z0, z_top=z1)
    solid_v, solid_f = merge_mesh(sv, sf, cv, cf)

    pv: list = []
    pf: list = []
    for cx, cy, cz in centers:
        s_v, s_f = uv_sphere(cx, cy, cz, d_part / 2.0, lat=8, lon=12)
        pv, pf = merge_mesh(pv, pf, s_v, s_f)

    write_obj_multi(
        out_dir / "m2_validacao.obj",
        [
            ("leito_solido", solid_v, solid_f, "bed_solido"),
            ("particulas", pv, pf, "particulas"),
        ],
        mtl_path=out_dir / "m2_validacao.mtl",
        materials={
            "bed_solido": {"Kd": (0.74, 0.78, 0.83), "d": 0.20},   # sólido translúcido
            "particulas": {"Kd": (0.92, 0.27, 0.10), "d": 1.0},    # partículas sólidas
        },
    )

    st = meta["boolean_operation_status"]
    print("=" * 64)
    print("  DEMO m2 — interior sólido com partículas fixas dentro")
    print("=" * 64)
    print(f"inner_core        : {st.get('inner_core')}")
    print(f"particle_tools    : {st.get('particle_tools')}")
    print(f"particulas        : {st.get('n_particles_embedded')} embutidas no sólido")
    print(f"faces (m2 total)  : {len(f)}")
    print(f"\ngerado em: {out_dir}")
    print("  - m2_leito.stl       (malha m2 real; corte/clip para ver as partículas)")
    print("  - m2_validacao.obj   (núcleo TRANSLÚCIDO + partículas SÓLIDAS = ver direto)")


if __name__ == "__main__":
    main()
