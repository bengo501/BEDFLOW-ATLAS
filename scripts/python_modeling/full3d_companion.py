# utilitario compartilhado: "companheiro 3d completo" de uma saida 2d (thin slice)
#
# quando o modo de geometria e pseudo_2d_thin_slice, o pipeline corta o leito 3d
# numa lamina fina e exporta apenas o 2d. para validar visualmente o corte e
# manter rastreabilidade, gravamos tambem o modelo 3d completo num arquivo irmao
# com o sufixo "_full3d" (ex.: leito.stl -> leito_full3d.stl).
#
# este modulo centraliza:
#   - leitura do flag slice.preserve_full_3d (default: ligado)
#   - convencao de nome do arquivo companheiro
# para que o motor python (engine/pipeline.py) e o blender (leito_extracao.py)
# usem exatamente a mesma regra.
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

# sufixo aplicado ao nome base do arquivo 2d para nomear o modelo 3d preservado
FULL3D_SUFFIX = "_full3d"

# papel registrado no json lateral do arquivo companheiro
FULL3D_ROLE = "full_3d_companion"


def _coerce_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    s = str(value).strip().lower()
    if s in ("true", "1", "yes", "sim", "on"):
        return True
    if s in ("false", "0", "no", "nao", "off"):
        return False
    return default


def preserve_full_3d_enabled(
    slice_cfg: Optional[Dict[str, Any]], default: bool = True
) -> bool:
    """devolve True se o modelo 3d completo deve ser preservado ao gerar a fatia 2d.

    controlado por slice.preserve_full_3d; quando ausente, usa ``default`` (ligado).
    """
    if not isinstance(slice_cfg, dict):
        return default
    return _coerce_bool(slice_cfg.get("preserve_full_3d"), default)


def full3d_path_for(out_2d: Path, suffix: Optional[str] = None) -> Path:
    """caminho do arquivo 3d companheiro ao lado da saida 2d.

    preserva a extensao do 2d quando ``suffix`` e None; caso contrario usa a
    extensao informada (ex.: ".blend") mantendo a mesma pasta e nome base.
    """
    out_2d = Path(out_2d)
    ext = suffix if suffix is not None else out_2d.suffix
    if ext and not ext.startswith("."):
        ext = "." + ext
    return out_2d.parent / f"{out_2d.stem}{FULL3D_SUFFIX}{ext}"


def full3d_sidecar_path_for(full3d_path: Path) -> Path:
    """caminho do json lateral ({stem}_pure_bed.json) do arquivo 3d companheiro."""
    full3d_path = Path(full3d_path)
    return full3d_path.parent / f"{full3d_path.stem}_pure_bed.json"


def full3d_companion_metadata(
    *,
    companion_of: Path,
    generation_backend: str,
    geometry_mode: str = "full_3d",
    n_particles: Optional[int] = None,
) -> Dict[str, Any]:
    """metadados padrao para o json lateral do modelo 3d preservado."""
    meta: Dict[str, Any] = {
        "geometry_mode": geometry_mode,
        "generation_backend": generation_backend,
        "role": FULL3D_ROLE,
        "companion_of": Path(companion_of).name,
        "note": "modelo 3d completo preservado para validacao do corte 2d",
    }
    if n_particles is not None:
        meta["n_particles"] = int(n_particles)
    return meta
