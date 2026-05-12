# modelagem geometrica do leito em python puro
# vertices e faces triangulares sem blender
# este modulo monta cilindro oco tampas e esferas numa unica malha
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from stl_mesh_utils import (
    box_mesh,
    cylinder_axis,
    merge_mesh,
    tri,
    vec3,
    uv_sphere,
    write_stl_binary,
)

__all__ = [
    "MeshData",
    "PackedBedModel",
    "create_hollow_cylinder_geometry",
    "create_cap_geometry",
    "build_packed_bed_model",
    "export_model_data",
]


@dataclass
class MeshData:
    # meshdata guarda uma malha triangular simples
    # vertices lista de pontos xyz em metros
    # faces lista de triplos de indices inteiros
    vertices: List[vec3] = field(default_factory=list)
    faces: List[tri] = field(default_factory=list)


@dataclass
class PackedBedModel:
    # packedbedmodel agrupa malha final e metadados opcionais
    # mesh e a geometria completa
    # meta e um dicionario livre para numeros e texto de resumo
    mesh: MeshData
    meta: Dict[str, Any] = field(default_factory=dict)


def create_hollow_cylinder_geometry(
    r_ext: float,
    r_int: float,
    height: float,
    segmentos: int = 48,
) -> MeshData:
    # funcao create_hollow_cylinder_geometry
    # constroi um tubo oco vertical com eixo z
    # r_ext raio externo em metros
    # r_int raio interno em metros
    # height altura total do tubo ao longo de z
    # segmentos numero de lados do poligono aproximando o circulo
    # layout mental dos indices
    # bloco zero a n menos um e anel exterior em z igual zero
    # bloco n a dois n menos um e anel exterior em z igual height
    # bloco dois n a tres n menos um e anel interior em z igual zero
    # bloco tres n a quatro n menos um e anel interior em z igual height
    # se dados absurdos devolve malha vazia sem crash
    if r_int >= r_ext or height <= 0 or segmentos < 3:
        return MeshData()
    # n copia local do numero de segmentos para ler codigo mais curto
    n = segmentos
    verts: List[vec3] = []
    faces: List[tri] = []

    # anel exterior base z zero
    for i in range(n):
        a = 2 * math.pi * i / n
        c = math.cos(a)
        s = math.sin(a)
        verts.append((r_ext * c, r_ext * s, 0.0))
    # anel exterior topo z height
    for i in range(n):
        a = 2 * math.pi * i / n
        c = math.cos(a)
        s = math.sin(a)
        verts.append((r_ext * c, r_ext * s, height))
    # anel interior base z zero
    for i in range(n):
        a = 2 * math.pi * i / n
        c = math.cos(a)
        s = math.sin(a)
        verts.append((r_int * c, r_int * s, 0.0))
    # anel interior topo z height
    for i in range(n):
        a = 2 * math.pi * i / n
        c = math.cos(a)
        s = math.sin(a)
        verts.append((r_int * c, r_int * s, height))

    # ni devolve o vizinho seguinte no anel com wrap no fim
    def ni(i: int) -> int:
        return (i + 1) % n

    # superficie externa dois triangulos por quadrilatero entre aneis
    # normais apontam para fora do solido
    for i in range(n):
        j = ni(i)
        faces.append((i, n + j, n + i))
        faces.append((i, j, n + j))
    # superficie interna ordem dos vertices invertida para normais para dentro do buraco
    for i in range(n):
        j = ni(i)
        ib = 2 * n + i
        it = 3 * n + i
        jb = 2 * n + j
        jt = 3 * n + j
        faces.append((ib, it, jt))
        faces.append((ib, jt, jb))
    # anel inferior fecha o disco entre raio interno e externo em z zero
    for i in range(n):
        j = ni(i)
        faces.append((i, 2 * n + j, 2 * n + i))
        faces.append((i, j, 2 * n + j))
    # anel superior fecha o disco em z height
    for i in range(n):
        j = ni(i)
        oi = n + i
        oj = n + j
        ii = 3 * n + i
        ij = 3 * n + j
        faces.append((oi, ii, ij))
        faces.append((oi, ij, oj))

    return MeshData(vertices=verts, faces=faces)


