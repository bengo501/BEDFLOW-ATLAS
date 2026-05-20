# motor de empacotamento python (geometrico + dem)
from .reports import PackingResult, write_packing_report

__all__ = [
    "PackingResult",
    "write_packing_report",
]


def generate_packed_bed(*args, **kwargs):
    from .pipeline import generate_packed_bed as _gp

    return _gp(*args, **kwargs)


def run_packing(*args, **kwargs):
    from .pipeline import run_packing as _rp

    return _rp(*args, **kwargs)
