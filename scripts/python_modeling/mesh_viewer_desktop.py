#!/usr/bin/env python3
"""
visualizador desktop para stl/obj/ply (open3d).

interface predefinida: janela gui minimalista (open3d.visualization.gui) —
cena + barra lateral + overlays 2d fixos (sem painel tipo mini-blender do draw()).

defina bedflow_o3d_legacy=1 para o visualizador glfw antigo (teclas).

corte: crop por caixa alinhada ao eixo escolhido (geometria pura; nao edita ficheiro).

metadados do leito: coloque um ficheiro com o mesmo nome da malha e extensao .bed.json
na mesma pasta (ou use --bed-json caminho) para preencher altura, particulas, etc. no painel.
"""
from __future__ import annotations

import argparse
import copy
import os
import sys
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))


def _cluster_count(mesh: object) -> int:
    try:
        _labels, n_tri, _area = mesh.cluster_connected_triangles()
        return int(len(n_tri))
    except Exception:
        return 1


def _style_mesh(m: object) -> None:
    import open3d as o3d

    m.vertex_colors = o3d.utility.Vector3dVector()
    m.compute_vertex_normals()
    m.paint_uniform_color([0.12, 0.42, 0.78])


def _run_legacy_viewer(
    o3d: object,
    path: Path,
    mesh_orig: object,
    mesh: object,
    center: np.ndarray,
    mn: np.ndarray,
    mx: np.ndarray,
    n_vert: int,
    n_tri: int,
    n_comp: int,
) -> None:
    from mesh_viewer.geometry_core import bbox_lineset, crop_mesh_slab, style_mesh_rgb

    state: dict = {
        "clip_frac": 0.0,
        "axis": 1,
        "from_max": True,
        "show_bbox": False,
        "bbox_geom": bbox_lineset(mesh_orig),
        "wire": False,
        "dark_bg": True,
        "geom": mesh,
    }

    print(
        "bedflow viewer (legacy): r reset | w wireframe | b bbox | h fundo | "
        "[ / ] corte | 0 sem corte | x/y/z eixo | n lado | i info | esc/q sair",
        file=sys.stderr,
    )

    vis = o3d.visualization.VisualizerWithKeyCallback()
    win = f"bedflow viewer (legacy) — {path.name}"
    if not vis.create_window(window_name=win, width=1024, height=768, visible=True):
        print("erro: nao foi possivel criar a janela open3d.", file=sys.stderr)
        return

    def _apply_render_opts() -> None:
        ro = vis.get_render_option()
        ro.mesh_show_back_face = True
        ro.mesh_show_wireframe = bool(state["wire"])
        if state["dark_bg"]:
            ro.background_color = np.asarray([0.08, 0.08, 0.1])
        else:
            ro.background_color = np.asarray([0.95, 0.95, 0.95])

    def _refresh_mesh_geometry() -> None:
        new_m = crop_mesh_slab(
            mesh_orig,
            float(state["clip_frac"]),
            int(state["axis"]),
            bool(state["from_max"]),
        )
        style_mesh_rgb(new_m, (0.12, 0.42, 0.78))
        try:
            vis.remove_geometry(state["geom"], reset_bounding_box=False)
        except Exception:
            pass
        state["geom"] = new_m
        vis.add_geometry(state["geom"], reset_bounding_box=False)
        if state["show_bbox"] and state["bbox_geom"] is not None:
            try:
                vis.remove_geometry(state["bbox_geom"], reset_bounding_box=False)
            except Exception:
                pass
            state["bbox_geom"] = bbox_lineset(mesh_orig)
            vis.add_geometry(state["bbox_geom"], reset_bounding_box=False)
        _apply_render_opts()
        vis.update_renderer()

    vis.add_geometry(state["geom"], reset_bounding_box=True)
    _apply_render_opts()
    ctr = vis.get_view_control()
    ctr.set_zoom(0.62)
    ctr.set_lookat(center)
    ctr.set_front(np.asarray([0.52, -0.62, -0.58]))
    ctr.set_up(np.asarray([0.0, 1.0, 0.0]))

    def _set_title() -> None:
        axn = ("x", "y", "z")[int(state["axis"]) % 3]
        side = "max" if state["from_max"] else "min"
        ext_s = f"{mx[0]-mn[0]:.4f} x {mx[1]-mn[1]:.4f} x {mx[2]-mn[2]:.4f}"
        t = (
            f"{path.name} | v={n_vert} t={n_tri} comp~{n_comp} | {ext_s} | "
            f"corte={state['clip_frac']:.2f} ax={axn} {side}"
        )
        try:
            vis.set_window_title(t)
        except Exception:
            pass

    def _quit_cb(_vis: object) -> bool:
        _vis.close()
        return True

    def _reset_cb(_vis: object) -> bool:
        _vis.reset_view_point(True)
        c = _vis.get_view_control()
        c.set_zoom(0.62)
        c.set_lookat(center)
        c.set_front(np.asarray([0.52, -0.62, -0.58]))
        c.set_up(np.asarray([0.0, 1.0, 0.0]))
        _set_title()
        return False

    def _wire_cb(_vis: object) -> bool:
        state["wire"] = not state["wire"]
        _apply_render_opts()
        _vis.update_renderer()
        _set_title()
        return False

    def _bg_cb(_vis: object) -> bool:
        state["dark_bg"] = not state["dark_bg"]
        _apply_render_opts()
        _vis.update_renderer()
        _set_title()
        return False

    def _bbox_cb(_vis: object) -> bool:
        state["show_bbox"] = not state["show_bbox"]
        if state["show_bbox"] and state["bbox_geom"] is not None:
            state["bbox_geom"] = bbox_lineset(mesh_orig)
            _vis.add_geometry(state["bbox_geom"], reset_bounding_box=False)
        elif state["bbox_geom"] is not None:
            try:
                _vis.remove_geometry(state["bbox_geom"], reset_bounding_box=False)
            except Exception:
                pass
        _vis.update_renderer()
        _set_title()
        return False

    def _clip_dec(_vis: object) -> bool:
        state["clip_frac"] = max(0.0, float(state["clip_frac"]) - 0.05)
        _refresh_mesh_geometry()
        _set_title()
        return False

    def _clip_inc(_vis: object) -> bool:
        state["clip_frac"] = min(0.95, float(state["clip_frac"]) + 0.05)
        _refresh_mesh_geometry()
        _set_title()
        return False

    def _clip_zero(_vis: object) -> bool:
        state["clip_frac"] = 0.0
        _refresh_mesh_geometry()
        _set_title()
        return False

    def _axis_cb(_vis: object, ax: int) -> bool:
        state["axis"] = ax
        _refresh_mesh_geometry()
        _set_title()
        return False

    def _flip_cb(_vis: object) -> bool:
        state["from_max"] = not bool(state["from_max"])
        _refresh_mesh_geometry()
        _set_title()
        return False

    def _info_cb(_vis: object) -> bool:
        axn = ("x", "y", "z")[int(state["axis"]) % 3]
        print(
            f"[info] vertices={n_vert} triangulos={n_tri} componentes~{n_comp} "
            f"clip={state['clip_frac']:.3f} eixo={axn}",
            file=sys.stderr,
        )
        return False

    vis.register_key_callback(ord("Q"), _quit_cb)
    try:
        vis.register_key_callback(27, _quit_cb)
    except Exception:
        pass
    vis.register_key_callback(ord("R"), _reset_cb)
    vis.register_key_callback(ord("W"), _wire_cb)
    vis.register_key_callback(ord("B"), _bbox_cb)
    vis.register_key_callback(ord("H"), _bg_cb)
    vis.register_key_callback(ord("["), _clip_dec)
    vis.register_key_callback(ord("]"), _clip_inc)
    vis.register_key_callback(ord("0"), _clip_zero)
    vis.register_key_callback(ord("I"), _info_cb)
    vis.register_key_callback(ord("X"), lambda v: _axis_cb(v, 0))
    vis.register_key_callback(ord("Y"), lambda v: _axis_cb(v, 1))
    vis.register_key_callback(ord("Z"), lambda v: _axis_cb(v, 2))
    vis.register_key_callback(ord("N"), _flip_cb)

    _set_title()
    vis.run()
    vis.destroy_window()


