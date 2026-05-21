# nucleo de geracao geometrica stl em python puro
# o ficheiro packed bed stl chama este modulo depois de validar o json
#
# ha dois grandes caminhos conforme o campo packing method no ficheiro json
# caminho um chamado cientifico usa spherical packing ou hexagonal 3d
# caminho dois chamado legacy usa rigid body com simulacao de queda
#
# no caminho cientifico nao ha motor fisico blender dentro deste ficheiro
# as posicoes das esferas vem de funcoes em packed bed science
# depois pure bed mesh constroi o cilindro tampas e particulas como malha triangular
# no fim exportamos stl binario e um json lateral com metadados
#
# o dominio geometrico chama se annulus bed domain
# ele descreve o anel entre raio interno e externo e a faixa vertical entre tampas
# validate configuration verifica se cada centro respeita paredes e se pares nao colidem
#
# modo spherical packing em palavras simples
# imagina lancar pontos aleatorios dentro do volume permitido
# cada novo ponto so fica se estiver longe o suficiente dos anteriores
# longe significa distancia entre centros maior ou igual a soma dos raios mais gap
# se falhar muitas vezes seguidas o algoritmo pode parar antes do numero pedido
#
# modo hexagonal 3d em palavras simples
# imagina uma grade regular tipo favo cortada pelo cilindro
# os centros validos sao os nos da grade que caem dentro do dominio
# o passo horizontal opcional step x mexe na densidade horizontal da grade
#
# integracao backend
# quando o utilizador escolhe motor python no api o servico corre este script
# quando escolhe blender outro caminho usa leito extracao dentro do blender
#
from __future__ import annotations

import json
import sys
import time
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

# diretorio deste ficheiro serve para imports relativos sem instalar pacote
_PMDIR = Path(__file__).resolve().parent
if str(_PMDIR) not in sys.path:
    sys.path.insert(0, str(_PMDIR))

# raiz do repositorio sobe dois niveis a partir de scripts python modeling
_ROOT = Path(__file__).resolve().parents[2]
# ferramenta opcional de visualizacao noutra pasta
_VIS_CIL = _ROOT / "tools" / "vis_cilindro"
if str(_VIS_CIL) not in sys.path:
    sys.path.insert(0, str(_VIS_CIL))

# pasta scripts contem o pacote packed bed science como codigo fonte local
_SCRIPTS = Path(__file__).resolve().parents[1]
_BLENDER_SCRIPTS_DIR = _SCRIPTS / "blender_scripts"
if str(_BLENDER_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_BLENDER_SCRIPTS_DIR))

from modelo_cilindro import (  # noqa: E402
    gera_malha_tubo_com_tampas,
    mesh,
    params_cilindro,
    params_particulas,
    simula_ate_tampa_fechar,
)

from packed_bed_science.geometry_math import (  # noqa: E402
    AnnulusBedDomain,
    collision_radius_for_particle_kind,
)
from packed_bed_science.packing_hexagonal import generate_hexagonal_packing  # noqa: E402
from packed_bed_science.packing_modes import (  # noqa: E402
    merge_root_packing_mode,
    packing_method_from_section,
)
from packed_bed_science.packing_spherical import generate_spherical_packing  # noqa: E402
from packed_bed_science.validation import validate_configuration  # noqa: E402

from bed_config import (  # noqa: E402
    merge_root_generation_backend,
    normalize_generation_backend,
    resolve_bed_geometry_numbers,
)
from geometry_modes import (  # noqa: E402
    GEOMETRY_STATISTICAL,
    geometry_mode_from_data,
    resolve_slice_config,
    resolve_statistical_config,
)
from pseudo_2d_statistical import generate_statistical_thin_3d_stl  # noqa: E402
from pure_bed_mesh import build_packed_bed_model, export_model_data  # noqa: E402
from stl_mesh_utils import (  # noqa: E402
    box_mesh,
    cylinder_axis,
    merge_mesh,
    uv_sphere,
    write_stl_binary,
)
from thin_slice_build import apply_thin_slice_mesh, slice_cfg_active  # noqa: E402

# alias de tipo para tripla de floats xyz
vec3 = Tuple[float, float, float]
# alias de tipo para triangulo como tres indices
tri = Tuple[int, int, int]


