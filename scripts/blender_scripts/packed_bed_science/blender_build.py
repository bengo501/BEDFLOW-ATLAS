# este arquivo so roda dentro do blender porque importa bpy
# bpy e a api python do blender para criar malhas e objetos na cena

from __future__ import annotations

import bpy
from typing import Any, List, Optional, Tuple


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


def create_visible_inner_cylinders(
    outer_radius: float,
    inner_radius: float,
    height: float,
    *,
    outer_name: str = "leito_externo",
    inner_name: str = "cilindro_interno_vis",
) -> Tuple[Any, Any]:
    """[OBSOLETO] dois cilindros cheios concentricos (o externo solido engloba o
    interno => sobreposicao parede/nucleo). nao usar: o m2 agora usa parede anelar
    + nucleo solido (create_bed_by_internal_mode). mantido apenas por compatibilidade."""
    if inner_radius >= outer_radius:
        raise ValueError("inner_radius must be less than outer_radius")
    bpy.ops.mesh.primitive_cylinder_add(
        radius=outer_radius,
        depth=height,
        location=(0, 0, height / 2),
    )
    outer = bpy.context.active_object
    outer.name = outer_name
    bpy.ops.mesh.primitive_cylinder_add(
        radius=inner_radius,
        depth=height,
        location=(0, 0, height / 2),
    )
    inner = bpy.context.active_object
    inner.name = inner_name
    return outer, inner


def create_solid_inner_core(
    inner_radius: float,
    height: float,
    name: str = "nucleo_interno",
    *,
    z_bottom: Optional[float] = None,
    z_top: Optional[float] = None,
) -> Any:
    """cilindro solido r_int (m2/m3) que preenche o vao interno ENTRE as tampas.

    z_bottom/z_top delimitam o vao (faces internas das tampas); quando None ocupa
    toda a altura. evita que o nucleo invada o volume das tampas.
    """
    z0 = 0.0 if z_bottom is None else float(z_bottom)
    z1 = float(height) if z_top is None else float(z_top)
    depth = max(z1 - z0, 1e-6)
    cz = (z0 + z1) / 2.0
    bpy.ops.mesh.primitive_cylinder_add(
        radius=inner_radius,
        depth=depth,
        location=(0, 0, cz),
    )
    core = bpy.context.active_object
    core.name = name
    return core


def _apply_boolean_difference(target: Any, tool: Any, mod_name: str = "Boolean") -> bool:
    bool_mod = target.modifiers.new(name=mod_name, type="BOOLEAN")
    bool_mod.operation = "DIFFERENCE"
    bool_mod.object = tool
    try:
        bool_mod.solver = "EXACT"
    except TypeError:
        pass
    bpy.context.view_layer.objects.active = target
    try:
        bpy.ops.object.modifier_apply(modifier=mod_name)
        return True
    except Exception:
        return False


def punch_core_with_particle_tools(
    core_obj: Any,
    centers: List[Tuple[float, float, float]],
    diameter: float,
    kind: str = "sphere",
    *,
    max_tools: Optional[int] = None,
) -> Tuple[str, List[str], int]:
    """m3 blender: difference no nucleo com uma ferramenta por particula; tools removidas apos apply."""
    warnings: List[str] = []
    if not centers or core_obj is None:
        return "n/a", warnings, 0
    k = (kind or "sphere").strip().lower()
    r = diameter / 2.0
    if max_tools is None:
        n = len(centers)
    else:
        n = min(len(centers), max(0, int(max_tools)))
    applied = 0
    for idx, loc in enumerate(centers[:n], start=1):
        if k == "cube":
            bpy.ops.mesh.primitive_cube_add(size=diameter, location=loc)
        elif k == "cylinder":
            bpy.ops.mesh.primitive_cylinder_add(
                radius=r, depth=diameter, location=loc
            )
        else:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc)
        tool = bpy.context.active_object
        tool.name = f"boolean_tool_{idx:03d}"
        tool.data = tool.data.copy()
        if _apply_boolean_difference(core_obj, tool, mod_name=f"BoolHole{idx}"):
            applied += 1
        bpy.data.objects.remove(tool, do_unlink=True)
    if applied == 0:
        warnings.append("nenhuma booleana de furo aplicada no nucleo")
        return "failed", warnings, 0
    if applied < n:
        warnings.append(f"apenas {applied}/{n} furos aplicados (limite max_tools)")
    return "applied", warnings, applied


def _interior_core_span(
    height: float, bottom_cap: float, top_cap: float
) -> Tuple[float, float]:
    """vao interno entre as faces internas das tampas.

    as tampas (create_caps) ficam centradas em z=0 e z=height, logo as faces
    internas estao em z=bottom_cap/2 e z=height-top_cap/2. o nucleo solido deve
    ficar nesse intervalo para nao sobrepor as tampas.
    """
    z0 = max(0.0, float(bottom_cap)) / 2.0
    z1 = float(height) - max(0.0, float(top_cap)) / 2.0
    if z1 <= z0:
        mid = float(height) / 2.0
        return mid - 1e-4, mid + 1e-4
    return z0, z1


def create_bed_by_internal_mode(
    mode: str,
    outer_radius: float,
    inner_radius: float,
    height: float,
    visibility: Optional[dict] = None,
    *,
    bottom_cap: float = 0.0,
    top_cap: float = 0.0,
) -> Tuple[Any, Optional[Any], dict]:
    """
    devolve (leito_principal, nucleo_opcional, boolean_operation_status parcial).

    m2/m3 usam parede anelar (create_hollow_cylinder) + nucleo solido r_int que
    preenche apenas o vao entre as tampas, evitando sobreposicao parede/nucleo e
    tampas/nucleo.
    """
    vis = visibility or {}
    show_outer = vis.get("show_outer_cylinder", True)
    show_inner = vis.get("show_internal_cylinder", False)
    m = (mode or "hollow_boolean_applied").strip().lower()
    z0, z1 = _interior_core_span(height, bottom_cap, top_cap)

    if m == "internal_cylinder_visible_no_boolean":
        if not show_outer:
            return None, None, {
                "outer_shell": "skipped",
                "inner_core": "visible_separate",
            }
        # parede anelar (sem sobrepor o nucleo) + nucleo solido visivel entre tampas
        leito = create_hollow_cylinder(outer_radius, inner_radius, height)
        inner = None
        if show_inner and inner_radius > 0:
            inner = create_solid_inner_core(
                inner_radius, height, name="cilindro_interno_vis",
                z_bottom=z0, z_top=z1,
            )
        return leito, inner, {
            "outer_shell": "explicit_annulus",
            "inner_core": "visible_separate" if inner else "n/a",
        }

    if m == "solid_internal_cylinder_with_particle_holes":
        leito = create_hollow_cylinder(outer_radius, inner_radius, height)
        core = create_solid_inner_core(
            inner_radius, height, z_bottom=z0, z_top=z1
        )
        if not show_inner:
            try:
                core.hide_set(True)
                core.hide_render = True
            except Exception:
                pass
        return leito, core, {
            "outer_shell": "explicit_annulus",
            "inner_core": "solid_with_holes",
        }

    leito = create_hollow_cylinder(outer_radius, inner_radius, height)
    return leito, None, {"outer_shell": "applied", "inner_core": "n/a"}


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
