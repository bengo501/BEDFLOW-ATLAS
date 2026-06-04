"""
prova de que o assentamento do DEM (motor python, packing_method=rigid_body/dem)
produz empacotamentos GEOMETRICAMENTE VÁLIDOS após a resolução de contatos.

contexto: o DEM usa contato mola-amortecedor (soft), que deixa micro-sobreposições
residuais; a validação estrita (distância >= r_i+r_j+gap) acusava esses contatos.
a etapa de resolução de contatos (relaxação posição) separa as sobreposições e
reaplica as paredes, tornando o resultado válido.
"""
from __future__ import annotations

import sys
from pathlib import Path

_PM = Path(__file__).resolve().parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from engine.dem_solver import run_dem_packing  # noqa: E402
from engine.domain import PackedBedDomain  # noqa: E402
from packed_bed_science.validation import validate_configuration  # noqa: E402

_DOMAIN = PackedBedDomain(
    r_int=0.022, r_ext=0.025, height=0.05, bottom_cap_thickness=0.003,
    top_cap_thickness=0.003, gap=0.0005, particle_diameter=0.008, particle_kind="sphere",
)
_N = 14
_STEPS = 2500


def _pack(resolve: bool):
    centers, meta = run_dem_packing(
        _DOMAIN, _N,
        {"seed": 3, "dem": {"steps": _STEPS, "resolve_contacts": resolve}},
    )
    radii = [0.004] * len(centers)
    report = validate_configuration(centers, radii, _DOMAIN.annulus, _DOMAIN.gap)
    return centers, meta, report


def test_dem_with_resolution_is_valid():
    """com a resolução de contatos (padrão), o empacotamento passa na validação."""
    _centers, meta, report = _pack(resolve=True)
    cr = meta.get("contact_resolution", {})
    assert cr.get("converged") is True, f"contato não convergiu: {cr}"
    assert cr.get("max_overlap_after", 1.0) < 1e-8
    assert report["ok"] is True, f"validação falhou: {report['messages'][:5]}"
    assert report["pair_violations"] == 0
    assert report["domain_violations"] == 0


def test_dem_without_resolution_has_violations():
    """sem a resolução, os contatos soft do DEM deixam violações (mostra o efeito)."""
    _centers, _meta, report = _pack(resolve=False)
    assert report["pair_violations"] > 0 or report["domain_violations"] > 0


def test_resolution_reduces_overlap():
    """a resolução reduz drasticamente a sobreposição máxima."""
    _c, meta, _r = _pack(resolve=True)
    cr = meta["contact_resolution"]
    assert cr["max_overlap_before"] > cr["max_overlap_after"]
    assert cr["max_overlap_after"] < 1e-8