def _to_float(v: Any, default: float = 0.0) -> float:
    # converte entrada solta do json para float seguro
    # v e o valor bruto que pode ser none numero ou texto
    # default e o numero de recurso quando v e invalido ou none
    # passo um none devolve default
    # passo dois tipos numericos nativos viram float direto
    # passo tres texto limpa virgula europeia e chama float de novo
    # isto evita falhas quando o wizard grava numeros como string
    if v is None:
        return float(default)
    if isinstance(v, (int, float)):
        return float(v)
    return float(str(v).replace(",", "."))


def _to_int(v: Any, default: int = 0) -> int:
    # igual ao float mas o resultado final e inteiro
    # contagens e seeds devem ser inteiros para os geradores
    if v is None:
        return int(default)
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return int(v)
    return int(float(str(v).replace(",", ".")))


def _packing_method_name(packing: Dict[str, Any]) -> str:
    return packing_method_from_section(packing)


def _coerce_bool(v: Any, default: bool = True) -> bool:
    # strict validation e outros flags chegam como texto ou booleano
    # normalizamos para nao depender do tipo exato vindo do json
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


def load_bed_json(path: Path) -> Dict[str, Any]:
    # le o ficheiro json e devolve um dicionario unico com chaves fixas
    # path e o caminho para o ficheiro gerado pelo wizard ou editado a mao
    # o objetivo e esconder a estrutura aninhada do json do resto do codigo
    # aplicamos merge de packing e generation no topo antes de ler seccoes
    # resolve bed geometry numbers aceita diameter ou r outer r inner
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        merge_root_packing_mode(data)
        merge_root_generation_backend(data)
    bed = dict(data.get("bed") or {})
    particles = data.get("particles") or {}
    lids = data.get("lids") or {}
    packing = data.get("packing") or {}

    # diameter altura e parede ja normalizados em metros
    diameter, height, wall = resolve_bed_geometry_numbers(bed)

    # count numero pedido de particulas pode vir como string
    count = particles.get("count", 100)
    # particle count final e usado pelos algoritmos de distribuicao
    count_i = _to_int(count, 100)

    # diametro da particula esferica
    pd = particles.get("diameter", 0.005)
    # particle diameter e o diametro fisico da esfera
    # depois o algoritmo converte para raio para o dominio
    particle_d = _to_float(pd, 0.005)

    # gravidade usada so no modo legacy rigid body
    grav = packing.get("gravity", -9.81)
    grav_f = _to_float(grav, -9.81)

    # espessuras fisicas das tampas inferior e superior
    bottom_t = _to_float(lids.get("bottom_thickness"), 0.003)
    top_t = _to_float(lids.get("top_thickness"), 0.003)

    # gap e folga minima entre superficies de duas particulas vizinhas (modos cientificos)
    # o dominio usa raio equivalente circumscribed sphere para colisao
    gap = packing.get("gap")
    if gap is not None:
        gap_f = _to_float(gap, 0.0)
    else:
        gap_f = _to_float(packing.get("collision_margin"), 0.0)
    # gap e o valor que define a folga minima entre particulas
    # ele entra tanto na geracao como na validacao

    gm = geometry_mode_from_data(data) if isinstance(data, dict) else "full_3d"
    slice_cfg = resolve_slice_config(data) if isinstance(data, dict) else {}
    stat_cfg = resolve_statistical_config(data) if isinstance(data, dict) else {}

    # chaves abaixo alimentam tanto o modo cientifico como o legacy
    return {
        "diameter": diameter,
        "height": height,
        "wall_thickness": wall,
        "particle_count": max(1, count_i),
        "particle_diameter": particle_d,
        "gravity": grav_f,
        "bottom_thickness": bottom_t,
        "top_thickness": top_t,
        "packing": packing,
        "packing_method": packing_method_from_section(packing),
        "gap": gap_f,
        "random_seed": packing.get("random_seed"),
        "max_placement_attempts": _to_int(packing.get("max_placement_attempts"), 500_000),
        "strict_validation": _coerce_bool(packing.get("strict_validation"), True),
        "step_x": packing.get("step_x"),
        "particles_seed": particles.get("seed"),
        "mesh_segmentos": _to_int(packing.get("mesh_segmentos"), 48),
        "sphere_lat": _to_int(packing.get("sphere_lat"), 4),
        "sphere_lon": _to_int(packing.get("sphere_lon"), 6),
        "generation_backend": normalize_generation_backend(
            data.get("generation_backend") if isinstance(data, dict) else None
        ),
        "geometry_mode": gm,
        "slice": slice_cfg,
        "statistical_2d": stat_cfg,
        "bed": bed,
        "particles": particles if isinstance(particles, dict) else {},
        "particle_kind": str(particles.get("kind") or "sphere").strip().lower(),
    }