def main() -> int:
    p = argparse.ArgumentParser(description="visualizador 3d (open3d)")
    p.add_argument("mesh_file", type=str, help="ficheiro .stl .obj ou .ply")
    p.add_argument(
        "--bed-json",
        type=str,
        default=None,
        help="opcional: caminho para .bed.json (senao tenta ficheiro com o mesmo nome da malha)",
    )
    args = p.parse_args()
    path = Path(args.mesh_file).expanduser().resolve()
    if not path.is_file():
        print(f"erro: ficheiro nao encontrado: {path}", file=sys.stderr)
        return 1
    suf = path.suffix.lower()
    if suf not in (".stl", ".obj", ".ply"):
        print(
            "erro: open3d neste script suporta stl, obj e ply. "
            "para gltf/glb use o visualizador web ou blender.",
            file=sys.stderr,
        )
        return 1
    try:
        import open3d as o3d
    except ImportError:
        print(
            "erro: instale as dependencias de visualizacao (open3d):\n"
            "  pip install -r requirements-visualizacao.txt\n",
            file=sys.stderr,
        )
        return 2

    try:
        mesh = o3d.io.read_triangle_mesh(
            str(path), enable_post_processing=True, print_progress=False
        )
        if mesh.is_empty() or len(mesh.triangles) == 0:
            print(
                "erro: malha vazia apos leitura. exporte com triangulos ou use .stl.",
                file=sys.stderr,
            )
            return 3
        mesh.remove_duplicated_vertices()
        mesh.remove_degenerate_triangles()
        mesh.remove_unreferenced_vertices()
        if mesh.is_empty() or len(mesh.triangles) == 0:
            hint = (
                "obj sem triangulos validos — reexporte como stl ou abra no viewer web"
                if suf == ".obj"
                else "malha sem triangulos apos limpeza"
            )
            print(f"erro: {hint}", file=sys.stderr)
            return 3
        _style_mesh(mesh)

        bbox = mesh.get_axis_aligned_bounding_box()
        center = np.asarray(bbox.get_center(), dtype=np.float64)
        extent = float(np.max(bbox.get_extent()))
        if extent < 1e-12:
            print("erro: caixa limitadora degenerada.", file=sys.stderr)
            return 3

        mesh_orig = copy.deepcopy(mesh)
        n_vert = len(mesh.vertices)
        n_tri = len(mesh.triangles)
        n_comp = _cluster_count(mesh_orig)
        mn = np.asarray(bbox.get_min_bound(), dtype=np.float64)
        mx = np.asarray(bbox.get_max_bound(), dtype=np.float64)

        legacy = os.environ.get("BEDFLOW_O3D_LEGACY", "").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        from mesh_viewer.bed_metadata import load_bed_json_for_mesh

        bed_path = Path(args.bed_json).expanduser().resolve() if args.bed_json else None
        bed_meta = load_bed_json_for_mesh(path, explicit=bed_path)

        if legacy:
            _run_legacy_viewer(o3d, path, mesh_orig, mesh, center, mn, mx, n_vert, n_tri, n_comp)
        else:
            try:
                from mesh_viewer.scientific_app import run_scientific_viewer

                run_scientific_viewer(
                    o3d,
                    path,
                    mesh_orig,
                    mn,
                    mx,
                    center,
                    n_vert,
                    n_tri,
                    n_comp,
                    bed_meta=bed_meta,
                )
            except Exception as e:
                print(
                    f"aviso: viewer gui cientifico falhou ({e}); modo legacy.",
                    file=sys.stderr,
                )
                _run_legacy_viewer(
                    o3d, path, mesh_orig, mesh, center, mn, mx, n_vert, n_tri, n_comp
                )
    except Exception as e:
        print(f"erro ao abrir malha: {e}", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
