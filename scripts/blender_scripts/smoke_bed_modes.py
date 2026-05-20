# smoke: valida modulos de modos de cilindro (sem bpy)
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_PM = _ROOT / "scripts" / "python_modeling"
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from bed_internal_modes import (  # noqa: E402
    MODE_VISIBLE_INNER,
    normalize_internal_cylinder_mode,
    resolve_bed_internal_config,
)

assert normalize_internal_cylinder_mode("m2") == MODE_VISIBLE_INNER
mode, vis, _ = resolve_bed_internal_config(
    {"bed": {"internal_cylinder_mode": MODE_VISIBLE_INNER}}
)
assert mode == MODE_VISIBLE_INNER
assert vis["show_internal_cylinder"] is True
print("smoke_bed_modes: ok")
