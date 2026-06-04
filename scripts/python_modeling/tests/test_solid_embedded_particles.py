"""
prova de que o modo m2 (internal_cylinder_visible_no_boolean) mantém as
partículas FIXAS e DISTINTAS dentro do cilindro sólido.

contexto: a versão antiga usava união booleana (fuse) núcleo + partículas. quando
as partículas estão totalmente dentro do núcleo (caso real do empacotamento), a
união as ABSORVE e o resultado é um cilindro maciço liso (partículas somem). o
modo correto mantém as partículas como geometria distinta embutida (paridade com
o backend blender, que as cria como objetos separados).

estes testes verificam:
  - embedded (padrão): a geometria das partículas está presente no resultado;
  - fuse (opt-in bed.solid_particles_fuse): núcleo + partículas num sólido único;
  - o núcleo não invade as tampas (vão interno) — sem sobreposição.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

_PM = Path(__file__).resolve().parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from bed_internal_modes import MODE_VISIBLE_INNER  # noqa: E402
from bed_shell_build import build_bed_with_internal_mode  # noqa: E402

R_EXT, R_INT, H, TB, TT = 0.025, 0.020, 0.06, 0.004, 0.004
D_PART = 0.008
# partículas TOTALMENTE dentro do núcleo (centro a raio < r_int - r_part)
CENTERS = [(0.006, 0.0, 0.02), (-0.006, 0.0, 0.03), (0.0, 0.006, 0.045), (0.005, -0.005, 0.05)]


def _build(extra_bed=None):
    bed = {
        "internal_cylinder_mode": MODE_VISIBLE_INNER,
        "visibility": {"show_internal_cylinder": True, "show_particles": True},
    }
    bed.update(extra_bed or {})
    return build_bed_with_internal_mode(
        {"bed": bed}, R_EXT, R_INT, H, TB, TT, CENTERS, D_PART, "sphere", segmentos=24
    )


def test_m2_embedded_status():
    _v, _f, meta = _build()
    st = meta["boolean_operation_status"]
    assert st["inner_core"] == "solid_with_embedded_particles"
    assert st["particle_tools"] == "embedded"
    assert st["n_particles_embedded"] == len(CENTERS)


def test_m2_embedded_keeps_particle_geometry():
    """cada partícula (mesmo totalmente interna) deixa geometria de esfera no resultado."""
    v, _f, _meta = _build()
    r = D_PART / 2.0
    for c in CENTERS:
        near = [p for p in v if math.dist((p[0], p[1], p[2]), c) <= r * 1.4]
        assert len(near) >= 4, f"sem geometria de particula perto de {c} (achou {len(near)})"


def test_m2_embedded_more_faces_than_fused():
    """embedded mantém as faces das partículas; fuse as absorve (menos faces)."""
    _ve, fe, _me = _build()
    _vf, ff, mf = _build({"solid_particles_fuse": True})
    assert mf["boolean_operation_status"]["inner_core"] == "fused_with_particles"
    assert len(fe) > len(ff), "embedded deveria ter mais faces (geometria das particulas)"


def test_m2_core_does_not_invade_caps():
    """o núcleo sólido fica no vão entre as tampas: z in [TB, H-TT]."""
    v, _f, _meta = _build()
    # o objeto além da parede/tampas inclui o núcleo; verifica que nenhum vértice do
    # núcleo/partículas passa das faces internas das tampas (com folga do raio da partícula)
    r = D_PART / 2.0
    zs = [p[2] for p in v]
    # parede/tampas vão de 0..H; o núcleo+particulas devem caber em [TB-? , H-TT+?]
    # (as partículas podem chegar perto das tampas, mas o NÚCLEO não invade)
    assert min(zs) >= 0.0 - 1e-9 and max(zs) <= H + 1e-9
    # checagem direta do núcleo isolado
    from bed_shell_build import _solid_cylinder_mesh, _interior_span

    z0, z1 = _interior_span(H, TB, TT)
    cv, _cf = _solid_cylinder_mesh(R_INT, H, 24, z_bottom=z0, z_top=z1)
    czs = [p[2] for p in cv]
    assert min(czs) >= TB - 1e-9, "núcleo invade a tampa inferior"
    assert max(czs) <= H - TT + 1e-9, "núcleo invade a tampa superior"
