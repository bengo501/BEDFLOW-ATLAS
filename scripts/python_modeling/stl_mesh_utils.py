# ficheiro de utilidades geometricas puras
# nao depende de numpy nem trimesh para manter dependencias minimas
# junta malhas e escreve stl binario com normais por triangulo
from __future__ import annotations

import math
import struct
from pathlib import Path
from typing import List, Tuple

# vec3 representa um ponto ou vetor em tres dimensoes em metros
vec3 = Tuple[float, float, float]
# tri e um triangulo como tres indices inteiros na lista global de vertices
tri = Tuple[int, int, int]


def uv_sphere(
    cx: float,
    cy: float,
    cz: float,
    r: float,
    lat: int = 5,
    lon: int = 8,
) -> Tuple[List[vec3], List[tri]]:
    # funcao uv_sphere
    # devolve vertices e faces que aproximam uma esfera por malha tipo globo
    # cx cy cz centro da esfera
    # r raio
    # lat numero de faixas ao longo do meridiano quanto maior mais suave
    # lon numero de fatias em volta do eixo z quanto maior mais suave
    verts: List[vec3] = []
    faces: List[tri] = []
    # passo um percorre da base ao topo th vai de zero a pi radianos
    for j in range(lat + 1):
        th = math.pi * j / lat
        sin_t = math.sin(th)
        cos_t = math.cos(th)
        # passo dois percorre o azimute ph vai de zero a dois pi
        for i in range(lon):
            ph = 2 * math.pi * i / lon
            # conversao de coordenadas esfericas para cartesianas x y z
            x = cx + r * sin_t * math.cos(ph)
            y = cy + r * sin_t * math.sin(ph)
            z = cz + r * cos_t
            verts.append((x, y, z))
    # para cada quadrilatero da grelha criamos dois triangulos
    # indices a b d e b c d cobrem o quadrilatero sem buracos
    for j in range(lat):
        for i in range(lon):
            a = j * lon + i
            b = j * lon + (i + 1) % lon
            c = (j + 1) * lon + (i + 1) % lon
            d = (j + 1) * lon + i
            faces.append((a, b, d))
            faces.append((b, c, d))
    return verts, faces


def box_mesh_anisotropic(
    cx: float,
    cy: float,
    cz: float,
    size_x: float,
    size_y: float,
    size_z: float,
) -> Tuple[List[vec3], List[tri]]:
    """paralelepípedo alinhado aos eixos centrado em (cx,cy,cz)."""
    if size_x <= 0 or size_y <= 0 or size_z <= 0:
        return [], []
    hx, hy, hz = size_x / 2.0, size_y / 2.0, size_z / 2.0
    verts: List[vec3] = [
        (cx - hx, cy - hy, cz - hz),
        (cx + hx, cy - hy, cz - hz),
        (cx + hx, cy + hy, cz - hz),
        (cx - hx, cy + hy, cz - hz),
        (cx - hx, cy - hy, cz + hz),
        (cx + hx, cy - hy, cz + hz),
        (cx + hx, cy + hy, cz + hz),
        (cx - hx, cy + hy, cz + hz),
    ]
    faces: List[tri] = [
        (0, 2, 1),
        (0, 3, 2),
        (4, 5, 6),
        (4, 6, 7),
        (0, 1, 5),
        (0, 5, 4),
        (2, 3, 7),
        (2, 7, 6),
        (0, 4, 7),
        (0, 7, 3),
        (1, 2, 6),
        (1, 6, 5),
    ]
    return verts, faces


def box_mesh(
    cx: float,
    cy: float,
    cz: float,
    edge: float,
) -> Tuple[List[vec3], List[tri]]:
    """cubo alinhado aos eixos centrado em (cx,cy,cz); aresta edge em metros."""
    return box_mesh_anisotropic(cx, cy, cz, edge, edge, edge)


