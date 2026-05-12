# este arquivo so roda dentro do blender porque importa bpy
# bpy e a api python do blender para criar malhas e objetos na cena

from __future__ import annotations

import bpy
from typing import List, Tuple, Any


def create_hollow_cylinder(
    outer_radius: float,
    inner_radius: float,
    height: float,
    name: str = "leito_extracao",
) -> Any:
    # cria o tubo oco igual a ideia do script principal
    # outer_radius raio externo da parede solida em metros
    # inner_radius raio do furo interno em metros
    # height altura do tubo ao longo de z em metros
    # name nome do objeto no outliner do blender
    if inner_radius >= outer_radius:
        raise ValueError("inner_radius must be less than outer_radius")
    # cilindro grande centrado em z igual metade da altura para base em zero e topo em height
    bpy.ops.mesh.primitive_cylinder_add(
        radius=outer_radius,
        depth=height,
        location=(0, 0, height / 2),
    )
    cilindro_externo = bpy.context.active_object
    cilindro_externo.name = name

    # cilindro menor um pouco mais alto para o boolean cortar limpo
    bpy.ops.mesh.primitive_cylinder_add(
        radius=inner_radius,
        depth=height + 0.01,
        location=(0, 0, height / 2),
    )
    cilindro_interno = bpy.context.active_object
    cilindro_interno.name = "furo_temporario"

    # modificador boolean subtrai o interno do externo
    bool_mod = cilindro_externo.modifiers.new(name="Boolean", type="BOOLEAN")
    bool_mod.operation = "DIFFERENCE"
    bool_mod.object = cilindro_interno

    bpy.context.view_layer.objects.active = cilindro_externo
    bpy.ops.object.modifier_apply(modifier="Boolean")
    bpy.data.objects.remove(cilindro_interno, do_unlink=True)
    return cilindro_externo


def create_caps(
    height: float,
    outer_diameter: float,
    bottom_thickness: float,
    top_thickness: float,
    bottom_name: str = "tampa_inferior",
    top_name: str = "tampa_superior",
    top_has_collision: bool = False,
) -> Tuple[Any, Any]:
    # cria duas tampas discos finos como cilindros baixos
    # height altura do leito para posicionar a tampa superior no topo
    # outer_diameter diametro externo igual ao tubo
    # bottom_thickness espessura da tampa de baixo
    # top_thickness espessura da tampa de cima
    # top_has_collision se false a fisica futura ignora colisao na tampa de cima no fluxo antigo
    r = outer_diameter / 2

    bpy.ops.mesh.primitive_cylinder_add(
        radius=r,
        depth=bottom_thickness,
        location=(0, 0, 0),
    )
    t_inf = bpy.context.active_object
    t_inf.name = bottom_name
    t_inf["tem_colisao"] = True

    bpy.ops.mesh.primitive_cylinder_add(
        radius=r,
        depth=top_thickness,
        location=(0, 0, height),
    )
    t_sup = bpy.context.active_object
    t_sup.name = top_name
    t_sup["tem_colisao"] = top_has_collision

    return t_inf, t_sup


def create_spheres(
    centers: List[Tuple[float, float, float]],
    radius: float,
    name_prefix: str = "particula",
    segments: int = 16,
    rings: int = 8,
) -> List[Any]:
    # cria muitas esferas reutilizando a mesma mesh para economizar memoria
    # centers lista de posicoes x y z
    # radius raio da esfera
    # name_prefix prefixo do nome particula_01 etc
    # segments e rings controlam suavidade da uv sphere
    if not centers:
        return []
    objs: List[Any] = []
    # primeira esfera cria o datablock de mesh
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        location=centers[0],
        segments=segments,
        ring_count=rings,
    )
    base_obj = bpy.context.active_object
    base_obj.name = f"{name_prefix}_01"
    objs.append(base_obj)

    coll = bpy.context.collection
    # demais esferas sao copias do objeto apontando para o mesmo base_obj.data
    for idx, loc in enumerate(centers[1:], start=2):
        o = base_obj.copy()
        o.data = base_obj.data
        o.location = loc
        o.name = f"{name_prefix}_{idx:02d}"
        coll.objects.link(o)
        objs.append(o)
    return objs


def create_cubes(
    centers: List[Tuple[float, float, float]],
    edge: float,
    name_prefix: str = "particula",
) -> List[Any]:
    """cubos com mesh datablock partilhado (instancias)."""
    if not centers or edge <= 0:
        return []
    objs: List[Any] = []
    bpy.ops.mesh.primitive_cube_add(size=edge, location=centers[0])
    base_obj = bpy.context.active_object
    base_obj.name = f"{name_prefix}_01"
    objs.append(base_obj)
    coll = bpy.context.collection
    for idx, loc in enumerate(centers[1:], start=2):
        o = base_obj.copy()
        o.data = base_obj.data
        o.location = loc
        o.name = f"{name_prefix}_{idx:02d}"
        coll.objects.link(o)
        objs.append(o)
    return objs


def create_cylinders(
    centers: List[Tuple[float, float, float]],
    diameter: float,
    name_prefix: str = "particula",
    vertices: int = 24,
) -> List[Any]:
    """cilindros ao longo de z; altura igual ao diametro (parametro unico do json)."""
    if not centers or diameter <= 0:
        return []
    r = diameter / 2.0
    depth = diameter
    objs: List[Any] = []
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=r,
        depth=depth,
        location=centers[0],
    )
    base_obj = bpy.context.active_object
    base_obj.name = f"{name_prefix}_01"
    objs.append(base_obj)
    coll = bpy.context.collection
    for idx, loc in enumerate(centers[1:], start=2):
        o = base_obj.copy()
        o.data = base_obj.data
        o.location = loc
        o.name = f"{name_prefix}_{idx:02d}"
        coll.objects.link(o)
        objs.append(o)
    return objs


def create_particles_by_kind(
    kind: str,
    centers: List[Tuple[float, float, float]],
    diameter: float,
    name_prefix: str = "particula",
) -> List[Any]:
    """despacho por particles.kind: sphere | cube | cylinder."""
    k = (kind or "sphere").strip().lower()
    if k == "cube":
        return create_cubes(centers, diameter, name_prefix=name_prefix)
    if k == "cylinder":
        return create_cylinders(centers, diameter, name_prefix=name_prefix)
    return create_spheres(centers, diameter / 2.0, name_prefix=name_prefix)
