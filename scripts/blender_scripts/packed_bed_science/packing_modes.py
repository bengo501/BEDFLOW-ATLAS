# este ficheiro e a fonte unica de nomes canonicos para modos de empacotamento
# o blender o script stl offline e o bed wizard importam daqui para nao divergirem
# quatro modos existem no produto
# rigid_body: blender usa fisica nativa; python_engine usa preset dem simplificado
# spherical_packing usa sorteio e rejeicao ver packing_spherical
# hexagonal_3d usa grade regular filtrada ver packing_hexagonal
# dem usa solver de elementos discretos no motor python
from __future__ import annotations

from typing import Any, Dict, FrozenSet, Optional

# conjunto imutavel com os tres nomes oficiais usados em if e validacao
# frozen set impede alteracao acidental em tempo de execucao
SUPPORTED_PACKING_MODES: FrozenSet[str] = frozenset(
    ("rigid_body", "spherical_packing", "hexagonal_3d", "dem")
)

# tupla com ordem fixa para menus no terminal e mensagens de ajuda
PACKING_MODE_CHOICES: tuple[str, ...] = (
    "rigid_body",
    "spherical_packing",
    "hexagonal_3d",
    "dem",
)


def normalize_packing_mode(raw: Optional[Any], default: str = "rigid_body") -> str:
    # entrada raw pode ser none string numero vindo de json ou formulario
    # saida e sempre um dos tres modos ou default se nada reconhecer
    # passo um tratar none e string vazia
    if raw is None:
        return default
    # passo dois converter para string minuscula e tirar aspas comuns
    s = str(raw).strip().strip('"').strip("'").lower()
    if not s:
        return default
    # passo tres trocar hifens e espacos por underscore para unificar hexagonal-3d e hexagonal 3d
    s = s.replace("-", "_").replace(" ", "_")
    # passo quatro colapsar underscores duplicados que possam aparecer
    while "__" in s:
        s = s.replace("__", "_")
    # passo cinco tabela de sinonimos que utilizadores e ficheiros antigos podem enviar
    # rigidbody sem underscore vira rigid_body
    # hex3d e atalho informal para hexagonal_3d
    # spherical sozinho vira spherical_packing
    aliases = {
        "rigidbody": "rigid_body",
        "rigid": "rigid_body",
        "hexagonal3d": "hexagonal_3d",
        "hex3d": "hexagonal_3d",
        "hexagonal": "hexagonal_3d",
        "spherical": "spherical_packing",
        "sphericalpacking": "spherical_packing",
        "discrete_element": "dem",
        "discrete_element_method": "dem",
        "elements_discretos": "dem",
    }
    s = aliases.get(s, s)
    # passo seis se bate com um modo oficial devolve esse nome
    if s in SUPPORTED_PACKING_MODES:
        return s
    # passo sete qualquer outra string desconhecida cai no default para nao quebrar o pipeline
    return default


def packing_method_from_section(packing: Optional[Dict[str, Any]]) -> str:
    # packing e o dicionario json em packing apos leitura do ficheiro
    # devolve sempre um nome canonico via normalize_packing_mode
    # se packing for none ou dict vazio assume rigid_body
    if not packing:
        return "rigid_body"
    # alguns apis antigos gravam packing_method em vez de method
    m = packing.get("method")
    if m in (None, ""):
        m = packing.get("packing_method")
    return normalize_packing_mode(m, default="rigid_body")


def merge_root_packing_mode(data: Dict[str, Any]) -> Dict[str, Any]:
    # alguns json trazem packing_mode no topo do objeto em paralelo com packing method
    # esta funcao copia o valor do topo para packing method so quando method falta
    # assim o leitor downstream so precisa olhar packing method
    # data e o dict raiz do json modificado in place
    if not isinstance(data, dict):
        return data
    pmode = data.get("packing_mode")
    if pmode is None:
        return data
    pack = data.get("packing")
    if not isinstance(pack, dict):
        data["packing"] = {}
        pack = data["packing"]
    if pack.get("method") in (None, ""):
        pack["method"] = normalize_packing_mode(pmode)
    return data