def _mesh_to_lists(m: mesh) -> Tuple[List[vec3], List[tri]]:
    # traduz o tipo mesh do modelo cilindro legado para listas python simples
    # vertices sao pontos xyz
    # indices agrupam tres inteiros por triangulo
    return list(m.vertices), list(m.indices)


def _legacy_generate_stl(p: Dict[str, Any], out_stl: Path, max_passos: int) -> None:
    # modo legacy rigid body
    # p e o dicionario devolvido por load bed json
    # out stl e o caminho de escrita do ficheiro final
    # max passos limita o loop da simulacao simples de queda
    # primeiro calculamos raios do tubo e altura
    # depois geramos malha do tubo com tampas
    # depois simulamos particulas ate parar
    # depois validamos com packed bed science se strict pedir
    # por fim fundimos esferas uv ao tubo e escrevemos stl
    r_ext = p["diameter"] / 2.0
    # r int raio interno nunca menor que um pouco mais que raio da particula para nao ficar impossivel
    r_int = max(r_ext - p["wall_thickness"], p["particle_diameter"] * 0.51)
    # altura cilindro
    altura = p["height"]
    pk = str(p.get("particle_kind") or "sphere").strip().lower()
    d_char = float(p["particle_diameter"])
    r_pack = collision_radius_for_particle_kind(pk, d_char)

    # parametros do tubo para malha com tampas incluidas no legacy
    p_cil = params_cilindro(
        raio_externo=r_ext,
        raio_interno=r_int,
        altura=altura,
        segmentos=min(64, max(12, p.get("mesh_segmentos", 48))),
    )
    # parametros das particulas numero raio passos e dt
    p_par = params_particulas(
        num_particulas=p["particle_count"],
        raio_particula=p["particle_diameter"] / 2.0,
        gravidade=p["gravity"],
        dt=0.004,
        max_passos=max_passos,
    )

    t_wall0 = time.perf_counter()
    # gera malha do tubo com tampas como no fluxo antigo
    malha_tubo = gera_malha_tubo_com_tampas(p_cil)
    verts, faces = _mesh_to_lists(malha_tubo)

    # simula ate as particulas pararem ou fechar tampa conforme funcao legacy
    particulas_finais, _ = simula_ate_tampa_fechar(p_cil, p_par)
    # raio esferico igual ao usado na simulacao
    r_s = p_par.raio_particula
    # validacao best effort fisica legacy e aproximada pode haver falsos positivos
    tb = p["bottom_thickness"]
    tt = p["top_thickness"]
    gap_v = p["gap"]
    domain_chk = AnnulusBedDomain(
        r_int=r_int,
        r_ext=r_ext,
        height=altura,
        bottom_cap_thickness=tb,
        top_cap_thickness=tt,
        r_sphere=r_pack,
        gap=gap_v,
    )
    centers_chk = [tuple(part.pos) for part in particulas_finais]
    radii_chk = [r_pack] * len(centers_chk)
    report_legacy = validate_configuration(centers_chk, radii_chk, domain_chk, gap_v)
    if p["strict_validation"] and not report_legacy.get("ok", False):
        raise RuntimeError(
            "validacao pos simulacao rigid body falhou: "
            + str(report_legacy.get("messages", []))[:500]
        )
    centers_legacy = [tuple(part.pos) for part in particulas_finais]
    slice_cfg = resolve_slice_config(p) or dict(p.get("slice") or {})
    slice_sum: Dict[str, Any] = {}
    if slice_cfg_active(slice_cfg):
        dbg_json = None
        if slice_cfg.get("debug_export_gizmos"):
            dbg_json = out_stl.parent / f"{out_stl.stem}_slice_debug.json"
        verts, faces, slice_sum = apply_thin_slice_mesh(
            verts,
            faces,
            centers_legacy,
            particle_diameter=d_char,
            particle_kind=pk,
            r_ext=r_ext,
            r_int=r_int,
            slice_cfg=slice_cfg,
            segmentos=int(p.get("mesh_segmentos", 48)),
            debug_json_path=dbg_json,
        )
    else:
        cyl_seg = max(12, min(32, int(p.get("mesh_segmentos", 48) // 2)))
        for part in particulas_finais:
            x, y, z = part.pos
            if pk == "cube":
                sv, sf = box_mesh(x, y, z, d_char)
            elif pk == "cylinder":
                sv, sf = cylinder_axis(
                    x, y, z, d_char * 0.5, d_char, axis="z", segments=cyl_seg
                )
            else:
                sv, sf = uv_sphere(
                    x, y, z, r_s, lat=p["sphere_lat"], lon=p["sphere_lon"]
                )
            verts, faces = merge_mesh(verts, faces, sv, sf)

    write_stl_binary(out_stl, verts, faces)
    elapsed = time.perf_counter() - t_wall0
    preview_n = 12
    # json lateral para o modo testes rapidos e para inspecao humana sem abrir stl
    # report legacy vem de validate configuration que compara pares e limites do dominio
    slice_summary_legacy = slice_sum if slice_cfg_active(slice_cfg) else {}
    gm_legacy = geometry_mode_from_data(p)
    sidecar: Dict[str, Any] = {
        "geometry_mode": gm_legacy,
        "generation_backend": str(p.get("generation_backend") or "python_engine"),
        "packing_method": "rigid_body",
        "particle_kind": pk,
        "particle_type": pk,
        "collision_model": "circumscribed_sphere",
        "collision_radius_equiv": r_pack,
        "validation": report_legacy,
        "generation_wall_time_sec": elapsed,
        "n_particles_requested": p["particle_count"],
        "n_particles_placed": len(centers_chk),
        "particle_centers_preview": [
            [float(c[0]), float(c[1]), float(c[2])] for c in centers_chk[:preview_n]
        ],
        "particle_centers_histogram": [
            [float(c[0]), float(c[1]), float(c[2])]
            for c in centers_chk[: min(len(centers_chk), 500)]
        ],
        "generation": {
            "mode": "legacy_python_drop",
            "max_passos": max_passos,
            "warning": "sem contacto partícula-partícula; use dem ou rigid_body sem use_legacy_drop",
        },
        "pair_violations": report_legacy.get("pair_violations"),
        "domain_violations": report_legacy.get("domain_violations"),
    }
    if slice_cfg_active(slice_cfg):
        sidecar["slice"] = slice_cfg
    if slice_summary_legacy:
        sidecar["slice_particle_summary"] = slice_summary_legacy
        sidecar["slice_particle_policy"] = slice_cfg.get("slice_particle_policy")
    out_json = out_stl.parent / f"{out_stl.stem}_pure_bed.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as fp:
        json.dump(sidecar, fp, indent=2, ensure_ascii=False)


def _porosity_volume_kind(
    domain: AnnulusBedDomain,
    centers: List[vec3],
    particle_kind: str,
    particle_diameter: float,
) -> float:
    """porosidade por volume de particula real (esfera/cubo/cilindro)."""
    v_void = domain.annulus_volume_void()
    if v_void <= 0:
        return 0.0
    n = len(centers)
    d = float(particle_diameter)
    k = (particle_kind or "sphere").strip().lower()
    if k == "cube":
        v_part = n * d * d * d
    elif k == "cylinder":
        v_part = n * math.pi * (d / 2.0) ** 2 * d
    else:
        v_part = n * (4.0 / 3.0) * math.pi * (d / 2.0) ** 3
    return max(0.0, min(1.0, 1.0 - v_part / v_void))


def _science_generate_stl(p: Dict[str, Any], out_stl: Path) -> None:
    # legado: substituido por engine.pipeline.run_packing + _build_and_export_mesh
    # mantido para referencia; nao e chamado por generate_packed_bed_stl
    # modo cientifico sem fisica tipo blender
    # passo um calcula raios e altura e monta annulus bed domain
    # passo dois escolhe gerador conforme packing method
    # passo tres valida centros e estima porosidade
    # passo quatro constroi malha com pure bed mesh e exporta
    # colisao entre esferas e checagem de paredes usam validate configuration
    # a ideia e distancia entre centros maior ou igual soma raios mais gap
    r_ext = p["diameter"] / 2.0
    # r int raio interno parede menos espessura
    r_int = r_ext - p["wall_thickness"]
    # checagem basica de sanidade antes de continuar
    if r_int <= 0 or r_int >= r_ext:
        raise ValueError("raio interno invalido verifique diameter e wall thickness")
    # altura util
    altura = p["height"]
    pk = str(p.get("particle_kind") or "sphere").strip().lower()
    d_char = float(p["particle_diameter"])
    r_pack = collision_radius_for_particle_kind(pk, d_char)
    # gap copiado do dicionario
    gap = p["gap"]
    # espessuras de tampa inferior e superior
    tb = p["bottom_thickness"]
    tt = p["top_thickness"]

    # domain encapsula limites radiais em xy e limites em z com tampas
    # o pacote packed bed science usa a mesma definicao no blender e aqui
    domain = AnnulusBedDomain(
        r_int=r_int,
        r_ext=r_ext,
        height=altura,
        bottom_cap_thickness=tb,
        top_cap_thickness=tt,
        r_sphere=r_pack,
        gap=gap,
    )

    # method ja veio normalizado pelo loader
    method = p["packing_method"]
    # medimos tempo de cpu para o json lateral
    t0 = time.perf_counter()
    if method == "spherical_packing":
        # ramo spherical packing
        # o gerador interno tenta varias vezes ate aceitar cada centro
        # seed controla repetibilidade dos sorteios
        seed = p.get("random_seed")
        if seed is None:
            seed = p.get("particles_seed")
        # seed none deixa o gerador escolher comportamento proprio
        seed_i = _to_int(seed, 42) if seed is not None else None
        # generate spherical packing devolve dict com centros e estatisticas
        gen = generate_spherical_packing(
            domain,
            p["particle_count"],
            r_pack,
            gap,
            random_seed=seed_i,
            max_placement_attempts=p["max_placement_attempts"],
        )
    else:
        # ramo hexagonal 3d
        # a grade e deterministica e rapida comparada ao sorteio
        # step x controla distancia horizontal entre colunas
        step_x_opt = p.get("step_x")
        step_x_f = _to_float(step_x_opt, 0.0) if step_x_opt is not None else None
        # valor zero ou negativo vira none para automatico
        if step_x_f is not None and step_x_f <= 0:
            step_x_f = None
        # generate hexagonal packing devolve dict parecido ao spherical
        gen = generate_hexagonal_packing(
            domain,
            p["particle_count"],
            r_pack,
            gap,
            step_x=step_x_f,
        )
    # tempo decorrido em segundos
    elapsed = time.perf_counter() - t0

    # centers e lista de tuplos xyz em metros
    centers = gen["centers"]
    radii = [r_pack] * len(centers)
    # validate configuration percorre pares e dominio
    # para cada par compara distancia com soma raios mais gap
    # para cada centro verifica se ainda esta dentro do volume permitido para a esfera inteira
    report_val = validate_configuration(centers, radii, domain, gap)
    # porosidade aproximada por volume
    poros = _porosity_volume_kind(domain, centers, pk, d_char)

    # strict true transforma avisos de validacao em excecao
    strict = p["strict_validation"]
    if not report_val.get("ok", False):
        if strict:
            raise RuntimeError(
                "validacao geometrica falhou: " + str(report_val.get("messages", []))[:500]
            )
    # spherical pode falhar em atingir o numero pedido por esgotar tentativas
    if method == "spherical_packing" and len(centers) < p["particle_count"] and strict:
        raise RuntimeError(
            f"spherical packing so colocou {len(centers)} de {p['particle_count']}"
        )

    # segmentos do cilindro limitados para nao explodir memoria
    seg = min(64, max(12, p.get("mesh_segmentos", 48)))
    slice_cfg = resolve_slice_config(p) or dict(p.get("slice") or {})
    gm = str(p.get("geometry_mode") or "full_3d")
    slice_summary_scientific: Dict[str, Any] = {}
    if not slice_cfg_active(slice_cfg):
        packed = build_packed_bed_model(
            r_ext=r_ext,
            r_int=r_int,
            height=altura,
            bottom_cap_thickness=tb,
            top_cap_thickness=tt,
            particle_centers=centers,
            particle_diameter=d_char,
            particle_kind=pk,
            segmentos_cil=seg,
            lat_sphere=p["sphere_lat"],
            lon_sphere=p["sphere_lon"],
        )
    else:
        shell = build_packed_bed_model(
            r_ext=r_ext,
            r_int=r_int,
            height=altura,
            bottom_cap_thickness=tb,
            top_cap_thickness=tt,
            particle_centers=[],
            particle_diameter=d_char,
            particle_kind=pk,
            segmentos_cil=seg,
            lat_sphere=p["sphere_lat"],
            lon_sphere=p["sphere_lon"],
        )
        dbg_json = None
        if slice_cfg.get("debug_export_gizmos"):
            dbg_json = out_stl.parent / f"{out_stl.stem}_slice_debug.json"
        v_all, f_all, slice_sum = apply_thin_slice_mesh(
            shell.mesh.vertices,
            shell.mesh.faces,
            centers,
            particle_diameter=d_char,
            particle_kind=pk,
            r_ext=r_ext,
            r_int=r_int,
            slice_cfg=slice_cfg,
            segmentos=seg,
            debug_json_path=dbg_json,
        )
        packed = type(shell)(mesh=type(shell.mesh)(vertices=v_all, faces=f_all), meta=shell.meta)  # type: ignore
        slice_summary_scientific = slice_sum

    preview_n = 12
    gen_public = {k: v for k, v in gen.items() if k != "centers"}
    attempts_i = gen.get("attempts")
    reject_approx = None
    if isinstance(attempts_i, (int, float)):
        # no spherical packing cada tentativa falha conta como rejeicao aproximada
        # tentativas aceites mais rejeicoes somam o total attempts do gerador
        reject_approx = max(0, int(attempts_i) - len(centers))
    # extra junta metadados ao packed bed model antes de export model data
    # export escreve stl binario e opcionalmente este extra como ficheiro json lateral
    # spherical e hexagonal passam por validate configuration depois dos geradores
    # a validacao verifica cada par de esferas com distancia maior ou igual dois r mais gap
    # tambem verifica cada centro dentro do anel cilindrico com folga para tampas
    extra: Dict[str, Any] = {
        "packing_method": method,
        "particle_kind": pk,
        "collision_model": "circumscribed_sphere",
        "collision_radius_equiv": r_pack,
        "validation": report_val,
        "porosity_estimate": poros,
        "generation": gen_public,
        "generation_wall_time_sec": elapsed,
        "gap_convention": "center_distance >= r1+r2+gap",
        "n_particles_requested": p["particle_count"],
        "n_particles_placed": len(centers),
        "n_spheres_requested": p["particle_count"],
        "n_spheres_placed": len(centers),
        "sphere_centers_preview": [
            [float(c[0]), float(c[1]), float(c[2])] for c in centers[:preview_n]
        ],
        "sphere_centers_histogram": [
            [float(c[0]), float(c[1]), float(c[2])]
            for c in centers[: min(len(centers), 500)]
        ],
        "pair_violations": report_val.get("pair_violations"),
        "domain_violations": report_val.get("domain_violations"),
        "placement_attempts_total": attempts_i,
        "placement_rejections_approx": reject_approx,
        "geometry_mode": gm,
    }
    # json opcional com mesmo nome base que stl mais sufixo pure bed
    out_json = out_stl.parent / f"{out_stl.stem}_pure_bed.json"
    if slice_cfg_active(slice_cfg):
        extra["slice"] = slice_cfg
        if slice_summary_scientific:
            extra["slice_particle_summary"] = slice_summary_scientific
            extra["slice_particle_policy"] = slice_cfg.get("slice_particle_policy")
    export_model_data(packed, out_stl, out_json=out_json, extra=extra)


def generate_packed_bed_stl(
    bed_json: Path, out_stl: Path, max_passos: int = 12000
) -> None:
    # entrada publica unica para testes e para o servico fastapi
    p = load_bed_json(bed_json)
    packing = p.get("packing") or {}
    use_legacy = _coerce_bool(packing.get("use_legacy_drop"), False)
    method = str(p.get("packing_method") or "rigid_body")
    if method == "rigid_body" and use_legacy:
        _legacy_generate_stl(p, out_stl, max_passos)
        return
    from engine.pipeline import generate_packed_bed

    generate_packed_bed(p, out_stl)


# resumo final para quem le o ficheiro inteiro
# tubo oco vem de malha parametrizada por segmentos
# tampas sao volumes curtos
# particulas sao esfera uv cubo ou cilindro conforme particles kind
# spherical e aleatorio com rejeicao
# hexagonal e grade cortada ao cilindro
# validate configuration fecha o ciclo de seguranca geometrica
# motor python escolhido na api aponta para este script
# motor blender escolhido na api aponta para o projeto blender