def merge_mesh(
    va: List[vec3], fa: List[tri], vb: List[vec3], fb: List[tri]
) -> Tuple[List[vec3], List[tri]]:
    # funcao merge_mesh
    # concatena a malha b depois da malha a
    # va fa vertices e faces da primeira parte
    # vb fb vertices e faces da segunda parte
    # off numero de vertices ja existentes antes de colar b
    off = len(va)
    # somamos listas de vertices
    # somamos faces da segunda malha com indices deslocados por off
    return va + vb, fa + [(a + off, b + off, c + off) for a, b, c in fb]


def cylinder_axis(
    cx: float,
    cy: float,
    cz: float,
    radius: float,
    height: float,
    *,
    axis: str = "y",
    segments: int = 24,
) -> Tuple[List[vec3], List[tri]]:
    # cilindro com tampas, orientado ao longo de x/y/z
    # usado para representar a fatia fina (disco/cilindro achatado) de uma esfera
    if radius <= 0 or height <= 0 or segments < 3:
        return [], []
    a = axis.strip().lower()
    if a not in ("x", "y", "z"):
        a = "y"
    h2 = height / 2.0

    def make_point(ang: float, t: float) -> vec3:
        c = math.cos(ang) * radius
        s = math.sin(ang) * radius
        if a == "y":
            return (cx + c, cy + t, cz + s)
        if a == "x":
            return (cx + t, cy + c, cz + s)
        return (cx + c, cy + s, cz + t)

    verts: List[vec3] = []
    faces: List[tri] = []
    # centros das tampas
    if a == "y":
        cb = (cx, cy - h2, cz)
        ct = (cx, cy + h2, cz)
    elif a == "x":
        cb = (cx - h2, cy, cz)
        ct = (cx + h2, cy, cz)
    else:
        cb = (cx, cy, cz - h2)
        ct = (cx, cy, cz + h2)
    verts.append(cb)  # 0
    verts.append(ct)  # 1

    base_ring = 2
    # aneis inferior e superior
    for i in range(segments):
        ang = 2 * math.pi * i / segments
        verts.append(make_point(ang, -h2))
    for i in range(segments):
        ang = 2 * math.pi * i / segments
        verts.append(make_point(ang, +h2))

    def ni(i: int) -> int:
        return (i + 1) % segments

    rb = lambda i: base_ring + i
    rt = lambda i: base_ring + segments + i
    # disco inferior
    for i in range(segments):
        j = ni(i)
        faces.append((0, rb(i), rb(j)))
    # disco superior
    for i in range(segments):
        j = ni(i)
        faces.append((1, rt(j), rt(i)))
    # lateral
    for i in range(segments):
        j = ni(i)
        faces.append((rb(i), rt(i), rt(j)))
        faces.append((rb(i), rt(j), rb(j)))

    return verts, faces


def filter_faces_by_slab(
    vertices: List[vec3],
    faces: List[tri],
    *,
    axis: str,
    min_v: float,
    max_v: float,
) -> Tuple[List[vec3], List[tri]]:
    # mantem triangulos que intersectam a faixa [min_v, max_v]
    # criterio simples: intervalo dos 3 vertices sobrepoe o intervalo da fatia
    # isto corta a parede e tampas para formar uma fatia fina (sem cap automatico)
    a = axis.strip().lower()
    if a not in ("x", "y", "z"):
        a = "y"
    ai = 0 if a == "x" else (1 if a == "y" else 2)
    keep_faces: List[tri] = []
    used: List[int] = []
    used_set = set()
    for (i, j, k) in faces:
        vi = vertices[i][ai]
        vj = vertices[j][ai]
        vk = vertices[k][ai]
        tri_min = min(vi, vj, vk)
        tri_max = max(vi, vj, vk)
        if tri_max >= min_v and tri_min <= max_v:
            keep_faces.append((i, j, k))
            for idx in (i, j, k):
                if idx not in used_set:
                    used_set.add(idx)
                    used.append(idx)
    # remap compacto
    remap = {old: new for new, old in enumerate(used)}
    new_verts = [vertices[i] for i in used]
    new_faces = [(remap[i], remap[j], remap[k]) for (i, j, k) in keep_faces]
    return new_verts, new_faces


