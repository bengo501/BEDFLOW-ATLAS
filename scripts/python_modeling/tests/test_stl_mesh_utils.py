# testes leves de stl mesh utils sem dependencias pesadas
from __future__ import annotations

import struct
import tempfile
from pathlib import Path

from stl_mesh_utils import merge_mesh, uv_sphere, write_stl_binary


def test_uv_sphere_nonempty():
    v, f = uv_sphere(0.0, 0.0, 0.0, 0.01, lat=4, lon=6)
    assert len(v) == (4 + 1) * 6
    assert len(f) > 0


def test_merge_mesh_offsets_indices():
    va = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)]
    fa = [(0, 1, 0)]
    vb = [(2.0, 0.0, 0.0)]
    fb = [(0, 0, 0)]
    v, f = merge_mesh(va, fa, vb, fb)
    assert len(v) == 3
    assert any(t[0] == 2 for t in f if len(t) == 3)


def test_write_stl_binary_creates_valid_header():
    verts = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
    faces = [(0, 1, 2)]
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "t.stl"
        write_stl_binary(p, verts, faces)
        raw = p.read_bytes()
        assert len(raw) >= 84
        n = struct.unpack_from("<I", raw, 80)[0]
        assert n == 1
        assert len(raw) == 84 + 50 * n


def test_write_stl_binary_threejs_stride():
    """three.js STLLoader usa faceLength=50; ficheiros com 52 bytes/tri falham no viewer."""
    verts = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
    faces = [(0, 1, 2), (0, 2, 3)]
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "bed.stl"
        write_stl_binary(p, verts, faces)
        raw = p.read_bytes()
        n = struct.unpack_from("<I", raw, 80)[0]
        assert n == 2
        assert len(raw) == 84 + 50 * n
