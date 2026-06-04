import bpy
import math
import os
import random
import json
import sys
import argparse
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# o blender executa este arquivo como script entao o diretorio do arquivo precisa estar no sys path
# assim o python acha a pasta packed_bed_science ao lado deste arquivo
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

# modulos sem bpy definem matematica validacao e algoritmos de posicao
from packed_bed_science.geometry_math import AnnulusBedDomain, estimate_porosity, collision_radius_for_particle_kind
from packed_bed_science.packing_modes import merge_root_packing_mode, packing_method_from_section
from packed_bed_science.validation import validate_configuration
from packed_bed_science.packing_spherical import generate_spherical_packing
from packed_bed_science.packing_hexagonal import generate_hexagonal_packing

# blender_build usa bpy para criar tubo tampas e esferas ja posicionadas
from packed_bed_science.blender_build import (
    create_bed_by_internal_mode,
    create_caps,
    create_hollow_cylinder,
    create_particles_by_kind,
    punch_core_with_particle_tools,
)

# =============
# Limpar cena =
# =========================================================================================
def limpar_cena():
    #remove todos os objetos da cena
    bpy.ops.object.select_all(action='SELECT') #selecionar todos os objetos da cena
    bpy.ops.object.delete(use_global=False) # deletar todos os objetos da cena
    print("cena limpa")
# =========================================================================================

# ====================
# Criar cilindro oco =
# =========================================================================================
def criar_cilindro_oco(altura=0.1, diametro_externo=0.025, espessura_parede=0.002):
    # cria um cilindro oco (leito de extracao)
    # parametros: altura: altura do leito em metros
    #             diametro_externo: diametro externo em metros  
    #             espessura_parede: espessura da parede em metros
    
    # calcular raios
    raio_externo = diametro_externo / 2 # calcular raio externo baseado no diametro externo dividido por 2
    raio_interno = raio_externo - espessura_parede # calcular raio interno baseado no raio externo e espessura da parede
    
    # criar cilindro externo
    bpy.ops.mesh.primitive_cylinder_add( # criar cilindro com tamanho especifico e localizacao 0,0,0 (centro)
        radius=raio_externo, # raio do cilindro baseado no raio externo
        depth=altura, # altura do cilindro baseado na altura
        location=(0, 0, altura/2) # localizacao do cilindro baseada na altura dividida por 2
    )
    cilindro_externo = bpy.context.active_object # objeto ativo atual
    cilindro_externo.name = "leito_extracao" # nome do objeto leito_extracao
    
    # criar cilindro interno para fazer o furo
    bpy.ops.mesh.primitive_cylinder_add( # criar cilindro com tamanho especifico e localizacao 0,0,0 (centro)
        radius=raio_interno, # raio do cilindro baseado no raio interno
        depth=altura + 0.01,  # um pouco maior para cortar bem
        location=(0, 0, altura/2) # localizacao do cilindro baseada na altura dividida por 2
    )
    cilindro_interno = bpy.context.active_object # objeto ativo atual
    cilindro_interno.name = "furo_temporario" # nome do objeto furo_temporario
    
    # fazer operacao booleana (subtracao)
    bool_mod = cilindro_externo.modifiers.new(name="Boolean", type='BOOLEAN') # criar modificador booleano
    bool_mod.operation = 'DIFFERENCE' # operacao booleana (subtracao)
    bool_mod.object = cilindro_interno # objeto interno para subtrair
    
    # aplicar o modificador
    bpy.context.view_layer.objects.active = cilindro_externo # objeto ativo atual
    bpy.ops.object.modifier_apply(modifier="Boolean") # aplicar o modificador booleano
    
    # remover cilindro interno temporario
    bpy.data.objects.remove(cilindro_interno, do_unlink=True) # remover o cilindro interno
    
    print(f"leito criado: altura={altura}m, diametro={diametro_externo}m")
    return cilindro_externo # retornar o cilindro externo
# =========================================================================================

# =============
# Criar tampa =
# =========================================================================================
def criar_tampa(posicao_z, diametro=0.025, espessura=0.003, nome="tampa", tem_colisao=True):
    # cria uma tampa circular
    # parametros: posicao_z: posicao vertical da tampa
    #             diametro: diametro da tampa
    #             espessura: espessura da tampa
    #             nome: nome do objeto
    #             tem_colisao: se false, particulas atravessam (tampa superior)
    bpy.ops.mesh.primitive_cylinder_add( # criar cilindro com tamanho especifico e localizacao 0,0,0 (centro)
        radius=diametro/2,
        depth=espessura, # espessura do cilindro
        location=(0, 0, posicao_z) # localizacao do cilindro baseada na posicao z
    )
    tampa = bpy.context.active_object # objeto ativo atual
    tampa.name = nome # nome do objeto
    tampa["tem_colisao"] = tem_colisao  # marcar se tem colisao
    
    print(f"{nome} criada na posicao z={posicao_z}m (colisao: {tem_colisao})")
    return tampa
# =========================================================================================

# ==================
# Criar particulas =
# =========================================================================================
def criar_particulas(
    quantidade=30,
    raio_leito=0.0125,
    altura_leito=0.1,
    raio_particula=0.001,
    kind: str = "sphere",
    diametro_particula: Optional[float] = None,
):
    # posicoes iniciais acima do leito; malha conforme kind (instancias partilhadas)
    d = float(diametro_particula) if diametro_particula is not None else float(raio_particula) * 2.0
    k = (kind or "sphere").strip().lower()
    posicoes: list = []
    for i in range(int(quantidade)):
        x = random.uniform(-raio_leito * 0.7, raio_leito * 0.7)
        y = random.uniform(-raio_leito * 0.7, raio_leito * 0.7)
        z = altura_leito + 0.02 + (i * 0.005)
        posicoes.append((x, y, z))
    particulas = create_particles_by_kind(k, posicoes, d)
    print(f"{len(particulas)} particulas ({k}) criadas")
    return particulas
# =========================================================================================

# ================
# Aplicar fisica =
# =========================================================================================
def aplicar_fisica(objeto, eh_movel=True, tem_colisao=True):
    # aplica fisica de corpo rigido aos objetos    
    # parametros: objeto: objeto do blender
    #             eh_movel: se true, objeto pode se mover (particulas)
    #             se false, objeto eh estatico (leito e tampas)
    #             tem_colisao: se false, objeto nao colide (tampa superior)

    # selecionar o objeto
    bpy.context.view_layer.objects.active = objeto
    
    # verificar se objeto tem marcacao de colisao customizada
    if "tem_colisao" in objeto and not objeto["tem_colisao"]:
        print(f"fisica nao aplicada (sem colisao): {objeto.name}")
        return
    
    #aplicar fisica de acordo com o tipo de objeto
    if eh_movel:
        # particulas: corpo rigido com gravidade
        bpy.ops.rigidbody.object_add(type='ACTIVE')
        objeto.rigid_body.mass = 0.01  # massa pequena
        objeto.rigid_body.friction = 0.5  # atrito medio
        objeto.rigid_body.restitution = 0.3  # pouco elastica
        objeto.rigid_body.linear_damping = 0.1  # amortecimento linear
        objeto.rigid_body.angular_damping = 0.1  # amortecimento angular
        print(f"fisica aplicada (movel): {objeto.name}")
    else:
        # leito e tampas: corpo rigido sem gravidade (estatico)
        bpy.ops.rigidbody.object_add(type='PASSIVE')
        objeto.rigid_body.friction = 0.8  # muito atrito para segurar particulas
        objeto.rigid_body.restitution = 0.1  # pouco elastico
        
        # importante: usar mesh collision para cilindro oco
        objeto.rigid_body.collision_shape = 'MESH'
        objeto.rigid_body.mesh_source = 'FINAL'  # usar geometria final (pos-boolean)
        
        print(f"fisica aplicada (estatico, mesh collision): {objeto.name}")