def clip_mesh_to_util_volume(
    vertices: List[vec3],
    faces: List[tri],
    *,
    r_util: float,
    slice_axis: str,
    slice_center: float,
    slice_thickness: float,
) -> Tuple[List[vec3], List[tri]]:
    """
    remove triangulos com algum vertice fora do cilindro util (rho) ou fora da faixa do slice.
    conservador: pode apagar mais do que o clip exacto.
    """
    if not vertices or not faces:
        return [], []
    a = slice_axis.strip().lower()
    if a not in ("x", "y", "z"):
        a = "y"
    ai = 0 if a == "x" else (1 if a == "y" else 2)
    lo = slice_center - slice_thickness / 2.0
    hi = slice_center + slice_thickness / 2.0

    def inside(p: vec3) -> bool:
        if math.hypot(p[0], p[1]) > r_util + 1e-9:
            return False
        s = p[ai]
        return lo - 1e-9 <= s <= hi + 1e-9

    keep_faces: List[tri] = []
    used: List[int] = []
    used_set = set()
    for (i, j, k) in faces:
        if inside(vertices[i]) and inside(vertices[j]) and inside(vertices[k]):
            keep_faces.append((i, j, k))
            for idx in (i, j, k):
                if idx not in used_set:
                    used_set.add(idx)
                    used.append(idx)
    remap = {old: new for new, old in enumerate(used)}
    new_verts = [vertices[i] for i in used]
    new_faces = [(remap[i], remap[j], remap[k]) for (i, j, k) in keep_faces]
    return new_verts, new_faces


def annulus_cap_pair(
    *,
    r_ext: float,
    r_int: float,
    axis: str,
    position: float,
    thickness: float,
    segments: int = 24,
) -> Tuple[List[vec3], List[tri]]:
    """fecha a lamina com dois aneis (tampas da fatia) no plano perpendicular ao eixo."""
    if r_ext <= r_int or thickness <= 0 or segments < 3:
        return [], []
    a = axis.strip().lower()
    if a not in ("x", "y", "z"):
        a = "y"
    half = thickness / 2.0
    planes = (position - half, position + half)
    verts: List[vec3] = []
    faces: List[tri] = []

    def ring_point(r: float, ang: float, plane_val: float) -> vec3:
        c = math.cos(ang)
        s = math.sin(ang)
        if a == "x":
            return (plane_val, r * c, r * s)
        if a == "y":
            return (r * c, plane_val, r * s)
        return (r * c, r * s, plane_val)

    for plane_val in planes:
        base = len(verts)
        for i in range(segments):
            ang = 2 * math.pi * i / segments
            verts.append(ring_point(r_ext, ang, plane_val))
        for i in range(segments):
            ang = 2 * math.pi * i / segments
            verts.append(ring_point(r_int, ang, plane_val))
        for i in range(segments):
            j = (i + 1) % segments
            eo, io = base + i, base + j
            ei, ii = base + segments + i, base + segments + j
            faces.append((eo, ei, io))
            faces.append((io, ei, ii))
    return verts, faces


