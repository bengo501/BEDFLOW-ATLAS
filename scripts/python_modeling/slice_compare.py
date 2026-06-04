#!/usr/bin/env python3
"""
saídas de comparação/validação do corte 2d (pseudo_2d_thin_slice).

ao gerar uma fatia 2d, é útil ter também o modelo 3d completo (antes do corte)
para validar se o corte foi bem executado. este módulo monta, a partir das duas
malhas (2d e 3d), os arquivos de comparação:

  - "lado a lado" (combined): a fatia 2d e o leito 3d deslocados no eixo x, num
    único arquivo, para olhar os dois juntos;
  - "sobreposto" (overlay): a fatia 2d na MESMA posição em que foi cortada,
    dentro do leito 3d (translúcido), para validar a posição/forma do corte.

formatos:
  - .obj (+ .mtl): dois objetos nomeados e coloridos (bed_3d translúcido,
    slice_2d sólido) — ideal para inspeção (Blender/ParaView/three.js);
  - .stl: malha única (fallback universal); no overlay as malhas se sobrepõem
    (use um plano de corte para ver a fatia dentro do leito).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from stl_mesh_utils import merge_mesh, tri, vec3, write_stl_binary

# modos de saída de comparação
COMPARE_OFF = "off"
COMPARE_SEPARATE = "separate"
COMPARE_COMBINED = "combined"
COMPARE_OVERLAY = "overlay"
COMPARE_ALL = "all"
VALID_COMPARE_MODES = (
    COMPARE_OFF,
    COMPARE_SEPARATE,
    COMPARE_COMBINED,
    COMPARE_OVERLAY,
    COMPARE_ALL,
)


def normalize_compare_mode(raw: Any, default: str = COMPARE_SEPARATE) -> str:
    """normaliza o modo de comparação (aceita aliases em pt/en)."""
    s = str(raw or default).strip().lower().replace("-", "_").replace(" ", "_")
    if s in VALID_COMPARE_MODES:
        return s
    aliases = {
        "none": COMPARE_OFF,
        "nao": COMPARE_OFF,
        "no": COMPARE_OFF,
        "so_2d": COMPARE_OFF,
        "apenas_2d": COMPARE_OFF,
        "separado": COMPARE_SEPARATE,
        "separados": COMPARE_SEPARATE,
        "dois": COMPARE_SEPARATE,
        "ambos": COMPARE_SEPARATE,
        "side_by_side": COMPARE_COMBINED,
        "lado_a_lado": COMPARE_COMBINED,
        "juntos": COMPARE_COMBINED,
        "combinado": COMPARE_COMBINED,
        "nested": COMPARE_OVERLAY,
        "sobreposto": COMPARE_OVERLAY,
        "dentro": COMPARE_OVERLAY,
        "2d_in_3d": COMPARE_OVERLAY,
        "todos": COMPARE_ALL,
        "tudo": COMPARE_ALL,
    }
    return aliases.get(s, default)


def _bbox(verts: List[vec3]) -> Tuple[vec3, vec3]:
    xs = [p[0] for p in verts]
    ys = [p[1] for p in verts]
    zs = [p[2] for p in verts]
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def _translate(verts: List[vec3], dx: float, dy: float, dz: float) -> List[vec3]:
    return [(p[0] + dx, p[1] + dy, p[2] + dz) for p in verts]


def _side_by_side_offset(
    v2d: List[vec3], v3d: List[vec3], axis: str = "x", gap_factor: float = 0.25
) -> Tuple[float, float, float]:
    """deslocamento para por o 3d ao lado do 2d sem sobrepor (no eixo dado)."""
    lo2, hi2 = _bbox(v2d)
    lo3, hi3 = _bbox(v3d)
    ai = {"x": 0, "y": 1, "z": 2}.get(axis, 0)
    span2 = hi2[ai] - lo2[ai]
    span3 = hi3[ai] - lo3[ai]
    gap = max(span2, span3) * gap_factor + 1e-4
    # encostar o min do 3d logo após o max do 2d (+ gap)
    shift = (hi2[ai] - lo3[ai]) + gap
    d = [0.0, 0.0, 0.0]
    d[ai] = shift
    return d[0], d[1], d[2]


def write_obj_multi(
    path: Path,
    objects: List[Tuple[str, List[vec3], List[tri], str]],
    *,
    mtl_path: Optional[Path] = None,
    materials: Optional[Dict[str, Dict[str, Any]]] = None,
) -> None:
    """grava um .obj com múltiplos objetos nomeados (faces 1-based globais).

    objects: lista de (nome_objeto, vertices, faces, nome_material).
    materials: {nome_material: {"Kd": (r,g,b), "d": alpha}} -> grava o .mtl.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    if mtl_path is not None and materials:
        lines.append(f"mtllib {Path(mtl_path).name}")
    offset = 0  # vértices já escritos (faces são 1-based e globais no .obj)
    for name, verts, faces, mat in objects:
        lines.append(f"o {name}")
        if materials and mat in (materials or {}):
            lines.append(f"usemtl {mat}")
        for x, y, z in verts:
            lines.append(f"v {x:.6f} {y:.6f} {z:.6f}")
        for a, b, c in faces:
            lines.append(f"f {a + 1 + offset} {b + 1 + offset} {c + 1 + offset}")
        offset += len(verts)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if mtl_path is not None and materials:
        mlines: List[str] = []
        for mat, props in materials.items():
            mlines.append(f"newmtl {mat}")
            kd = props.get("Kd", (0.8, 0.8, 0.8))
            mlines.append(f"Kd {kd[0]:.3f} {kd[1]:.3f} {kd[2]:.3f}")
            mlines.append("Ka 0.000 0.000 0.000")
            d = float(props.get("d", 1.0))
            mlines.append(f"d {d:.3f}")          # opacidade (1=opaco)
            mlines.append(f"Tr {1.0 - d:.3f}")   # transparência (alguns leitores)
            mlines.append("illum 2")
        Path(mtl_path).write_text("\n".join(mlines) + "\n", encoding="utf-8")


