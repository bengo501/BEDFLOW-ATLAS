# modo hexagonal 3d usa grade regular inspirada em empacotamento compacto
# no plano xy linhas alternadas deslocam metade do passo horizontal formando triangulos equilateros
# em z camadas alternam outro deslocamento para aproximar empilhamento abc de esferas iguais
# passo vertical dz deriva de geometria de tetraedro regular entre centros vizinhos
# iteramos indices i j k numa caixa maior que o dominio depois filtramos com point in domain
# candidatos dentro do anulo cilindrico entram numa lista
# ordenamos por raio ao eixo depois z depois x depois y para o corte nos primeiros n ser determinista
# se houver menos candidatos que n target devolvemos todos e marcamos motivo insuficiente
# colisao entre pares ainda e verificada depois em validation py como no modo spherical
from __future__ import annotations

import math
import random
import time
from typing import List, Tuple, Dict, Any, Optional

from .geometry_math import AnnulusBedDomain, point_in_domain


def _cylinder_radius_xy(p: Tuple[float, float, float]) -> float:
    # rho e distancia euclidiana de x y ao eixo z ignorando z
    return math.hypot(p[0], p[1])


def generate_hexagonal_packing(
    domain: AnnulusBedDomain,
    n_target: int,
    r_sphere: float,
    gap: float,
    *,
    step_x: Optional[float] = None,
    random_seed: Optional[int] = None,
) -> Dict[str, Any]:
    # domain igual ao spherical packing
    # n target numero desejado de centros
    # r sphere raio
    # gap folga entre superficies
    # step x opcional espacamento horizontal se none usa dois r mais gap que e o diametro com folga

    t0 = time.perf_counter()
    # a e o passo horizontal da grade se o utilizador nao der valor usamos o minimo fisico
    a = float(step_x) if step_x is not None else (2.0 * r_sphere + gap)
    # passo nulo ou negativo nao define rede
    if a <= 0:
        return {
            "centers": [],
            "n_placed": 0,
            "n_target": n_target,
            "elapsed_sec": time.perf_counter() - t0,
            "stopped_reason": "passo_invalido",
            "step_x": a,
        }

    # dy separacao entre linhas no y para triangulos equilateros no plano
    dy = a * math.sqrt(3.0) / 2.0
    # dz separacao vertical entre camadas tipo empilhamento denso
    dz = a * math.sqrt(2.0 / 3.0)
    # deslocamentos quando k e impar simulam camada b ou c
    layer_shift_x = a / 2.0
    layer_shift_y = a / (2.0 * math.sqrt(3.0))

    xmin, xmax, ymin, ymax, zmin, zmax = domain.bbox_for_sampling()
    rho_min, rho_max = domain.radial_bounds()

    if rho_min > rho_max or zmin > zmax:
        return {
            "centers": [],
            "n_placed": 0,
            "n_target": n_target,
            "elapsed_sec": time.perf_counter() - t0,
            "stopped_reason": "dominio_vazio",
            "step_x": a,
        }

    # margin expande a grelha alem do bbox para nao cortar pontos validos na borda
    margin = 2.0 * a
    # limites de indices cobrem a caixa ampliada em todas as direcoes
    i_min = int(math.floor((xmin - margin) / a))
    i_max = int(math.ceil((xmax + margin) / a))
    j_min = int(math.floor((ymin - margin) / dy))
    j_max = int(math.ceil((ymax + margin) / dy))
    k_min = int(math.floor((zmin - margin) / dz))
    k_max = int(math.ceil((zmax + margin) / dz))

    # candidates guarda todos os centros da grade que caem dentro do dominio
    candidates: List[Tuple[float, float, float]] = []
    # k indexa camadas em z
    for k in range(k_min, k_max + 1):
        lz = k * dz
        # offsets dependem da paridade da camada
        off_x_k = layer_shift_x if (k % 2) else 0.0
        off_y_k = layer_shift_y if (k % 2) else 0.0
        # j indexa linhas no plano xy
        for j in range(j_min, j_max + 1):
            # row off cria o deslocamento horizontal das linhas impares
            row_off = (a / 2.0) if (j % 2) else 0.0
            y = j * dy + off_y_k
            # i indexa colunas ao longo de x
            for i in range(i_min, i_max + 1):
                x = i * a + row_off + off_x_k
                z = lz
                p = (x, y, z)
                # so entra na lista se o centro respeitar paredes e tampas
                if point_in_domain(p, domain):
                    candidates.append(p)

    rng = random.Random(random_seed) if random_seed is not None else random
    rng.shuffle(candidates)

    if len(candidates) >= n_target:
        chosen = candidates[:n_target]
        reason = "ok_truncado"
    else:
        chosen = candidates
        reason = "pontos_insuficientes_na_grade"

    elapsed = time.perf_counter() - t0
    return {
        "centers": chosen,
        "n_placed": len(chosen),
        "n_target": n_target,
        "elapsed_sec": elapsed,
        "stopped_reason": reason,
        "step_x": a,
        "step_y": dy,
        "step_z": dz,
        "candidates_before_trim": len(candidates),
        "random_seed": random_seed,
    }