def create_cap_geometry(
    outer_radius: float,
    thickness: float,
    z_center: float,
    segmentos: int = 48,
) -> MeshData:
    # funcao create_cap_geometry
    # tampa modelada como cilindro curto com dois discos nas bases
    # outer_radius raio externo da tampa igual ao tubo
    # thickness espessura ao longo de z
    # z_center centro geometrico da tampa no eixo z
    # segmentos poligonizacao do circulo
    # se dados invalidos devolve malha vazia
    if outer_radius <= 0 or thickness <= 0 or segmentos < 3:
        return MeshData()
    # z0 face inferior da tampa
    z0 = z_center - thickness / 2.0
    # z1 face superior da tampa
    z1 = z_center + thickness / 2.0
    n = segmentos
    verts: List[vec3] = []
    faces: List[tri] = []
    # vertice zero centro do disco inferior
    verts.append((0.0, 0.0, z0))
    # vertice um centro do disco superior
    verts.append((0.0, 0.0, z1))
    # base_ring e o indice onde comeca o primeiro anel no disco inferior
    base_ring = 2
    # anel no plano z0
    for i in range(n):
        a = 2 * math.pi * i / n
        c = math.cos(a)
        s = math.sin(a)
        verts.append((outer_radius * c, outer_radius * s, z0))
    # anel no plano z1
    for i in range(n):
        a = 2 * math.pi * i / n
        c = math.cos(a)
        s = math.sin(a)
        verts.append((outer_radius * c, outer_radius * s, z1))

    def ni(i: int) -> int:
        return (i + 1) % n

    # cb ct indices dos centros inferior e superior
    cb = 0
    ct = 1
    # funcoes auxiliares mapeiam indice angular para indice de vertice
    rb0 = lambda i: base_ring + i
    rt0 = lambda i: base_ring + n + i
    # triangulos do disco inferior em leque a partir do centro
    for i in range(n):
        j = ni(i)
        faces.append((cb, rb0(j), rb0(i)))
    # triangulos do disco superior em leque a partir do centro
    for i in range(n):
        j = ni(i)
        faces.append((ct, rt0(i), rt0(j)))
    # superficie lateral da tampa dois triangulos por faixa
    for i in range(n):
        j = ni(i)
        faces.append((rb0(i), rb0(j), rt0(j)))
        faces.append((rb0(i), rt0(j), rt0(i)))

    return MeshData(vertices=verts, faces=faces)


def meshdata_to_lists(m: MeshData) -> Tuple[List[vec3], List[tri]]:
    # copia dataclass para listas mutaveis para usar merge_mesh
    return list(m.vertices), list(m.faces)


def _append_particle_mesh(
    vx: List[vec3],
    fx: List[tri],
    cx: float,
    cy: float,
    cz: float,
    particle_diameter: float,
    particle_kind: str,
    lat_sphere: int,
    lon_sphere: int,
) -> Tuple[List[vec3], List[tri]]:
    pk = (particle_kind or "sphere").strip().lower()
    d = float(particle_diameter)
    if pk == "cube":
        sv, sf = box_mesh(cx, cy, cz, d)
    elif pk == "cylinder":
        sv, sf = cylinder_axis(cx, cy, cz, d * 0.5, d, axis="z", segments=20)
    else:
        sv, sf = uv_sphere(cx, cy, cz, d * 0.5, lat=lat_sphere, lon=lon_sphere)
    return merge_mesh(vx, fx, sv, sf)


def build_packed_bed_model(
    r_ext: float,
    r_int: float,
    height: float,
    bottom_cap_thickness: float,
    top_cap_thickness: float,
    particle_centers: List[vec3],
    particle_diameter: float,
    particle_kind: str = "sphere",
    segmentos_cil: int = 48,
    lat_sphere: int = 4,
    lon_sphere: int = 6,
) -> PackedBedModel:
    # funcao build_packed_bed_model
    # passo um gera corpo cilindrico oco
    body = create_hollow_cylinder_geometry(
        r_ext, r_int, height, segmentos=segmentos_cil
    )
    # v f acumulam vertices e faces ao longo de todas as partes
    v, f = meshdata_to_lists(body)
    # z_inf centro da tampa inferior metade da espessura acima de z zero
    z_inf = bottom_cap_thickness / 2.0
    # z_sup centro da tampa superior metade da espessura abaixo do topo
    z_sup = height - top_cap_thickness / 2.0
    # cap_i tampa de baixo
    cap_i = create_cap_geometry(r_ext, bottom_cap_thickness, z_inf, segmentos_cil)
    # cap_s tampa de cima
    cap_s = create_cap_geometry(r_ext, top_cap_thickness, z_sup, segmentos_cil)
    # merge das tampas sobre o tubo
    v, f = merge_mesh(v, f, cap_i.vertices, cap_i.faces)
    v, f = merge_mesh(v, f, cap_s.vertices, cap_s.faces)
    pk = (particle_kind or "sphere").strip().lower()
    for c in particle_centers:
        sx, sy, sz = c
        v, f = _append_particle_mesh(
            v, f, sx, sy, sz, particle_diameter, pk, lat_sphere, lon_sphere
        )
    meta = {
        "n_particles": len(particle_centers),
        "particle_kind": pk,
        "r_ext": r_ext,
        "r_int": r_int,
        "height": height,
    }
    return PackedBedModel(mesh=MeshData(vertices=v, faces=f), meta=meta)


def export_model_data(
    packed: PackedBedModel,
    out_stl: Path,
    out_json: Optional[Path] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    # funcao export_model_data
    # packed modelo completo com mesh e meta
    # out_stl caminho do stl binario
    # out_json caminho opcional para json com metadados
    # extra dicionario opcional fundido em cima de meta
    # sempre escreve stl primeiro
    write_stl_binary(out_stl, packed.mesh.vertices, packed.mesh.faces)
    # se pedido json junta meta extra e grava utf8 indentado
    if out_json is not None:
        data = dict(packed.meta)
        if extra:
            data.update(extra)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        with out_json.open("w", encoding="utf-8") as fp:
            json.dump(data, fp, indent=2, ensure_ascii=False)