# materiais padrão para os arquivos de comparação
_MAT_BED = "bed_3d"
_MAT_SLICE = "slice_2d"
_MATERIALS_OVERLAY = {
    _MAT_BED: {"Kd": (0.74, 0.78, 0.83), "d": 0.22},    # leito 3d translúcido
    _MAT_SLICE: {"Kd": (0.92, 0.27, 0.10), "d": 1.0},   # fatia 2d sólida (laranja)
}
_MATERIALS_COMBINED = {
    _MAT_BED: {"Kd": (0.74, 0.78, 0.83), "d": 1.0},     # ambos sólidos (lado a lado)
    _MAT_SLICE: {"Kd": (0.92, 0.27, 0.10), "d": 1.0},
}


def export_slice_comparison(
    out_stl: Path,
    mesh_2d: Tuple[List[vec3], List[tri]],
    mesh_3d: Tuple[List[vec3], List[tri]],
    *,
    compare_mode: str,
    side_by_side_axis: str = "x",
) -> List[str]:
    """gera os arquivos de comparação pedidos ao lado de out_stl.

    devolve os nomes (relativos) dos arquivos gerados.
    """
    mode = normalize_compare_mode(compare_mode)
    if mode in (COMPARE_OFF, COMPARE_SEPARATE):
        return []  # nada extra (o _full3d separado é tratado no pipeline)

    v2d, f2d = mesh_2d
    v3d, f3d = mesh_3d
    if not v2d or not v3d:
        return []

    out_stl = Path(out_stl)
    stem = out_stl.stem
    parent = out_stl.parent
    parent.mkdir(parents=True, exist_ok=True)
    generated: List[str] = []

    want_combined = mode in (COMPARE_COMBINED, COMPARE_ALL)
    want_overlay = mode in (COMPARE_OVERLAY, COMPARE_ALL)

    if want_combined:
        dx, dy, dz = _side_by_side_offset(v2d, v3d, axis=side_by_side_axis)
        v3d_sbs = _translate(v3d, dx, dy, dz)
        # .obj (dois objetos coloridos) + .mtl
        obj = parent / f"{stem}_compare.obj"
        mtl = parent / f"{stem}_compare.mtl"
        write_obj_multi(
            obj,
            [
                (_MAT_SLICE, v2d, f2d, _MAT_SLICE),
                (_MAT_BED, v3d_sbs, f3d, _MAT_BED),
            ],
            mtl_path=mtl,
            materials=_MATERIALS_COMBINED,
        )
        generated += [obj.name, mtl.name]
        # .stl (malha única lado a lado)
        vm, fm = merge_mesh(list(v2d), list(f2d), v3d_sbs, f3d)
        stl = parent / f"{stem}_compare.stl"
        write_stl_binary(stl, vm, fm)
        generated.append(stl.name)

    if want_overlay:
        # 2d na MESMA posição, dentro do 3d (translúcido)
        obj = parent / f"{stem}_overlay.obj"
        mtl = parent / f"{stem}_overlay.mtl"
        write_obj_multi(
            obj,
            [
                (_MAT_BED, v3d, f3d, _MAT_BED),
                (_MAT_SLICE, v2d, f2d, _MAT_SLICE),
            ],
            mtl_path=mtl,
            materials=_MATERIALS_OVERLAY,
        )
        generated += [obj.name, mtl.name]
        # .stl (sobreposto; use plano de corte para ver a fatia dentro do leito)
        vm, fm = merge_mesh(list(v3d), list(f3d), list(v2d), list(f2d))
        stl = parent / f"{stem}_overlay.stl"
        write_stl_binary(stl, vm, fm)
        generated.append(stl.name)

    return generated


__all__ = [
    "COMPARE_OFF",
    "COMPARE_SEPARATE",
    "COMPARE_COMBINED",
    "COMPARE_OVERLAY",
    "COMPARE_ALL",
    "VALID_COMPARE_MODES",
    "normalize_compare_mode",
    "export_slice_comparison",
    "write_obj_multi",
]
