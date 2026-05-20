# normalizacao de json para geracao pure python e alinhamento com bed wizard
#
# este modulo faz apenas traducao de campos
# ele pega informacoes geometricas do cilindro oco e do tipo de geracao
# e devolve os valores que o restante do codigo espera
#
# objetivo
# permitir que o usuario use raios externos e internos
# sem quebrar o formato historico que usa diameter e wall_thickness
#
from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple


def _to_float(v: Any, default: float = 0.0) -> float:
    # esta funcao tenta converter um valor solto do json em float
    # o json pode trazer valores como numero ou como string
    # e pode trazer virgula decimal
    # se o valor for none a funcao devolve o default
    if v is None:
        return float(default)
    # se o tipo ja for numerico convertemos para float
    if isinstance(v, (int, float)):
        return float(v)
    # se vier como texto removemos a conversao de virgula
    return float(str(v).replace(",", "."))


def _first_float(bed: Dict[str, Any], keys: Tuple[str, ...]) -> Optional[float]:
    # esta funcao escolhe o primeiro campo existente em uma lista de chaves
    # e converte esse campo para float
    # se nenhuma chave existir devolvemos none
    for k in keys:
        if k in bed and bed[k] is not None:
            return _to_float(bed[k], 0.0)
    return None


def normalize_generation_backend(raw: Optional[Any], default: str = "blender") -> str:
    # esta funcao normaliza o modo de geracao que o usuario pediu
    # ela aceita varias formas de entrada e devolve apenas dois nomes canonicos
    # python_engine e blender
    # default e usado quando o campo nao existe ou nao e reconhecido

    # se vier none usamos default
    if raw is None:
        return default

    # transformamos em texto e normalizamos caixa e espacos
    s = str(raw).strip().strip('"').strip("'").lower()
    if not s:
        return default

    # unificamos separadores para reduzir variacoes de escrita
    s = s.replace("-", "_").replace(" ", "_")
    while "__" in s:
        s = s.replace("__", "_")

    # tabela de alias comuns
    # o objetivo e aceitar nomes informais
    aliases = {
        "python": "python_engine",
        "pure": "python_engine",
        "pure_python": "python_engine",
        "python_engine": "python_engine",
        "python_puro": "python_engine",
        "stl_only": "python_engine",
        "blender_python": "blender",
        "blender": "blender",
    }
    s = aliases.get(s, s)

    # se depois de alias ainda for um dos nomes validos devolvemos
    if s in ("python_engine", "blender"):
        return s

    # caso desconhecido usamos default para nao quebrar o pipeline
    return default


def merge_root_generation_backend(data: Dict[str, Any]) -> None:
    # esta funcao copia um campo opcional dentro de generation para o topo
    #
    # alguns json usam a estrutura
    # generation
    #   backend
    # e o restante do sistema espera generation_backend na raiz
    #
    # entao se generation_backend ja existir nao fazemos nada
    # se generation_backend nao existir e generation for um dict
    # copiamos generation.backend para generation_backend
    if not isinstance(data, dict):
        return
    if data.get("generation_backend") not in (None, ""):
        return

    gen = data.get("generation")
    if isinstance(gen, dict):
        b = gen.get("backend")
        if b not in (None, ""):
            data["generation_backend"] = normalize_generation_backend(b)


def resolve_bed_geometry_numbers(bed: Dict[str, Any]) -> Tuple[float, float, float]:
    # esta funcao converte informacoes do cilindro oco para numeros padrao
    #
    # retorno em ordem
    # diameter
    # height
    # wall_thickness
    #
    # como o sistema historico usa diameter e wall_thickness
    # e a interface nova pode receber raios externos e internos
    # fazemos a conversao quando r_outer e r_inner existem
    #
    # regra de prioridade
    # se r_outer e r_inner existirem
    # usamos eles
    # se nao existirem usamos diameter e wall_thickness

    # procuramos raio externo e raio interno
    ro = _first_float(bed, ("r_outer", "r_ext"))
    ri = _first_float(bed, ("r_inner", "r_int"))

    # height vem do campo bed height
    height = _to_float(bed.get("height"), 0.1)

    # se ambos raios existirem calculamos diameter e wall_thickness
    if ro is not None and ri is not None:
        # valida minima para evitar cilindro impossivel
        # precisa ro maior que ri
        if ro <= 0 or ri < 0 or ro <= ri:
            raise ValueError("r_outer e r_inner invalidos esperado r_outer maior que r_inner positivos")

        diameter = 2.0 * ro
        wall = ro - ri
        return diameter, height, wall

    # caso contrario usamos valores historicos
    diameter = _to_float(bed.get("diameter"), 0.05)
    wall = _to_float(bed.get("wall_thickness"), 0.002)
    return diameter, height, wall


def bed_section_for_wizard(bed: Dict[str, Any]) -> Dict[str, Any]:
    # esta funcao prepara a secao bed no formato esperado pelo bed wizard
    #
    # ela devolve um novo dict que copia os campos existentes
    # e substitui diameter height wall_thickness pelos valores derivados
    # se o usuario forneceu raios externos e internos
    out = dict(bed)
    d, h, w = resolve_bed_geometry_numbers(out)
    out["diameter"] = d
    out["height"] = h
    out["wall_thickness"] = w
    return out