# =========================================================================================

# =============================
# Configurar simulacao fisica =
# =========================================================================================
def configurar_simulacao_fisica(gravidade=-9.81, substeps=10, iterations=10):
    #configura parametros globais da simulacao fisica
    scene = bpy.context.scene
    
    # configurar mundo da fisica
    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    
    # configurar propriedades do mundo da fisica
    if scene.rigidbody_world:
        try:
            # configurar gravidade
            if hasattr(scene.rigidbody_world, 'effector_weights'):
                scene.rigidbody_world.effector_weights.gravity = abs(gravidade) / 9.81
            
            # configurar qualidade da simulacao
            if hasattr(scene.rigidbody_world, 'substeps_per_frame'):
                scene.rigidbody_world.substeps_per_frame = substeps
            
            if hasattr(scene.rigidbody_world, 'solver_iterations'):
                scene.rigidbody_world.solver_iterations = iterations
            
            # configurar velocidade de repouso
            if hasattr(scene.rigidbody_world, 'use_split_impulse'):
                scene.rigidbody_world.use_split_impulse = True
                
            print(f"simulacao fisica configurada (gravidade: {gravidade}, substeps: {substeps}, iterations: {iterations})")
            
        except AttributeError as e:
            print(f"aviso: nao foi possivel configurar todas as propriedades da fisica: {e}")
            print("usando configuracao padrao do blender")
    else:
        print("erro: nao foi possivel criar mundo da fisica")
# =========================================================================================

