#!/usr/bin/env python3
"""
demonstração + prova do modo "queijo" (m3: solid_internal_cylinder_with_particle_holes).

o modo m3 subtrai a malha de cada partícula de um cilindro maciço (boolean
difference), deixando cavidades internas — como um queijo suíço. este módulo:

  1. constrói um cilindro maciço (núcleo);
  2. fura-o nas posições das partículas com a MESMA função do pipeline real
     (bed_shell_build.punch_holes_in_solid);
  3. mede evidências geométricas/topológicas que PROVAM que os furos existem;
  4. exporta os modelos (.stl) maciço e perfurado para inspeção visual.

uso (gera os modelos em generated/3d/cheese_demo/):
    python scripts/python_modeling/cheese_demo.py
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_PM = Path(__file__).resolve().parent
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from bed_shell_build import (  # noqa: E402
    _as_trimesh_volume,
    _pick_boolean_engine,
    _solid_cylinder_mesh,
    punch_holes_in_solid,
)
from stl_mesh_utils import write_stl_binary  # noqa: E402

vec3 = Tuple[float, float, float]


def grid_internal_holes(
    r_cyl: float,
    z0: float,
    z1: float,
    hole_diameter: float,
    *,
    margin: float = 0.002,
) -> List[vec3]:
    """gera centros de furos garantidamente INTERNOS (cada esfera cabe no núcleo
    sem tocar a parede lateral nem as faces), bem separados -> cavidades isoladas."""
    r = hole_diameter / 2.0
    rho_max = r_cyl - r - margin            # raio radial máximo do centro
    zc0 = z0 + r + margin
    zc1 = z1 - r - margin
    centers: List[vec3] = []
    # coluna central + um anel de 4, em duas alturas -> furos espalhados e isolados
    zs = [zc0 + (zc1 - zc0) * t for t in (0.18, 0.5, 0.82)]
    for k, z in enumerate(zs):
        centers.append((0.0, 0.0, z))       # eixo
        if rho_max > 0:
            rho = min(rho_max, r_cyl * 0.5)
            # alterna o ângulo por camada para não alinhar verticalmente
            base = math.pi / 4.0 * (k % 2)
            for a in range(4):
                ang = base + a * math.pi / 2.0
                centers.append((rho * math.cos(ang), rho * math.sin(ang), z))
    return centers


@dataclass
class CheeseResult:
    n_holes_requested: int
    n_holes_applied: int
    status: str
    solid_volume: float
    perforated_volume: float
    removed_volume: float
    expected_sphere_volume: float
    solid_euler: int
    perforated_euler: int
    perforated_watertight: bool
    n_shells: int            # cascas = 1 corpo externo + N cavidades
    n_cavities: int
    cavity_centroids: List[vec3] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = dict(self.__dict__)
        d["cavity_centroids"] = [list(c) for c in self.cavity_centroids]
        return d


def build_cheese(
    *,
    r_cyl: float = 0.02,
    height: float = 0.06,
    bottom_cap: float = 0.004,
    top_cap: float = 0.004,
    hole_diameter: float = 0.006,
    segments: int = 64,
    centers: Optional[List[vec3]] = None,
) -> Tuple[Any, Any, List[vec3], CheeseResult]:
    """constrói o cilindro maciço e o perfurado; devolve (solid_tm, perf_tm, centros, métricas).

    requer um backend booleano (manifold3d). levanta RuntimeError se ausente.
    """
    try:
        import trimesh  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("trimesh nao instalado") from exc

    engine = _pick_boolean_engine()
    if engine is None:
        raise RuntimeError(
            "sem backend booleano: instale manifold3d (pip install manifold3d)"
        )

    z0 = max(0.0, bottom_cap)
    z1 = height - max(0.0, top_cap)
    if centers is None:
        centers = grid_internal_holes(r_cyl, z0, z1, hole_diameter)

    cv, cf = _solid_cylinder_mesh(r_cyl, height, segments, z_bottom=z0, z_top=z1)
    solid_tm, _ok = _as_trimesh_volume(cv, cf)

    pv, pf, status, warns, n_holes = punch_holes_in_solid(
        cv, cf, centers, "sphere", hole_diameter
    )
    perf_tm = trimesh.Trimesh(vertices=pv, faces=pf, process=True)

    # cascas: corpo externo (maior bbox) + cavidades internas
    shells = perf_tm.split(only_watertight=False)
    if len(shells) <= 1:
        cavities = []
    else:
        def _bbox_vol(m: Any) -> float:
            e = m.bounds[1] - m.bounds[0]
            return float(e[0] * e[1] * e[2])

        ordered = sorted(shells, key=_bbox_vol, reverse=True)
        cavities = ordered[1:]  # tudo exceto o corpo externo
    centroids = [tuple(float(x) for x in s.vertices.mean(axis=0)) for s in cavities]

    r = hole_diameter / 2.0
    res = CheeseResult(
        n_holes_requested=len(centers),
        n_holes_applied=int(n_holes),
        status=status,
        solid_volume=float(solid_tm.volume),
        perforated_volume=float(perf_tm.volume),
        removed_volume=float(solid_tm.volume - perf_tm.volume),
        expected_sphere_volume=len(centers) * (4.0 / 3.0) * math.pi * r ** 3,
        solid_euler=int(solid_tm.euler_number),
        perforated_euler=int(perf_tm.euler_number),
        perforated_watertight=bool(perf_tm.is_watertight),
        n_shells=len(shells),
        n_cavities=len(cavities),
        cavity_centroids=centroids,
        warnings=list(warns),
    )
    return solid_tm, perf_tm, centers, res


def generate_cheese_demo(out_dir: Path) -> CheeseResult:
    """gera os modelos do queijo (.stl maciço e perfurado) + relatório json."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    solid_tm, perf_tm, centers, res = build_cheese()

    # exporta usando o mesmo escritor stl binário do projeto
    write_stl_binary(
        out_dir / "cheese_solido.stl",
        [tuple(map(float, v)) for v in solid_tm.vertices],
        [tuple(map(int, f)) for f in solid_tm.faces],
    )
    write_stl_binary(
        out_dir / "cheese_perfurado.stl",
        [tuple(map(float, v)) for v in perf_tm.vertices],
        [tuple(map(int, f)) for f in perf_tm.faces],
    )
    (out_dir / "cheese_report.json").write_text(
        json.dumps(res.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return res


def main() -> None:
    repo = _PM.parent.parent
    out_dir = repo / "generated" / "3d" / "cheese_demo"
    res = generate_cheese_demo(out_dir)
    print("=" * 64)
    print("  DEMO QUEIJO (m3: solid_internal_cylinder_with_particle_holes)")
    print("=" * 64)
    print(f"furos pedidos/aplicados : {res.n_holes_requested} / {res.n_holes_applied} ({res.status})")
    print(f"volume maciço           : {res.solid_volume:.3e} m^3")
    print(f"volume perfurado        : {res.perforated_volume:.3e} m^3")
    print(f"volume removido         : {res.removed_volume:.3e} m^3 (>0 => material retirado)")
    print(f"euler maciço            : {res.solid_euler} (esperado 2)")
    print(f"euler perfurado         : {res.perforated_euler} (esperado 2*(1+N)={2*(1+res.n_holes_applied)})")
    print(f"cavidades internas      : {res.n_cavities} (esperado N={res.n_holes_applied})")
    print(f"watertight perfurado    : {res.perforated_watertight}")
    print(f"\nmodelos gerados em: {out_dir}")
    print("  - cheese_solido.stl    (cilindro maciço, sem furos)")
    print("  - cheese_perfurado.stl (queijo: maciço com cavidades)")
    print("  - cheese_report.json   (métricas)")


if __name__ == "__main__":
    main()
