# validacao real no blender dos modos de cilindro interno (m2/m3)
# executar:
#   blender --background --python scripts/blender_scripts/validate_internal_modes_blender.py
#
# verifica, em cena real do blender:
#  - m2 (interior solido visivel + particulas) usa parede ANELAR + nucleo solido
#  - m3 (queijo) fura o nucleo solido com as particulas
#  - o nucleo ocupa apenas o vao entre as tampas (sem sobrepor as tampas)
#  - a parede e anelar (raio externo) e o nucleo r_int (sem sobreposicao de volume)
from __future__ import annotations

import sys
from pathlib import Path

import bpy
from mathutils import Vector

_SCRIPT_DIR = Path(__file__).resolve().parent
_PM = _SCRIPT_DIR.parent / "python_modeling"
for p in (str(_SCRIPT_DIR), str(_PM)):
    if p not in sys.path:
        sys.path.insert(0, p)

from packed_bed_science.blender_build import (  # noqa: E402
    create_bed_by_internal_mode,
    create_caps,
    punch_core_with_particle_tools,
)

R_EXT = 0.025
R_INT = 0.020
H = 0.06
TB = 0.004
TT = 0.004
D_PART = 0.008
CENTERS = [(0.0, 0.0, 0.02), (0.008, 0.0, 0.03), (-0.008, 0.0, 0.045), (0.0, 0.008, 0.04)]

# faces internas das tampas (create_caps centra em z=0 e z=H): [TB/2, H-TT/2]
CAP_BOTTOM_INNER = TB / 2.0
CAP_TOP_INNER = H - TT / 2.0
EPS = 1e-5


def _clear() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def _bounds(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def _check(label, cond):
    print(f"    [{'OK ' if cond else 'FALHA'}] {label}")
    return cond


def run_mode(mode: str) -> bool:
    _clear()
    vis = {"show_outer_cylinder": True, "show_internal_cylinder": True, "show_particles": True}
    leito, nucleo, status = create_bed_by_internal_mode(
        mode, R_EXT, R_INT, H, vis, bottom_cap=TB, top_cap=TT
    )
    create_caps(H, R_EXT * 2.0, TB, TT)
    n_holes = 0
    if mode == "solid_internal_cylinder_with_particle_holes" and nucleo is not None:
        _stat, _w, n_holes = punch_core_with_particle_tools(
            nucleo, CENTERS, D_PART, "sphere"
        )

    print(f"\n=== modo: {mode} ===")
    print(f"  status build: {status}  furos={n_holes}")
    print("  objetos na cena:")
    core_obj = None
    wall_obj = None
    for o in sorted(bpy.data.objects, key=lambda x: x.name):
        if o.type != "MESH":
            continue
        x0, x1, y0, y1, z0, z1 = _bounds(o)
        print(
            f"    {o.name:24s} x[{x0:+.3f},{x1:+.3f}] "
            f"y[{y0:+.3f},{y1:+.3f}] z[{z0:+.4f},{z1:+.4f}]"
        )
        nm = o.name.lower()
        if "nucleo" in nm or "cilindro_interno" in nm:
            core_obj = o
        elif "leito" in nm or "extracao" in nm:
            wall_obj = o

    ok = True
    if core_obj is None:
        ok &= _check("nucleo solido presente na cena", False)
        return ok
    _, _, _, _, cz0, cz1 = _bounds(core_obj)
    _, cxr1, _, _, _, _ = _bounds(core_obj)
    ok &= _check(
        f"nucleo NAO invade a tampa inferior (z0={cz0:.4f} >= {CAP_BOTTOM_INNER:.4f})",
        cz0 >= CAP_BOTTOM_INNER - EPS,
    )
    ok &= _check(
        f"nucleo NAO invade a tampa superior (z1={cz1:.4f} <= {CAP_TOP_INNER:.4f})",
        cz1 <= CAP_TOP_INNER + EPS,
    )
    # raio do nucleo ~ r_int (sem sobrepor a parede anelar r_int..r_ext)
    ok &= _check(
        f"nucleo com raio ~ r_int ({cxr1:.4f} ~ {R_INT:.4f}, < r_ext {R_EXT:.4f})",
        abs(cxr1 - R_INT) < 1e-3,
    )
    if wall_obj is not None:
        wx0, wx1, _, _, _, _ = _bounds(wall_obj)
        ok &= _check(
            f"parede e anelar ate r_ext (x_max={wx1:.4f} ~ {R_EXT:.4f})",
            abs(wx1 - R_EXT) < 1e-3,
        )
    if mode == "solid_internal_cylinder_with_particle_holes":
        ok &= _check(f"furos aplicados no nucleo ({n_holes}/{len(CENTERS)})", n_holes == len(CENTERS))
    return ok


def main() -> None:
    all_ok = True
    for mode in (
        "internal_cylinder_visible_no_boolean",
        "solid_internal_cylinder_with_particle_holes",
    ):
        all_ok &= run_mode(mode)
    print("\n" + ("BEDFLOW_INTERNAL_MODES_OK" if all_ok else "BEDFLOW_INTERNAL_MODES_FAIL"))


if __name__ == "__main__":
    main()