# =====================
# Executar simulacao =
# =========================================================================================
def executar_simulacao_fisica(tempo_simulacao=5.0, fps=24):
    """
    executa a animacao de fisica para fazer particulas cairem
    
    parametros:
        tempo_simulacao: tempo em segundos da simulacao
        fps: frames por segundo (padrao 24)
    """
    scene = bpy.context.scene
    
    # configurar range de frames
    total_frames = int(tempo_simulacao * fps)
    scene.frame_start = 1
    scene.frame_end = total_frames
    scene.frame_current = 1
    
    print(f"\nexecutando simulacao fisica...")
    print(f"tempo: {tempo_simulacao}s | frames: {total_frames} | fps: {fps}")
    
    # executar frame por frame para garantir fisica
    for frame in range(1, total_frames + 1):
        scene.frame_set(frame)
        
        # mostrar progresso a cada 10%
        if frame % (total_frames // 10) == 0 or frame == 1 or frame == total_frames:
            progresso = (frame / total_frames) * 100
            print(f"  progresso: {progresso:.0f}% (frame {frame}/{total_frames})")
    
    print("simulacao fisica executada com sucesso!")
    print("particulas acomodadas no leito\n")
# =========================================================================================

# ==================
# Bake da fisica =
# =========================================================================================
def _temp_override_view3d():
    """
    em --background muitas vezes nao ha area VIEW_3D; bake_to_keyframes e keyframe_insert
    exigem contexto 3d valido. devolve (dict_para_temp_override ou None, area_promovida_ou_None, tipo_anterior).
    """
    wm = bpy.context.window_manager
    if not wm.windows:
        return None, None, None
    win = wm.windows[0]
    for area in win.screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "WINDOW":
                    ctx = dict(
                        window=win,
                        screen=win.screen,
                        area=area,
                        region=region,
                        scene=bpy.context.scene,
                        view_layer=bpy.context.view_layer,
                    )
                    return ctx, None, None
    area = win.screen.areas[0]
    prev = area.type
    area.type = "VIEW_3D"
    region = None
    for r in area.regions:
        if r.type == "WINDOW":
            region = r
            break
    if region is None:
        area.type = prev
        return None, None, None
    ctx = dict(
        window=win,
        screen=win.screen,
        area=area,
        region=region,
        scene=bpy.context.scene,
        view_layer=bpy.context.view_layer,
    )
    return ctx, area, prev


def _congelar_particulas_depsgraph(particulas):
    """
    fallback headless: copia matrix_world avaliada no frame atual e remove rigid body
    sem depender de bake_to_keyframes.
    """
    depsgraph = bpy.context.evaluated_depsgraph_get()
    bpy.context.view_layer.update()
    for obj in particulas:
        ev = obj.evaluated_get(depsgraph)
        obj.matrix_world = ev.matrix_world.copy()
    ovr, promoted_area, promoted_prev = _temp_override_view3d()
    if ovr is None:
        print("aviso: sem override 3d; posicoes copiadas mas rigid body pode permanecer")
        return
    try:
        with bpy.context.temp_override(**ovr):
            for obj in particulas:
                if not obj.rigid_body:
                    continue
                bpy.ops.object.select_all(action="DESELECT")
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.rigidbody.object_remove()
        print("congelamento alternativo: matriz avaliada aplicada e rigid body removido")
    except Exception as e:
        print(f"aviso: congelamento alternativo incompleto: {e}")
    finally:
        if promoted_area is not None and promoted_prev is not None:
            promoted_area.type = promoted_prev


def fazer_bake_fisica(particulas):
    """
    faz bake (congelamento) da fisica nas particulas
    isso converte a simulacao em keyframes fixos
    """
    print("\nfazendo bake da fisica...")

    ovr, promoted_area, promoted_prev = _temp_override_view3d()
    try:
        if ovr is not None:
            with bpy.context.temp_override(**ovr):
                bpy.ops.object.select_all(action="DESELECT")
                for particula in particulas:
                    particula.select_set(True)
                if particulas:
                    bpy.context.view_layer.objects.active = particulas[0]
                bpy.ops.rigidbody.bake_to_keyframes(
                    frame_start=bpy.context.scene.frame_start,
                    frame_end=bpy.context.scene.frame_end,
                    step=1,
                )
            print("bake concluido - fisica convertida em keyframes")
            with bpy.context.temp_override(**ovr):
                for particula in particulas:
                    if particula.rigid_body:
                        bpy.ops.object.select_all(action="DESELECT")
                        particula.select_set(True)
                        bpy.context.view_layer.objects.active = particula
                        bpy.ops.rigidbody.object_remove()
            print("rigid body removido - particulas estao fixas nas posicoes finais")
        else:
            raise RuntimeError("sem contexto VIEW_3D para bake")
    except Exception as e:
        print(f"aviso: erro no bake: {e}")
        print("tentando congelar posicoes via depsgraph (modo background)...")
        _congelar_particulas_depsgraph(particulas)
    finally:
        if promoted_area is not None and promoted_prev is not None:
            promoted_area.type = promoted_prev
# =========================================================================================

# ======
# Main =
# =========================================================================================
def main():
    #funcao principal - cria tudo e configura fisica
    print("======criando leito de extracao com fisica=======")
    # limpar tudo
    limpar_cena()
    # parametros do leito
    altura = 0.1          # 10 cm
    diametro = 0.025      # 2.5 cm  
    espessura = 0.002     # 2 mm
    # criar geometria
    print("criando geometria...")
    leito = criar_cilindro_oco(altura, diametro, espessura)
    tampa_inferior = criar_tampa(-espessura/2, diametro, espessura, "tampa_inferior", tem_colisao=True)
    tampa_superior = criar_tampa(altura + espessura/2, diametro, espessura, "tampa_superior", tem_colisao=False)
    # criar particulas
    particulas = criar_particulas(30, diametro/2, altura, 0.001)
    # configurar fisica
    print("configurando fisica...")
    configurar_simulacao_fisica()
    # aplicar fisica ao leito e tampas (estaticos)
    aplicar_fisica(leito, eh_movel=False)
    aplicar_fisica(tampa_inferior, eh_movel=False)
    # tampa superior sem colisao (particulas atravessam)
    aplicar_fisica(tampa_superior, eh_movel=False)
    # aplicar fisica as particulas (moveis)
    for particula in particulas:
        aplicar_fisica(particula, eh_movel=True)
    
    # executar simulacao para particulas cairem
    executar_simulacao_fisica(tempo_simulacao=5.0, fps=24)
    
    # fazer bake para fixar posicoes finais
    fazer_bake_fisica(particulas)
    
    print()
    print("=====pronto=====")
    print(f"objetos criados:")
    print(f"- leito cilindrico oco (colisao: mesh)")
    print(f"- tampa inferior (colisao: ativa)")
    print(f"- tampa superior (colisao: desativada)")
    print(f"- {len(particulas)} particulas (posicoes finais apos fisica)")
    print()
    print("particulas ja estao acomodadas dentro do leito!")
    print("abra o arquivo para ver o resultado final")

def ler_parametros_json(json_path):
    """ler parametros do arquivo json"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            params = json.load(f)
        if isinstance(params, dict):
            merge_root_packing_mode(params)
        print(f"parametros carregados de: {json_path}")
        return params
    except Exception as e:
        print(f"erro ao ler json: {e}")
        return None


def _coerce_float(v, default=0.0):
    # o json do compilador as vezes vem com numeros como texto
    # esta funcao devolve sempre float usando default se v for none
    if v is None:
        return float(default)
    if isinstance(v, (int, float)):
        return float(v)
    return float(str(v).strip())


def _coerce_int(v, default=0):
    # igual ao float mas arredonda para inteiro no final
    if v is None:
        return int(default)
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return int(v)
    return int(float(str(v).strip()))


def _packing_method_name(packing):
    return packing_method_from_section(packing)


def _coerce_bool(v, default=True):
    # json pode trazer true false como string em alguns fluxos manuais
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in ("true", "1", "yes", "sim"):
        return True
    if s in ("false", "0", "no", "nao"):
        return False
    return default


def _boolean_intersect_apply(target_obj, cutter_obj, label: str = "thin_slice") -> bool:
    try:
        mod = target_obj.modifiers.new(name=label, type="BOOLEAN")
        mod.operation = "INTERSECT"
        mod.object = cutter_obj
        if hasattr(mod, "solver"):
            try:
                mod.solver = "EXACT"
            except Exception:
                pass
        bpy.context.view_layer.objects.active = target_obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
        return True
    except Exception as e:
        print(f"aviso: boolean {label} falhou em {target_obj.name}: {e}")
        return False


def _set_object_dimensions_on_slice_axis(
    obj,
    *,
    slice_axis: str,
    thickness: float,
    size_a: float,
    size_b: float,
) -> None:
    """define dimensões mundiais: espessura no eixo da fatia, tamanhos no plano."""
    ax = (slice_axis or "y").strip().lower()
    t = max(float(thickness), 1e-9)
    a = max(float(size_a), 1e-9)
    b = max(float(size_b), 1e-9)
    if ax == "x":
        obj.dimensions = (t, a, b)
    elif ax == "y":
        obj.dimensions = (a, t, b)
    else:
        obj.dimensions = (a, b, t)


def _create_slice_disc_bpy(
    loc3: Tuple[float, float, float],
    *,
    radius: float,
    thickness: float,
    slice_axis: str,
    name: str,
    vertices: int = 24,
) -> Any:
    """cilindro fino com eixo local z rodado para coincidir com slice_axis (discos circulares na fatia)."""
    from mathutils import Euler  # noqa: E402
    from thin_slice_particles import blender_cylinder_rotation  # noqa: E402

    rs = max(float(radius), 1e-9)
    t = max(float(thickness), 1e-9)
    rot = blender_cylinder_rotation(slice_axis)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=max(8, vertices),
        radius=rs,
        depth=t,
        location=loc3,
        rotation=Euler(rot, "XYZ"),
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj


def _boolean_difference_apply(target_obj, cutter_obj, label: str = "rect_hole") -> bool:
    """aplica boolean DIFFERENCE (target - cutter) e consolida o modificador."""
    try:
        mod = target_obj.modifiers.new(name=label, type="BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.object = cutter_obj
        if hasattr(mod, "solver"):
            try:
                mod.solver = "EXACT"
            except Exception:
                pass
        bpy.context.view_layer.objects.active = target_obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
        return True
    except Exception as e:
        print(f"aviso: boolean difference {label} falhou em {target_obj.name}: {e}")
        return False


def _create_rect_frame_bpy(frame, *, bottom_cap: float = 0.0, top_cap: float = 0.0):
    """parede da fatia como moldura retangular fina (retângulo com corte retangular no meio).

    caixa externa (2*r_ext de largura, altura cheia, espessura = plano de corte) menos
    caixa interna (2*r_int de largura, altura útil), no plano de corte. eixo do leito = z;
    só faz sentido para corte vertical (slice_axis x ou y).
    """
    axis = frame.slice_axis if frame.slice_axis in ("x", "y") else "y"
    t = max(float(frame.slice_thickness), 1e-9)
    r_ext = float(frame.r_ext)
    r_int = float(frame.r_util)
    h = float(frame.height)
    pos = float(frame.slice_center)
    inner_h = max(h - max(0.0, float(bottom_cap)) - max(0.0, float(top_cap)), 1e-6)
    z_center = max(0.0, float(bottom_cap)) + inner_h / 2.0

    if axis == "x":
        outer_dims = (t, 2.0 * r_ext, h)
        inner_dims = (t * 2.0, 2.0 * r_int, inner_h)
        outer_loc = (pos, 0.0, h / 2.0)
        inner_loc = (pos, 0.0, z_center)
    else:  # y
        outer_dims = (2.0 * r_ext, t, h)
        inner_dims = (2.0 * r_int, t * 2.0, inner_h)
        outer_loc = (0.0, pos, h / 2.0)
        inner_loc = (0.0, pos, z_center)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=outer_loc)
    outer = bpy.context.active_object
    outer.name = "thin_slice_frame"
    outer.dimensions = outer_dims

    if r_int > 1e-9:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=inner_loc)
        inner = bpy.context.active_object
        inner.name = "thin_slice_frame_hole"
        inner.dimensions = inner_dims
        _boolean_difference_apply(outer, inner, label="thin_slice_frame_hole")
        try:
            bpy.data.objects.remove(inner, do_unlink=True)
        except Exception:
            pass
    return outer


def aplicar_thin_slice(
    slice_cfg: dict,
    *,
    altura: float,
    raio_ext: float,
    raio_int: float,
    particle_centers: Optional[List[Tuple[float, float, float]]] = None,
    particle_diameter: float = 0.005,
    particle_kind: str = "sphere",
    bottom_cap: float = 0.0,
    top_cap: float = 0.0,
    output_path: Optional[Path] = None,
) -> Dict[str, Any]:
    # leito e tampas: boolean intersect com cubo fino (referencial unificado)
    # particulas: filtro contained/intersecting; intersecting clipa com slice_volume
    from mathutils import Euler

    if not isinstance(slice_cfg, dict):
        return {}
    if not _coerce_bool(slice_cfg.get("slice_enabled"), False):
        return {}

    _pm = Path(__file__).resolve().parents[1] / "python_modeling"
    if str(_pm) not in sys.path:
        sys.path.insert(0, str(_pm))
    from bed_reference_frame import blender_cutter_spec, frame_from_slice_cfg  # noqa: E402
    from geometry_modes import (  # noqa: E402
        SLICE_WALL_RECTANGULAR,
        axis_index,
        normalize_slice_wall_mode,
        particle_passes_policy,
        particle_slice_metrics,
        snap_center_radial_to_util_wall,
    )
    from slice_debug_export import empty_slice_summary, write_slice_debug_json  # noqa: E402
    from thin_slice_particles import (  # noqa: E402
        DROP_BELOW_MIN_RADIUS,
        DROP_LEAK_RADIAL,
        DROP_POLICY,
        SliceParticleConfig,
        prepare_slice_particle_for_mesh,
        sphere_intersects_slice,
    )

    frame = frame_from_slice_cfg(
        slice_cfg, r_int=raio_int, r_ext=raio_ext, height=altura
    )
    axis = frame.slice_axis
    thickness = frame.slice_thickness
    pos = frame.slice_center
    policy = frame.slice_particle_policy
    keep_only = _coerce_bool(slice_cfg.get("keep_only_intersecting_particles"), True)
    preserve = _coerce_bool(slice_cfg.get("preserve_original_packing"), True)
    pcfg = SliceParticleConfig.from_slice_cfg(slice_cfg, r_int=raio_int)
    pcfg.preserve_original_packing = preserve
    pcfg.keep_only_intersecting = keep_only

    pk = (particle_kind or "sphere").strip().lower()
    d_char = float(particle_diameter)
    r_ax = d_char * 0.5

    loc, scale = blender_cutter_spec(frame)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=tuple(loc))
    cutter = bpy.context.active_object
    cutter.name = "thin_slice_cutter"
    cutter.scale = tuple(scale)

    wall_mode = normalize_slice_wall_mode(slice_cfg.get("slice_wall_mode"))
    use_rect_wall = wall_mode == SLICE_WALL_RECTANGULAR and axis in ("x", "y")

    part_prefix = "particula"
    bed_targets = [
        o
        for o in bpy.data.objects
        if o.type == "MESH" and o.name != cutter.name and not o.name.lower().startswith(part_prefix)
    ]
    if use_rect_wall:
        # parede = moldura retangular fina no plano de corte: remove as paredes reais
        # do leito/tampas e cria o retângulo com corte retangular no meio
        for obj in bed_targets:
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
            except Exception:
                pass
        _create_rect_frame_bpy(frame, bottom_cap=bottom_cap, top_cap=top_cap)
    else:
        for obj in bed_targets:
            _boolean_intersect_apply(obj, cutter, label="thin_slice_bed")

    parts = [
        o
        for o in bpy.data.objects
        if o.type == "MESH" and o.name.lower().startswith(part_prefix)
    ]
    parts.sort(key=lambda o: o.name)

    if len(parts) > 0:
        if particle_centers is not None and len(particle_centers) == len(parts):
            centers_final: List[Tuple[float, float, float]] = [
                (float(t[0]), float(t[1]), float(t[2])) for t in particle_centers
            ]
        else:
            if particle_centers is not None:
                print(
                    "aviso fatia: lista de centros nao coincide com particulas na cena; "
                    "usa matrix_world de cada objeto"
                )
            centers_final = [tuple(o.matrix_world.translation) for o in parts]
    else:
        centers_final = (
            [(float(t[0]), float(t[1]), float(t[2])) for t in particle_centers]
            if particle_centers
            else []
        )

    for o in parts:
        try:
            bpy.data.objects.remove(o, do_unlink=True)
        except Exception:
            pass

    disc_verts = 24
    n_slice_parts = 0
    n_full_parts = 0
    summary = empty_slice_summary()
    summary["slice_particle_policy"] = policy
    summary["slice_thickness"] = thickness
    summary["slice_axis"] = axis
    summary["slice_position"] = pos
    summary["n_snapped_to_wall"] = 0
    summary["n_centers"] = len(centers_final)
    summary["n_discarded_by_radius_threshold"] = 0
    radii_kept: List[float] = []
    particle_logs: List[dict] = []

    for idx, (x, y, z) in enumerate(centers_final, start=1):
        center = (float(x), float(y), float(z))
        metrics = particle_slice_metrics(
            center,
            particle_kind=pk,
            particle_diameter=d_char,
            slice_axis=axis,
            slice_center=pos,
            slice_thickness=thickness,
            r_util=frame.r_util,
        )
        if not bool(metrics.get("passes_legacy_slice_only")):
            summary["n_dropped_legacy_slice"] += 1
            if keep_only:
                continue
            loc3 = center
            if pk == "cube":
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc3)
                obj = bpy.context.active_object
                obj.dimensions = (d_char, d_char, d_char)
            elif pk == "cylinder":
                bpy.ops.mesh.primitive_cylinder_add(
                    radius=r_ax,
                    depth=d_char,
                    location=loc3,
                    rotation=Euler((0.0, 0.0, 0.0), "XYZ"),
                )
                obj = bpy.context.active_object
            else:
                bpy.ops.mesh.primitive_uv_sphere_add(
                    radius=r_ax,
                    location=loc3,
                    segments=disc_verts,
                    ring_count=max(8, disc_verts // 2),
                )
                obj = bpy.context.active_object
            obj.name = f"particula_full_{idx:04d}"
            n_full_parts += 1
            summary["n_full_3d_outside"] += 1
            continue

        loc3, rs, prep_meta = prepare_slice_particle_for_mesh(
            center,
            pk,
            d_char,
            cfg=pcfg,
            policy=policy,
        )
        if loc3 is None:
            reason = prep_meta.get("reason")
            if reason == DROP_POLICY:
                summary["n_dropped_policy"] += 1
            elif reason == DROP_BELOW_MIN_RADIUS:
                summary["n_discarded_by_radius_threshold"] += 1
            elif reason == DROP_LEAK_RADIAL:
                summary["n_dropped_policy"] += 1
                summary["n_dropped_leak_radial"] = (
                    int(summary.get("n_dropped_leak_radial") or 0) + 1
                )
            if _coerce_bool(slice_cfg.get("debug_export_gizmos"), False):
                metrics["action"] = reason or "dropped"
                particle_logs.append(metrics)
            continue

        cx, cy, cz = loc3
        if prep_meta.get("snapped_to_wall"):
            summary["n_snapped_to_wall"] += 1
        slab_t = max(float(thickness), 1e-9)

        if pk == "cube":
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc3)
            obj = bpy.context.active_object
            _set_object_dimensions_on_slice_axis(
                obj,
                slice_axis=axis,
                thickness=slab_t,
                size_a=d_char,
                size_b=d_char,
            )
            obj.name = f"slice_box_{idx:04d}"
        else:
            obj = _create_slice_disc_bpy(
                loc3,
                radius=max(rs, r_ax * 0.25),
                thickness=slab_t,
                slice_axis=axis,
                name=f"slice_disc_{idx:04d}",
                vertices=disc_verts,
            )

        _boolean_intersect_apply(obj, cutter, label="thin_slice_particle")

        n_slice_parts += 1
        summary["n_kept"] += 1
        radii_kept.append(rs)
        if _coerce_bool(slice_cfg.get("debug_export_gizmos"), False):
            metrics["action"] = "kept"
            particle_logs.append(metrics)

    try:
        bpy.data.objects.remove(cutter, do_unlink=True)
    except Exception:
        pass

    if radii_kept:
        summary["min_slice_radius"] = min(radii_kept)
        summary["max_slice_radius"] = max(radii_kept)
        summary["average_slice_radius"] = sum(radii_kept) / len(radii_kept)
    summary["slice_particle_summary"] = dict(summary)

    if _coerce_bool(slice_cfg.get("debug_export_gizmos"), False):
        summary["particles"] = particle_logs
        if output_path is not None:
            dbg = output_path.parent / f"{output_path.stem}_slice_debug.json"
            write_slice_debug_json(dbg, summary, frame)

    print(
        f"fatia pseudo-2d: leito/tampas cortados; "
        f"{n_slice_parts} discos (espessura={thickness:.4f} m, eixo={axis}), "
        f"{n_full_parts} particulas 3d fora, "
        f"snap_parede={summary.get('n_snapped_to_wall', 0)}, "
        f"fora_plano_fatia={summary.get('n_dropped_policy', 0)}"
    )
    return summary


def _salvar_relatorio_packing(output_path: Path, relatorio: dict):
    # grava metricas de empacotamento ao lado do arquivo blend pedido
    # o nome segue o stem do blend mais sufixo packing report
    try:
        p = output_path.parent / f"{output_path.stem}_packing_report.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        print(f"relatorio de empacotamento: {p}")
    except Exception as e:
        print(f"aviso: nao foi possivel salvar relatorio json: {e}")


def _remove_particle_objects(*, include_slice_discs: bool = False) -> int:
    """
    remove malhas de partículas 3d após boolean no núcleo (modo solid_internal_cylinder_with_particle_holes).
    mantém slice_disc_* (representação 2d) salvo include_slice_discs=True.
    """
    removed = 0
    for obj in list(bpy.data.objects):
        if obj.type != "MESH":
            continue
        low = obj.name.lower()
        if low.startswith("boolean_tool_"):
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
                removed += 1
            except Exception:
                pass
            continue
        if low.startswith("particula"):
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
                removed += 1
            except Exception:
                pass
            continue
        if include_slice_discs and low.startswith("slice_disc_"):
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
                removed += 1
            except Exception:
                pass
    return removed


def _finalize_solid_core_with_holes(
    nucleo: Any,
    centers: List[Tuple[float, float, float]],
    *,
    particle_diameter: float,
    particle_kind: str,
) -> Tuple[str, List[str], int]:
    """aplica furos no cilindro interno e garante que malhas de partícula foram removidas."""
    pstat, pw, n_applied = punch_core_with_particle_tools(
        nucleo,
        centers,
        particle_diameter,
        particle_kind,
        max_tools=None,
    )
    removed = _remove_particle_objects()
    if removed:
        print(f"particulas/ferramentas removidas apos boolean: {removed}")
    return pstat, pw, n_applied


def _prepare_export_visibility(params: dict) -> None:
    """remove ferramentas booleanas e particulas ocultas conforme bed.visibility."""
    try:
        _pm = Path(__file__).resolve().parents[1] / "python_modeling"
        if str(_pm) not in sys.path:
            sys.path.insert(0, str(_pm))
        from bed_internal_modes import (  # noqa: E402
            MODE_SOLID_HOLES,
            resolve_bed_internal_config,
        )

        mode, vis, _ = resolve_bed_internal_config(params)
    except Exception:
        return
    if mode == MODE_SOLID_HOLES or not vis.get("show_particles", True):
        n = _remove_particle_objects()
        if n:
            print(f"particulas removidas da cena/export: {n}")
    if vis.get("export_boolean_tools", False):
        return
    for obj in list(bpy.data.objects):
        if obj.name.startswith("boolean_tool_"):
            bpy.data.objects.remove(obj, do_unlink=True)


def export_formats_from_params(params: dict, default: str = "blend") -> str:
    """mapeia export.formats do json para lista cli (stl_binary -> stl)."""
    exp = params.get("export") if isinstance(params, dict) else None
    if not isinstance(exp, dict):
        return default
    raw = exp.get("formats")
    tokens: List[str] = []
    if isinstance(raw, list):
        for item in raw:
            s = str(item).strip().lower()
            if s in ("stl_binary", "stl"):
                tokens.append("stl")
            elif s in ("blend", "obj", "gltf", "glb", "fbx"):
                tokens.append(s)
    elif isinstance(raw, str) and raw.strip():
        for part in raw.split(","):
            s = part.strip().lower()
            if s in ("stl_binary", "stl"):
                tokens.append("stl")
            elif s:
                tokens.append(s)
    return ",".join(dict.fromkeys(tokens)) if tokens else default


def export_outputs(args, output_path: Path, *, formats_override: Optional[str] = None):
    # centraliza exportacao para nao repetir o mesmo codigo em cada ramo do main
    print(f"\nsalvando arquivo em: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fmt_raw = formats_override if formats_override is not None else getattr(args, "formats", "blend")
    if isinstance(fmt_raw, list):
        fmt_raw = ",".join(str(x) for x in fmt_raw)
    formats = [f.strip().lower() for f in str(fmt_raw).split(",") if f.strip()]
    print(f"formatos selecionados: {', '.join(formats)}")
    # cada bloco abaixo tenta exportar e imprime erro sem derrubar o script inteiro
    # se o destino for .blend, gravar sempre o ficheiro principal (json pode pedir so stl/obj)
    save_blend = "blend" in formats or output_path.suffix.lower() == ".blend"
    if save_blend:
        try:
            bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
            print(f"arquivo .blend salvo: {output_path}")
        except Exception as e:
            print(f"erro ao salvar .blend: {e}")
    if "gltf" in formats:
        try:
            gltf_path = output_path.with_suffix(".gltf")
            bpy.ops.export_scene.gltf(
                filepath=str(gltf_path),
                export_format="GLTF_SEPARATE",
                export_apply=True,
                export_yup=True,
                export_lights=True,
                export_extras=True,
            )
            print(f"arquivo .gltf exportado: {gltf_path}")
        except Exception as e:
            print(f"erro ao exportar .gltf: {e}")
    if "glb" in formats:
        try:
            glb_path = output_path.with_suffix(".glb")
            bpy.ops.export_scene.gltf(
                filepath=str(glb_path),
                export_format="GLB",
                export_apply=True,
                export_yup=True,
                export_lights=True,
                export_extras=True,
            )
            print(f"arquivo .glb exportado: {glb_path}")
        except Exception as e:
            print(f"erro ao exportar .glb: {e}")
    if "obj" in formats:
        try:
            obj_path = output_path.with_suffix(".obj")
            bpy.ops.wm.obj_export(
                filepath=str(obj_path),
                export_selected_objects=False,
                apply_modifiers=True,
                export_normals=True,
                export_uv=True,
                export_materials=True,
            )
            print(f"arquivo .obj exportado: {obj_path}")
        except Exception as e:
            print(f"erro ao exportar .obj: {e}")
    if "fbx" in formats:
        try:
            fbx_path = output_path.with_suffix(".fbx")
            bpy.ops.export_scene.fbx(
                filepath=str(fbx_path),
                use_selection=False,
                apply_scale_options="FBX_SCALE_ALL",
                axis_forward="-Z",
                axis_up="Y",
                apply_unit_scale=True,
                mesh_smooth_type="FACE",
            )
            print(f"arquivo .fbx exportado: {fbx_path}")
        except Exception as e:
            print(f"erro ao exportar .fbx: {e}")
    if "stl" in formats:
        try:
            stl_path = output_path.with_suffix(".stl")
            # blender 4.0.x: wm.stl_export pode nao existir; export_mesh.stl e o operador estavel
            try:
                bpy.ops.wm.stl_export(
                    filepath=str(stl_path),
                    export_selected_objects=False,
                    apply_modifiers=True,
                    ascii_format=False,
                )
            except Exception:
                bpy.ops.export_mesh.stl(
                    filepath=str(stl_path),
                    check_existing=False,
                    use_selection=False,
                    use_mesh_modifiers=True,
                    ascii=False,
                    global_scale=1.0,
                )
            print(f"arquivo .stl exportado: {stl_path}")
        except Exception as e:
            print(f"erro ao exportar .stl: {e}")
    print(f"\nexportacao concluida {len(formats)} formato(s) processado(s)")


def write_export_sidecar_json(
    output_path: Path,
    params: dict,
    *,
    slice_summary: Optional[Dict[str, Any]] = None,
    full_3d_companion: Optional[str] = None,
) -> None:
    """grava {stem}_pure_bed.json junto ao blend/stl para o viewer web."""
    try:
        _pm = Path(__file__).resolve().parents[1] / "python_modeling"
        if str(_pm) not in sys.path:
            sys.path.insert(0, str(_pm))
        from geometry_modes import geometry_mode_from_data, resolve_slice_config  # noqa: E402
    except ImportError:
        geometry_mode_from_data = lambda _p: str(params.get("geometry_mode") or "")  # type: ignore
        resolve_slice_config = lambda _p: {}  # type: ignore

    gm = geometry_mode_from_data(params)
    payload: Dict[str, Any] = {
        "geometry_mode": gm,
        "generation_backend": str(params.get("generation_backend") or "blender"),
        "packing_method": str(
            (params.get("packing") or {}).get("method")
            or params.get("packing_mode")
            or ""
        ),
    }
    sl = resolve_slice_config(params)
    if sl:
        payload["slice"] = sl
    if full_3d_companion:
        payload["full_3d_companion"] = full_3d_companion
    if slice_summary:
        payload["slice_particle_summary"] = slice_summary
        for k in (
            "slice_axis",
            "slice_position",
            "slice_thickness",
            "n_kept",
            "min_slice_radius",
            "max_slice_radius",
        ):
            if k in slice_summary and slice_summary[k] is not None:
                payload[k] = slice_summary[k]
    out_json = output_path.parent / f"{output_path.stem}_pure_bed.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    stl_sibling = output_path.parent / f"{output_path.stem}.stl"
    mesh_for_hash = stl_sibling if stl_sibling.is_file() else None
    try:
        _repo = Path(__file__).resolve().parents[2]
        if str(_repo) not in sys.path:
            sys.path.insert(0, str(_repo))
        from bedflow_export_metadata import enrich_export_metadata  # noqa: E402

        payload = enrich_export_metadata(
            payload,
            bed_data=params if isinstance(params, dict) else {},
            modeling_profile="blender",
            job_id=os.environ.get("BEDFLOW_JOB_ID"),
            mesh_path=mesh_for_hash,
        )
    except ImportError:
        pass
    with out_json.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2, ensure_ascii=False)
    print(f"sidecar metadata: {out_json}")


def export_full3d_companion(args, output_path: Path, params: dict) -> Optional[str]:
    """exporta o leito 3d completo da cena atual (antes do corte) como arquivo irmao.

    o boolean intersect de aplicar_thin_slice destroi o modelo 3d in-place; chamada
    aqui, antes do corte, grava <stem>_full3d.blend + .stl e o json lateral para
    permitir validar visualmente a fatia 2d. devolve o nome do .stl companheiro.
    """
    try:
        _pm = Path(__file__).resolve().parents[1] / "python_modeling"
        if str(_pm) not in sys.path:
            sys.path.insert(0, str(_pm))
        from full3d_companion import (  # noqa: E402
            full3d_companion_metadata,
            full3d_path_for,
            full3d_sidecar_path_for,
        )
    except ImportError as exc:
        print(f"aviso: full3d_companion indisponivel, 3d nao preservado: {exc}")
        return None

    full3d_blend = full3d_path_for(output_path, ".blend")
    full3d_stl = full3d_path_for(output_path, ".stl")
    print(f"\npreservando modelo 3d completo (validacao do corte): {full3d_blend}")
    # exporta a cena inteira (leito + tampas + particulas) sem podar visibilidade
    export_outputs(args, full3d_blend, formats_override="blend,stl")
    try:
        meta = full3d_companion_metadata(
            companion_of=output_path,
            generation_backend=str(params.get("generation_backend") or "blender"),
        )
        sidecar = full3d_sidecar_path_for(full3d_blend)
        sidecar.write_text(
            json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"sidecar 3d completo: {sidecar}")
    except OSError as exc:
        print(f"aviso: falha ao gravar sidecar 3d completo: {exc}")
    return full3d_stl.name


def main_com_parametros():
    # ponto de entrada quando o blender chama python leito_extracao py depois de --
    # fluxo resumido
    # passo 1 ler json com bed particles lids packing
    # passo 2 descobrir packing method rigid body ou modos cientificos
    # passo 3 limpar cena e criar geometria
    # passo 4 se cientifico gera centros valida e cria esferas sem fisica
    # passo 5 se rigid body usa fisica antiga com bake
    # passo 6 exportar formatos pedidos
    argv = sys.argv
    if '--' in argv:
        argv = argv[argv.index('--') + 1:]
    else:
        # se nao houver argumentos, usar valores padrao
        print("executando com parametros padrao...")
        main()
        return
    
    # criar parser de argumentos
    parser = argparse.ArgumentParser(description='gerar leito empacotado no blender')
    parser.add_argument('--params', type=str, help='caminho do arquivo json com parametros')
    parser.add_argument('--output', type=str, help='caminho do arquivo de saida .blend')
    parser.add_argument('--formats', type=str, default='blend,gltf,glb', 
                        help='formatos de exportacao separados por virgula (blend,gltf,glb,obj,fbx,stl)')
    
    try:
        args = parser.parse_args(argv)
    except:
        # se falhar ao processar argumentos, usar padrao
        print("erro ao processar argumentos, usando padrao...")
        main()
        return
    
    # sem arquivo json voltamos ao demo interno main que usa numeros fixos no codigo
    if not args.params:
        print("sem --params json executando main padrao...")
        main()
        return

    params = ler_parametros_json(args.params)
    if not params:
        print("falha ao ler json executando main padrao...")
        main()
        return

    # cada secao do json alimenta um pedaco do modelo
    bed_raw = params.get("bed") or {}
    particles_raw = params.get("particles") or {}
    lids_raw = params.get("lids") or {}
    packing_raw = params.get("packing") or {}
    slice_cfg = params.get("slice") if isinstance(params, dict) else None
    if not isinstance(slice_cfg, dict):
        slice_cfg = {}

    # geometria do tubo e particulas com defaults seguros se faltar chave
    altura = _coerce_float(bed_raw.get("height"), 0.1)
    diametro = _coerce_float(bed_raw.get("diameter"), 0.05)
    espessura = _coerce_float(bed_raw.get("wall_thickness"), 0.002)
    num_particulas = _coerce_int(particles_raw.get("count"), 100)
    diametro_particula = _coerce_float(particles_raw.get("diameter"), 0.005)
    particle_kind = str(particles_raw.get("kind") or "sphere").strip().lower()
    esp_tampa_inf = _coerce_float(lids_raw.get("bottom_thickness"), 0.003)
    esp_tampa_sup = _coerce_float(lids_raw.get("top_thickness"), 0.003)

    print("parametros do json:")
    print(f"  altura: {altura}m")
    print(f"  diametro: {diametro}m")
    print(f"  espessura parede: {espessura}m")
    print(f"  particulas: {num_particulas}")
    print(f"  tipo particula: {particle_kind}")
    print(f"  diametro particula: {diametro_particula}m")

    metodo = _packing_method_name(packing_raw)
    print(f"  metodo empacotamento: {metodo}")

    def _log_particle_plural(k: str) -> str:
        return {"sphere": "esferas", "cube": "cubos", "cylinder": "cilindros"}.get(
            (k or "sphere").lower(), "particulas"
        )

    try:
        limpar_cena()

        # centros do packing cientifico para fatia 2d (evita depender de matrix_world)
        centers_for_slice: Optional[List[Tuple[float, float, float]]] = None

        # raios usados igual no ramo cientifico e no ramo fisico para coerencia
        raio_ext = diametro / 2.0
        raio_int = raio_ext - espessura
        raio_equiv = collision_radius_for_particle_kind(particle_kind, diametro_particula)
        # gap explicito vence se nao existir usamos collision margin do packing fisico antigo
        if packing_raw.get("gap") is not None:
            gap = _coerce_float(packing_raw.get("gap"), 0.0)
        else:
            gap = _coerce_float(packing_raw.get("collision_margin"), 0.0)

        # ramo cientifico spherical packing ou hexagonal tres d
        # diferente do rigid body nao ha queda nem bake de fisica blender
        # passos mentais ler parametros montar domain igual ao pure generation
        # chamar generate spherical packing ou generate hexagonal packing
        # validate configuration confere pares e dominio com a mesma matematica python
        # depois create hollow cylinder create caps e create_particles_by_kind materializam na cena
        # gap e distancia extra entre superficies exigida entre centros usamos sphere center clearance no gerador
        if metodo in ("spherical_packing", "hexagonal_3d"):
            # aqui nao rodamos rigid body nem bake porque as posicoes ja sao finais
            print("modo cientifico: sem simulacao fisica rigid body")

            # domain encapsula todas as desigualdades geometricas em um so objeto
            domain = AnnulusBedDomain(
                r_int=raio_int,
                r_ext=raio_ext,
                height=altura,
                bottom_cap_thickness=esp_tampa_inf,
                top_cap_thickness=esp_tampa_sup,
                r_sphere=raio_equiv,
                gap=gap,
            )

            # mede tempo de cpu do gerador para comparar metodos no relatorio
            t0_gen = time.perf_counter()
            from packed_bed_science.packing_seed import resolve_packing_random_seed  # noqa: E402

            seed_i, seed_auto = resolve_packing_random_seed(
                packing_raw, particles_raw
            )
            if metodo == "spherical_packing":
                max_att = _coerce_int(packing_raw.get("max_placement_attempts"), 500_000)
                gen = generate_spherical_packing(
                    domain,
                    num_particulas,
                    raio_equiv,
                    gap,
                    random_seed=seed_i,
                    max_placement_attempts=max_att,
                )
            else:
                step_x_opt = packing_raw.get("step_x")
                step_x_f = (
                    _coerce_float(step_x_opt, 0.0)
                    if step_x_opt is not None
                    else None
                )
                if step_x_f is not None and step_x_f <= 0:
                    step_x_f = None
                gen = generate_hexagonal_packing(
                    domain,
                    num_particulas,
                    raio_equiv,
                    gap,
                    step_x=step_x_f,
                    random_seed=seed_i,
                )
            gen["packing_random_seed"] = seed_i
            gen["packing_seed_auto"] = seed_auto
            t_gen = time.perf_counter() - t0_gen
            centers = gen["centers"]
            centers_for_slice = list(centers)
            # lista de raios repetidos prepara validacao para futuro raio variavel
            radii = [raio_equiv] * len(centers)

            # strict true faz o script levantar erro se geometria invalida ou faltar esferas no modo esferico
            strict = _coerce_bool(packing_raw.get("strict_validation"), True)
            # validate configuration percorre pares e checa point in domain de novo
            report_val = validate_configuration(centers, radii, domain, gap)

            poros = estimate_porosity(domain, centers, raio_equiv)
            # dicionario serializado no json lateral sem incluir a lista enorme de centros duas vezes
            relatorio = {
                "packing_method": metodo,
                "particle_kind": particle_kind,
                "collision_model": "circumscribed_sphere_radius",
                "collision_radius_m": raio_equiv,
                "generation": {k: v for k, v in gen.items() if k != "centers"},
                "generation_wall_time_sec": t_gen,
                "gap_convention": "center_distance >= r1+r2+gap",
                "validation": report_val,
                "porosity_estimate": poros,
                "annulus_void_volume_m3": domain.annulus_volume_void(),
                "n_particles_placed": len(centers),
                "n_particles_requested": num_particulas,
                "n_spheres_placed": len(centers),
                "n_spheres_requested": num_particulas,
            }

            if args.output:
                _salvar_relatorio_packing(Path(args.output), relatorio)

            # falhas de dominio ou par colidente disparam erro opcional
            if report_val["ok"] is not True:
                print("validacao geometrica falhou:", report_val["messages"][:10])
                if strict:
                    raise RuntimeError("strict_validation true e configuracao invalida")

            if metodo == "spherical_packing" and len(centers) < num_particulas:
                msg = f"spherical_packing colocou apenas {len(centers)}/{num_particulas}"
                print("aviso:", msg)
                if strict:
                    raise RuntimeError(msg)

            if metodo == "hexagonal_3d" and len(centers) < num_particulas:
                print(
                    "aviso hexagonal_3d: pontos validos",
                    len(centers),
                    "menor que solicitado",
                    num_particulas,
                )

            _pm = Path(__file__).resolve().parents[1] / "python_modeling"
            if str(_pm) not in sys.path:
                sys.path.insert(0, str(_pm))
            from bed_internal_modes import (  # noqa: E402
                MODE_SOLID_HOLES,
                bed_internal_sidecar,
                resolve_bed_internal_config,
            )

            internal_mode, vis, _ = resolve_bed_internal_config(params)
            if internal_mode == MODE_SOLID_HOLES:
                vis["show_particles"] = False
            print(f"modo cilindro interno: {internal_mode}")

            print("criando geometria leito e tampas")
            leito, nucleo, bed_partial = create_bed_by_internal_mode(
                internal_mode, raio_ext, raio_int, altura, vis,
                bottom_cap=esp_tampa_inf, top_cap=esp_tampa_sup,
            )
            tampa_inferior, tampa_superior = create_caps(
                altura,
                diametro,
                esp_tampa_inf,
                esp_tampa_sup,
                top_has_collision=True,
            )
            bool_status = dict(bed_partial)
            bool_warnings: List[str] = []
            if internal_mode == MODE_SOLID_HOLES and nucleo is not None:
                print(
                    f"nucleo solido: aplicando boolean difference em {len(centers)} posicoes"
                )
                pstat, pw, n_holes = _finalize_solid_core_with_holes(
                    nucleo,
                    centers,
                    particle_diameter=diametro_particula,
                    particle_kind=particle_kind,
                )
                bool_status["particle_tools"] = pstat
                bool_status["n_holes_applied"] = n_holes
                bool_warnings.extend(pw)
            elif internal_mode == MODE_SOLID_HOLES:
                bool_status["particle_tools"] = "skipped"

            _plural = _log_particle_plural(particle_kind)
            if internal_mode == MODE_SOLID_HOLES:
                print(
                    f"{_plural}: furos no nucleo ({len(centers)} posicoes); malhas nao exportadas"
                )
                particulas = []
            elif vis.get("show_particles", True):
                print(f"{_plural}: {len(centers)} malhas mesh compartilhada")
                particulas = create_particles_by_kind(
                    particle_kind, centers, diametro_particula
                )
            else:
                print("particulas omitidas (show_particles=false)")
                particulas = []

            sidecar = bed_internal_sidecar(
                params,
                backend="blender",
                status={
                    **bool_status,
                    "backend": "blender",
                    "warnings": bool_warnings,
                    "r_int": raio_int,
                    "r_ext": raio_ext,
                },
            )
            relatorio["internal_cylinder_mode"] = sidecar["internal_cylinder_mode"]
            relatorio["visibility"] = sidecar["visibility"]
            relatorio["boolean_operation_status"] = sidecar["boolean_operation_status"]
            print(
                "boolean_operation_status:",
                relatorio["boolean_operation_status"],
            )

        else:
            # fluxo legado com corpos rigidos para quem ainda quer queda e bake
            _pm = Path(__file__).resolve().parents[1] / "python_modeling"
            if str(_pm) not in sys.path:
                sys.path.insert(0, str(_pm))
            try:
                from bed_internal_modes import resolve_bed_internal_config  # noqa: E402

                _icm, _, _ = resolve_bed_internal_config(params)
                if _icm != "hollow_boolean_applied":
                    print(
                        "aviso: internal_cylinder_mode",
                        _icm,
                        "ignorado no fluxo rigid_body (usa criar_cilindro_oco legado)",
                    )
            except ImportError:
                pass
            print("criando geometria fluxo rigid_body")
            leito = criar_cilindro_oco(altura, diametro, espessura)
            print(f"leito criado: altura={altura}m, diametro={diametro}m")

            tampa_inferior = criar_tampa(
                posicao_z=0,
                diametro=diametro,
                espessura=esp_tampa_inf,
                nome="tampa_inferior",
                tem_colisao=True,
            )
            print("tampa inferior criada com colisao")

            tampa_superior = criar_tampa(
                posicao_z=altura,
                diametro=diametro,
                espessura=esp_tampa_sup,
                nome="tampa_superior",
                tem_colisao=True,
            )
            print("tampa superior com colisao alinhada a inferior leito fechado")

            # criar particulas antigas sorteia posicoes acima do leito para a gravidade puxar
            raio_leito = raio_int
            particulas = criar_particulas(
                quantidade=num_particulas,
                raio_leito=raio_leito,
                altura_leito=altura,
                raio_particula=diametro_particula / 2.0,
                kind=particle_kind,
                diametro_particula=diametro_particula,
            )
            print(f"{len(particulas)} particulas criadas")

            print("configurando fisica")
            configurar_simulacao_fisica()

            print("aplicando fisica ao leito")
            aplicar_fisica(leito, eh_movel=False)

            print("aplicando fisica as tampas")
            aplicar_fisica(tampa_inferior, eh_movel=False)
            aplicar_fisica(tampa_superior, eh_movel=False)

            print("aplicando fisica as particulas")
            for i, particula in enumerate(particulas):
                aplicar_fisica(particula, eh_movel=True)
                if (i + 1) % 20 == 0:
                    print(f"  {i + 1}/{num_particulas} particulas processadas")

            print("fisica aplicada a todas as particulas")

            tempo_sim = _coerce_float(packing_raw.get("max_time"), 20.0)
            gravidade = _coerce_float(packing_raw.get("gravity"), -9.81)
            substeps = _coerce_int(packing_raw.get("substeps"), 10)
            iterations = _coerce_int(packing_raw.get("iterations"), 10)

            print("\nreconfigurando fisica com parametros do arquivo")
            print(f"  gravidade: {gravidade} m/s2")
            print(f"  tempo simulacao: {tempo_sim}s")
            print(f"  substeps: {substeps}")
            print(f"  iterations: {iterations}")

            configurar_simulacao_fisica(
                gravidade=gravidade, substeps=substeps, iterations=iterations
            )

            sep = "=" * 60
            print(f"\n{sep}")
            print("  executando animacao de fisica")
            print(f"{sep}")
            print(f"tempo de simulacao: {tempo_sim}s")
            print("fps: 24")
            print(f"total de frames: {int(tempo_sim * 24)}")
            print("\naguarde particulas caindo no leito")
            print("pode levar minutos conforme quantidade\n")

            executar_simulacao_fisica(tempo_simulacao=tempo_sim, fps=24)

            print(f"\n{sep}")
            print("  congelando posicoes finais")
            print(f"{sep}")
            fazer_bake_fisica(particulas)

            print(f"\n{sep}")
            print("  animacao completa")
            print(f"{sep}")
            print("particulas acomodadas bake aplicado pronto exportacao\n")

        # aplicar thin slice no fim (ambos os ramos ja criaram os meshes)
        try:
            _pm = Path(__file__).resolve().parents[1] / "python_modeling"
            if str(_pm) not in sys.path:
                sys.path.insert(0, str(_pm))
            from geometry_modes import (
                GEOMETRY_STATISTICAL,
                GEOMETRY_THIN_SLICE,
                geometry_mode_from_data,
                resolve_slice_config,
            )

            gm = geometry_mode_from_data(params)
            if gm == GEOMETRY_STATISTICAL:
                raise RuntimeError(
                    "pseudo_2d_statistical requer generation_backend python_engine; "
                    "use packed_bed_stl.py ou escolha python_engine no wizard."
                )
            resolved_slice = resolve_slice_config(params)
            if resolved_slice:
                slice_cfg = resolved_slice
            elif gm != GEOMETRY_THIN_SLICE:
                slice_cfg = {}
        except RuntimeError:
            raise
        except Exception:
            pass
        slice_summary_export: Dict[str, Any] = {}
        full3d_companion_name: Optional[str] = None
        if isinstance(slice_cfg, dict) and slice_cfg.get("slice_enabled"):
            # preserva o 3d completo ANTES do corte (o boolean intersect o destroi)
            try:
                _pm_f3d = Path(__file__).resolve().parents[1] / "python_modeling"
                if str(_pm_f3d) not in sys.path:
                    sys.path.insert(0, str(_pm_f3d))
                from full3d_companion import preserve_full_3d_enabled  # noqa: E402

                if args.output and preserve_full_3d_enabled(slice_cfg):
                    full3d_companion_name = export_full3d_companion(
                        args, Path(args.output), params
                    )
            except Exception as e:
                print(f"aviso: falha ao preservar modelo 3d completo: {e}")
            slice_summary_export = aplicar_thin_slice(
                slice_cfg,
                altura=altura,
                raio_ext=raio_ext,
                raio_int=raio_int,
                particle_centers=centers_for_slice,
                particle_diameter=diametro_particula,
                particle_kind=particle_kind,
                bottom_cap=esp_tampa_inf,
                top_cap=esp_tampa_sup,
                output_path=Path(args.output) if args.output else None,
            ) or {}

        try:
            _pm_ic = Path(__file__).resolve().parents[1] / "python_modeling"
            if str(_pm_ic) not in sys.path:
                sys.path.insert(0, str(_pm_ic))
            from bed_internal_modes import (  # noqa: E402
                MODE_SOLID_HOLES as _MODE_SOLID,
                resolve_bed_internal_config as _resolve_icm,
            )

            _icm_post, _, _ = _resolve_icm(params)
            if _icm_post == _MODE_SOLID:
                _remove_particle_objects()
        except Exception:
            pass

        # ambos os ramos chegam aqui com objetos na cena prontos para salvar
        if args.output:
            _prepare_export_visibility(params)
            fmt_cli = export_formats_from_params(params, getattr(args, "formats", "blend,stl,obj"))
            out_p = Path(args.output)
            export_outputs(args, out_p, formats_override=fmt_cli)
            write_export_sidecar_json(
                out_p,
                params,
                slice_summary=slice_summary_export or None,
                full_3d_companion=full3d_companion_name,
            )
        else:
            print("\naviso caminho saida nao especificado arquivo nao salvo")

        print("\nmodelo 3d gerado com sucesso!")

        
    except Exception as e:
        print(f"\nerro ao gerar modelo: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main_com_parametros()
# =========================================================================================

