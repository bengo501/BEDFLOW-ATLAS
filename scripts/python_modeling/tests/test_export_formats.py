"""
prova de que o motor python exporta OBJ/glTF/GLB (além de STL).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PM = Path(__file__).resolve().parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from mesh_export_formats import export_mesh_formats, normalize_export_formats  # noqa: E402
from stl_mesh_utils import cylinder_axis  # noqa: E402


def test_normalize_formats():
    assert normalize_export_formats("stl_binary,obj,glb") == ["stl", "obj", "glb"]
    assert normalize_export_formats(["STL", "gltf", "gltf"]) == ["stl", "gltf"]
    assert normalize_export_formats(None) == []


def test_export_obj(tmp_path):
    v, f = cylinder_axis(0, 0, 0.03, 0.02, 0.06, axis="z", segments=24)
    gen = export_mesh_formats(tmp_path / "m.stl", v, f, ["obj"], skip_stl=True)
    assert "m.obj" in gen
    assert (tmp_path / "m.obj").stat().st_size > 50
    # o .obj tem vértices e faces
    txt = (tmp_path / "m.obj").read_text(encoding="utf-8")
    assert "v " in txt and "f " in txt


def test_export_gltf_glb(tmp_path):
    pytest.importorskip("trimesh")
    v, f = cylinder_axis(0, 0, 0.03, 0.02, 0.06, axis="z", segments=24)
    gen = export_mesh_formats(tmp_path / "m.stl", v, f, ["gltf", "glb"], skip_stl=True)
    assert "m.gltf" in gen
    assert "m.glb" in gen
    assert (tmp_path / "m.glb").stat().st_size > 100


def test_blender_only_format_warns(tmp_path):
    v, f = cylinder_axis(0, 0, 0.03, 0.02, 0.06, axis="z", segments=16)
    warns: list = []
    gen = export_mesh_formats(tmp_path / "m.stl", v, f, ["blend", "fbx"], warnings=warns)
    assert gen == []  # nenhum gerado pelo motor python
    assert any("blender" in w for w in warns)
