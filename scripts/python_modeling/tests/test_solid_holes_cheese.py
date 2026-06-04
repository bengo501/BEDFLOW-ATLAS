"""
prova de que o modo m3 (queijo) realmente fura o cilindro maciço.

o modo solid_internal_cylinder_with_particle_holes deve subtrair a malha de cada
partícula do núcleo maciço, criando cavidades internas (queijo suíço). este teste
constrói um núcleo + furos com a MESMA função do pipeline real
(bed_shell_build.punch_holes_in_solid) e verifica evidências independentes:

  1. status 'applied' e nº de furos == nº de partículas;
  2. malha perfurada continua estanque (watertight) e válida;
  3. volume diminuiu (material foi removido) ~ volume das esferas;
  4. PROVA TOPOLÓGICA: euler = 2*(1+N) e N cavidades internas isoladas
     (cilindro maciço tem euler=2 e 0 cavidades);
  5. PROVA CAUSAL: cada cavidade fica exatamente na posição de uma partícula.

requer um backend booleano (manifold3d); sem ele o teste é pulado.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

_PM = Path(__file__).resolve().parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

pytest.importorskip("trimesh", reason="trimesh necessário para o teste do queijo")

from bed_shell_build import _pick_boolean_engine  # noqa: E402
from cheese_demo import build_cheese  # noqa: E402

_HAS_ENGINE = _pick_boolean_engine() is not None
pytestmark = pytest.mark.skipif(
    not _HAS_ENGINE,
    reason="sem backend booleano (instale manifold3d: pip install manifold3d)",
)


@pytest.fixture(scope="module")
def cheese():
    # furos garantidamente internos e isolados -> cada um vira uma cavidade
    solid_tm, perf_tm, centers, res = build_cheese(
        r_cyl=0.02, height=0.06, bottom_cap=0.004, top_cap=0.004,
        hole_diameter=0.006, segments=64,
    )
    return solid_tm, perf_tm, centers, res


def test_furos_aplicados(cheese):
    _, _, centers, res = cheese
    assert res.status == "applied"
    assert res.n_holes_applied == len(centers) > 0


def test_malha_perfurada_valida(cheese):
    _, _, _, res = cheese
    assert res.perforated_watertight, "malha perfurada deveria ser estanque"


def test_material_removido(cheese):
    _, _, _, res = cheese
    # volume diminuiu (buracos retiram material)
    assert res.removed_volume > 0
    assert res.perforated_volume < res.solid_volume
    # material removido ~ volume das esferas (icosfera subdiv=1 ~ 87% da esfera ideal)
    ratio = res.removed_volume / res.expected_sphere_volume
    assert 0.6 < ratio < 1.1, f"razao volume removido/esferas fora do esperado: {ratio:.3f}"


def test_prova_topologica_cavidades(cheese):
    """cilindro maciço: euler=2, 0 cavidades. perfurado com N furos internos
    isolados: euler=2*(1+N) e N cavidades (cada esfera vira uma casca fechada)."""
    _, _, centers, res = cheese
    n = len(centers)
    assert res.solid_euler == 2, "cilindro maciço deveria ter euler 2 (genus 0, sem cavidades)"
    assert res.n_cavities == n, f"esperado {n} cavidades, obtido {res.n_cavities}"
    assert res.perforated_euler == 2 * (1 + n), (
        f"euler perfurado {res.perforated_euler} != 2*(1+{n})={2 * (1 + n)} "
        "— furos internos não criaram N cavidades"
    )
    # cascas = 1 corpo externo + N cavidades
    assert res.n_shells == n + 1


def test_prova_causal_cavidade_na_particula(cheese):
    """cada cavidade está na posição de uma partícula (o furo é onde a partícula estava)."""
    _, _, centers, res = cheese
    tol = 0.006 * 0.5  # raio do furo
    for c in centers:
        d = min(
            math.dist(c, cav) for cav in res.cavity_centroids
        )
        assert d < tol, f"nenhuma cavidade perto da partícula {c} (dist min={d:.4f} m)"
    # correspondência 1-para-1
    assert len(res.cavity_centroids) == len(centers)


def test_gera_modelo(tmp_path):
    """executar a demo gera os .stl maciço e perfurado + relatório."""
    from cheese_demo import generate_cheese_demo

    res = generate_cheese_demo(tmp_path)
    assert (tmp_path / "cheese_solido.stl").stat().st_size > 80
    assert (tmp_path / "cheese_perfurado.stl").stat().st_size > 80
    assert (tmp_path / "cheese_report.json").is_file()
    # o perfurado tem mais geometria (superfícies dos furos) que o maciço
    assert (tmp_path / "cheese_perfurado.stl").stat().st_size > (
        tmp_path / "cheese_solido.stl"
    ).stat().st_size
    assert res.n_cavities == res.n_holes_applied