def rect_frame_mesh(
    *,
    slice_axis: str,
    position: float,
    thickness: float,
    half_width_outer: float,
    half_width_inner: float,
    w_outer_min: float,
    w_outer_max: float,
    w_inner_min: float,
    w_inner_max: float,
) -> Tuple[List[vec3], List[tri]]:
    """moldura retangular fina (retângulo com corte retangular no meio) no plano de corte.

    representa a parede do leito como um "porta-retrato" plano e fino, com a mesma
    espessura do plano de corte (eixo da fatia). decompõe-se em 4 barras sem
    sobreposição: parede esquerda/direita (altura cheia) + tampas inferior/superior
    (largura interna). o furo central (u∈[-iw,iw], w∈[wi0,wi1]) fica vazio.

    eixos no plano: u = eixo horizontal (radial, usa half_width_*),
    w = eixo da altura do leito (z, usa w_*). só faz sentido para corte vertical
    (slice_axis x ou y); para z cai para y por segurança.
    """
    a = slice_axis.strip().lower()
    if a not in ("x", "y"):
        a = "y"
    t = max(float(thickness), 1e-9)
    ow = max(float(half_width_outer), 0.0)
    iw = max(min(float(half_width_inner), ow), 0.0)
    wo0, wo1 = sorted((float(w_outer_min), float(w_outer_max)))
    wi0, wi1 = sorted((float(w_inner_min), float(w_inner_max)))
    # furo confinado ao retângulo externo
    wi0 = min(max(wi0, wo0), wo1)
    wi1 = min(max(wi1, wo0), wo1)

    bars: List[Tuple[float, float, float, float]] = []
    # paredes laterais (altura cheia)
    if ow - iw > 1e-12:
        bars.append((-ow, -iw, wo0, wo1))
        bars.append((iw, ow, wo0, wo1))
    # tampas inferior/superior (largura interna)
    if iw > 1e-12:
        if wi0 - wo0 > 1e-12:
            bars.append((-iw, iw, wo0, wi0))
        if wo1 - wi1 > 1e-12:
            bars.append((-iw, iw, wi1, wo1))

    v_all: List[vec3] = []
    f_all: List[tri] = []
    for (ua, ub, wa, wb) in bars:
        su = ub - ua
        sw = wb - wa
        if su <= 0 or sw <= 0:
            continue
        cu = (ua + ub) / 2.0
        cw = (wa + wb) / 2.0
        if a == "y":
            sv, sf = box_mesh_anisotropic(cu, position, cw, su, t, sw)
        else:  # x
            sv, sf = box_mesh_anisotropic(position, cu, cw, t, su, sw)
        v_all, f_all = merge_mesh(v_all, f_all, sv, sf)
    return v_all, f_all


def write_stl_binary(path: Path, vertices: List[vec3], faces: List[tri]) -> None:
    # funcao write_stl_binary
    # grava ficheiro stl binario padrao com uma normal por triangulo
    # path caminho de saida
    # vertices lista de todos os pontos
    # faces lista de triplos de indices
    # cria pastas pais se ainda nao existirem
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        # cabecalho de oitenta bytes reservado muitos leitores ignoram conteudo
        f.write(b"\0" * 80)
        # contagem de triangulos em uint32 little endian
        f.write(struct.pack("<I", len(faces)))
        # para cada triangulo calculamos a normal pela regra da mao direita
        for i, j, k in faces:
            x0, y0, z0 = vertices[i]
            x1, y1, z1 = vertices[j]
            x2, y2, z2 = vertices[k]
            # vetor u ao longo de uma aresta
            ux, uy, uz = x1 - x0, y1 - y0, z1 - z0
            # vetor v ao longo da outra aresta a partir do mesmo vertice
            vx, vy, vz = x2 - x0, y2 - y0, z2 - z0
            # produto vetorial u x v aponta para fora se a ordem i j k for coerente
            nx = uy * vz - uz * vy
            ny = uz * vx - ux * vz
            nz = ux * vy - uy * vx
            # comprimento para normalizar evita divisao por zero com or um
            ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            nx, ny, nz = nx / ln, ny / ln, nz / ln
            # 50 bytes/triangulo (padrao stl binario; three.js STLLoader usa faceLength=50)
            f.write(
                struct.pack(
                    "<12fH",
                    nx,
                    ny,
                    nz,
                    x0,
                    y0,
                    z0,
                    x1,
                    y1,
                    z1,
                    x2,
                    y2,
                    z2,
                    0,
                )
            )
