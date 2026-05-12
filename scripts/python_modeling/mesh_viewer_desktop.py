#!/usr/bin/env python3
"""
visualizador desktop para stl/obj/ply via open3d (opcional).
uso: python mesh_viewer_desktop.py caminho/absoluto/ou/relativo/modelo.stl

modo predefinido: open3d.visualization.draw (filament) — painel de acções,
etiquetas 3d na cena e caixas de dialogo (menos erros wgl/glfw no windows).

defina bedflow_o3d_legacy=1 para o visualizador antigo (teclas r/w/b/h/...).

nota: num unico stl fundido nao ha separacao parede/particulas; o corte por
caixa (crop) retira uma fatia ao longo do eixo escolhido para expor o interior.
"""
from __future__ import annotations

import argparse
import copy
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import numpy as np


def _cluster_count(mesh: Any) -> int:
    try:
        _labels, n_tri, _area = mesh.cluster_connected_triangles()
        return int(len(n_tri))
    except Exception:
        return 1


def _bbox_lineset(mesh: Any) -> Any:
    import open3d as o3d

    bb = mesh.get_axis_aligned_bounding_box()
    ls = o3d.geometry.LineSet.create_from_axis_aligned_bounding_box(bb)
    ls.paint_uniform_color([0.95, 0.45, 0.12])
    return ls


def _crop_mesh_slab(
    mesh_src: Any,
    clip_frac: float,
    axis: int,
    from_max: bool,
) -> Any:
    """
    remove uma fatia ao longo do eixo (0=x,1=y,2=z).
    clip_frac em [0,1]: 0 sem corte; maior remove mais volume a partir do
    extremo max do eixo se from_max, senao a partir do min.
    """
    import open3d as o3d

    if clip_frac <= 1e-9:
        return copy.deepcopy(mesh_src)
    axis = int(axis) % 3
    bbox = mesh_src.get_axis_aligned_bounding_box()
    mn = np.asarray(bbox.get_min_bound(), dtype=np.float64)
    mx = np.asarray(bbox.get_max_bound(), dtype=np.float64)
    h = float(mx[axis] - mn[axis])
    if h < 1e-12:
        return copy.deepcopy(mesh_src)
    delta = float(clip_frac) * h
    mn2 = mn.copy()
    mx2 = mx.copy()
    if from_max:
        mx2[axis] = mx[axis] - delta
    else:
        mn2[axis] = mn[axis] + delta
    if mx2[axis] <= mn2[axis] + 1e-9:
        return copy.deepcopy(mesh_src)
    aabb = o3d.geometry.AxisAlignedBoundingBox(
        min_bound=mn2.astype(np.float64), max_bound=mx2.astype(np.float64)
    )
    try:
        cropped = mesh_src.crop(aabb)
    except Exception:
        return copy.deepcopy(mesh_src)
    if cropped.is_empty() or len(cropped.triangles) == 0:
        return copy.deepcopy(mesh_src)
    return cropped


def _style_mesh(m: Any) -> None:
    import open3d as o3d

    m.vertex_colors = o3d.utility.Vector3dVector()
    m.compute_vertex_normals()
    m.paint_uniform_color([0.12, 0.42, 0.78])


def _f31(v: np.ndarray) -> np.ndarray:
    a = np.asarray(v, dtype=np.float32).reshape(3)
    return a.reshape(3, 1)


def _run_draw_viewer(
    o3d: Any,
    path: Path,
    mesh_orig: Any,
    center: np.ndarray,
    mn: np.ndarray,
    mx: np.ndarray,
    n_vert: int,
    n_tri: int,
    n_comp: int,
) -> None:
    from open3d.visualization import rendering

    state: Dict[str, Any] = {
        "clip_frac": 0.0,
        "axis": 1,
        "from_max": True,
        "show_bbox": False,
        "wire": False,
        "dark_bg": True,
    }

    ext = (mx - mn).astype(np.float64)
    eye = center + np.array(
        [
            ext[0] * 0.55 + float(np.max(ext)) * 0.35,
            ext[1] * 0.45,
            ext[2] * 0.55 + float(np.max(ext)) * 0.35,
        ],
        dtype=np.float64,
    )

    def _bg_rgba() -> np.ndarray:
        if state["dark_bg"]:
            return np.array([[0.08], [0.08], [0.1], [1.0]], dtype=np.float32)
        return np.array([[0.95], [0.95], [0.95], [1.0]], dtype=np.float32)

    def _mesh_material() -> Any:
        mat = rendering.MaterialRecord()
        mat.shader = "defaultLit"
        mat.base_color = (0.12, 0.42, 0.78, 1.0)
        return mat

    def _rebuild_main(vis: Any) -> None:
        m = _crop_mesh_slab(
            mesh_orig,
            float(state["clip_frac"]),
            int(state["axis"]),
            bool(state["from_max"]),
        )
        _style_mesh(m)
        try:
            vis.remove_geometry("mesh")
        except Exception:
            pass
        vis.add_geometry("mesh", m, _mesh_material())
        vis.enable_raw_mode(bool(state["wire"]))
        try:
            vis.show_geometry("bbox", bool(state["show_bbox"]))
        except Exception:
            pass
        vis.set_background(_bg_rgba(), None)
        vis.post_redraw()

    def _ensure_bbox(vis: Any) -> None:
        try:
            vis.remove_geometry("bbox")
        except Exception:
            pass
        ls = _bbox_lineset(mesh_orig)
        mat = rendering.MaterialRecord()
        mat.shader = "unlitLine"
        mat.base_color = (0.95, 0.45, 0.12, 1.0)
        mat.line_width = 2.0
        vis.add_geometry("bbox", ls, mat)
        vis.show_geometry("bbox", bool(state["show_bbox"]))

    def _help_lines() -> List[str]:
        ax_name = ("x", "y", "z")
        return [
            "painel >> acoes (corte, wire, …)",
            "legacy: env bedflow_o3d_legacy=1",
            f"eixo corte: {ax_name[int(state['axis']) % 3]}",
            "malha unica: sem camada so particulas",
        ]

    def _add_help_labels(vis: Any) -> None:
        try:
            vis.clear_3d_labels()
        except Exception:
            pass
        off = float(np.max(ext)) * 0.07
        base = mx.astype(np.float64) + np.array([off * 0.2, off, off * 0.2])
        for i, line in enumerate(_help_lines()):
            pos = base + np.array([0.0, off * 0.35 * float(i), 0.0])
            vis.add_3d_label(_f31(pos), line)

    def on_init(vis: Any) -> None:
        vis.setup_camera(60.0, _f31(center), _f31(eye), _f31(np.array([0.0, 1.0, 0.0])))
        vis.set_background(_bg_rgba(), None)
        _rebuild_main(vis)
        _ensure_bbox(vis)
        _add_help_labels(vis)
        _title(vis)

    def _title(vis: Any) -> None:
        axn = ("x", "y", "z")[int(state["axis"]) % 3]
        side = "max" if state["from_max"] else "min"
        try:
            vis.title = (
                f"{path.name}  v={n_vert}  t={n_tri}  comp~{n_comp}  "
                f"corte={state['clip_frac']:.2f}  eixo={axn}  lado={side}"
            )
        except Exception:
            pass

    def act_reset(vis: Any) -> None:
        vis.setup_camera(60.0, _f31(center), _f31(eye), _f31(np.array([0.0, 1.0, 0.0])))
        _title(vis)

    def act_wire(vis: Any) -> None:
        state["wire"] = not state["wire"]
        vis.enable_raw_mode(bool(state["wire"]))
        vis.post_redraw()
        _title(vis)

    def act_bbox(vis: Any) -> None:
        state["show_bbox"] = not state["show_bbox"]
        if state["show_bbox"]:
            _ensure_bbox(vis)
        try:
            vis.show_geometry("bbox", bool(state["show_bbox"]))
        except Exception:
            pass
        vis.post_redraw()
        _title(vis)

    def act_bg(vis: Any) -> None:
        state["dark_bg"] = not state["dark_bg"]
        vis.set_background(_bg_rgba(), None)
        vis.post_redraw()
        _title(vis)

    def act_clip_inc(vis: Any) -> None:
        state["clip_frac"] = min(0.95, float(state["clip_frac"]) + 0.05)
        _rebuild_main(vis)
        _title(vis)

    def act_clip_dec(vis: Any) -> None:
        state["clip_frac"] = max(0.0, float(state["clip_frac"]) - 0.05)
        _rebuild_main(vis)
        _title(vis)

    def act_clip_zero(vis: Any) -> None:
        state["clip_frac"] = 0.0
        _rebuild_main(vis)
        _title(vis)

    def act_axis(vis: Any) -> None:
        state["axis"] = (int(state["axis"]) + 1) % 3
        _rebuild_main(vis)
        _add_help_labels(vis)
        _title(vis)

    def act_flip(vis: Any) -> None:
        state["from_max"] = not bool(state["from_max"])
        _rebuild_main(vis)
        _add_help_labels(vis)
        _title(vis)

    def act_info(vis: Any) -> None:
        axn = ("x", "y", "z")[int(state["axis"]) % 3]
        side = "a partir do max" if state["from_max"] else "a partir do min"
        msg = (
            f"vertices: {n_vert}\ntriangulos: {n_tri}\n"
            f"componentes conectados (aprox.): {n_comp}\n"
            f"corte: {state['clip_frac']:.3f}\neixo: {axn} ({side})\n\n"
            "num stl/obj unico exportado, parede e particulas estao na mesma malha; "
            "para ver so particulas e preciso geometria separada no ficheiro "
            "(export dedicado) ou cortar ate expor o interior."
        )
        vis.show_message_box("bedflow — informacao", msg)
        _title(vis)

    def act_help(vis: Any) -> None:
        vis.show_message_box(
            "bedflow — ajuda",
            "botoes no painel:\n"
            "  reset cam — vista inicial\n"
            "  wireframe — modo raw (linhas)\n"
            "  bbox — caixa limitadora\n"
            "  fundo — claro/escuro\n"
            "  corte +/- / zero — fatia ao longo do eixo\n"
            "  eixo corte — cicla x, y, z\n"
            "  lado corte — inverte extremo do corte\n"
            "  info — estatisticas\n\n"
            "etiquetas 3d junto ao canto da caixa da malha.\n"
            "modo legacy (teclas): env bedflow_o3d_legacy=1",
        )

    actions: List[Tuple[str, Callable[[Any], None]]] = [
        ("reset cam", act_reset),
        ("wireframe", act_wire),
        ("bbox", act_bbox),
        ("fundo", act_bg),
        ("corte +", act_clip_inc),
        ("corte -", act_clip_dec),
        ("corte 0", act_clip_zero),
        ("eixo corte (x/y/z)", act_axis),
        ("lado corte", act_flip),
        ("info", act_info),
        ("ajuda", act_help),
    ]

    initial = copy.deepcopy(mesh_orig)
    _style_mesh(initial)

    o3d.visualization.draw(
        [{"name": "mesh", "geometry": initial, "material": _mesh_material()}],
        title=f"bedflow viewer — {path.name}",
        width=1100,
        height=768,
        show_ui=True,
        actions=actions,
        on_init=on_init,
        field_of_view=60.0,
        lookat=center.astype(np.float64),
        eye=eye.astype(np.float64),
        up=np.array([0.0, 1.0, 0.0], dtype=np.float64),
        bg_color=(0.08, 0.08, 0.1, 1.0),
    )


def _run_legacy_viewer(
    o3d: Any,
    path: Path,
    mesh_orig: Any,
    mesh: Any,
    center: np.ndarray,
    mn: np.ndarray,
    mx: np.ndarray,
    n_vert: int,
    n_tri: int,
    n_comp: int,
) -> None:
    state: Dict[str, Any] = {
        "clip_frac": 0.0,
        "axis": 1,
        "from_max": True,
        "show_bbox": False,
        "bbox_geom": _bbox_lineset(mesh_orig),
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
        new_m = _crop_mesh_slab(
            mesh_orig,
            float(state["clip_frac"]),
            int(state["axis"]),
            bool(state["from_max"]),
        )
        _style_mesh(new_m)
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
            state["bbox_geom"] = _bbox_lineset(mesh_orig)
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

    def _quit_cb(_vis: Any) -> bool:
        _vis.close()
        return True

    def _reset_cb(_vis: Any) -> bool:
        _vis.reset_view_point(True)
        c = _vis.get_view_control()
        c.set_zoom(0.62)
        c.set_lookat(center)
        c.set_front(np.asarray([0.52, -0.62, -0.58]))
        c.set_up(np.asarray([0.0, 1.0, 0.0]))
        _set_title()
        return False

    def _wire_cb(_vis: Any) -> bool:
        state["wire"] = not state["wire"]
        _apply_render_opts()
        _vis.update_renderer()
        _set_title()
        return False

    def _bg_cb(_vis: Any) -> bool:
        state["dark_bg"] = not state["dark_bg"]
        _apply_render_opts()
        _vis.update_renderer()
        _set_title()
        return False

    def _bbox_cb(_vis: Any) -> bool:
        state["show_bbox"] = not state["show_bbox"]
        if state["show_bbox"] and state["bbox_geom"] is not None:
            state["bbox_geom"] = _bbox_lineset(mesh_orig)
            _vis.add_geometry(state["bbox_geom"], reset_bounding_box=False)
        elif state["bbox_geom"] is not None:
            try:
                _vis.remove_geometry(state["bbox_geom"], reset_bounding_box=False)
            except Exception:
                pass
        _vis.update_renderer()
        _set_title()
        return False

    def _clip_dec(_vis: Any) -> bool:
        state["clip_frac"] = max(0.0, float(state["clip_frac"]) - 0.05)
        _refresh_mesh_geometry()
        _set_title()
        return False

    def _clip_inc(_vis: Any) -> bool:
        state["clip_frac"] = min(0.95, float(state["clip_frac"]) + 0.05)
        _refresh_mesh_geometry()
        _set_title()
        return False

    def _clip_zero(_vis: Any) -> bool:
        state["clip_frac"] = 0.0
        _refresh_mesh_geometry()
        _set_title()
        return False

    def _axis_cb(_vis: Any, ax: int) -> bool:
        state["axis"] = ax
        _refresh_mesh_geometry()
        _set_title()
        return False

    def _flip_cb(_vis: Any) -> bool:
        state["from_max"] = not bool(state["from_max"])
        _refresh_mesh_geometry()
        _set_title()
        return False

    def _info_cb(_vis: Any) -> bool:
        try:
            vc = _vis.get_view_control()
            p = vc.convert_to_pinhole_camera_parameters()
            extr = np.asarray(p.extrinsic)
            tvec = extr[:3, 3]
            dist = float(np.linalg.norm(np.asarray(center) - tvec))
        except Exception:
            dist = float("nan")
        axn = ("x", "y", "z")[int(state["axis"]) % 3]
        print(
            f"[info] vertices={n_vert} triangulos={n_tri} componentes~{n_comp} "
            f"clip={state['clip_frac']:.3f} eixo={axn} from_max={state['from_max']} "
            f"dist_cam~{dist:.4f}",
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
            "  pip install -r requirements-visualizacao.txt\n"
            "(ficheiro na raiz do repo; no windows com caminhos longos desativados "
            "pode falhar — veja comentarios nesse ficheiro.)\n"
            "alternativa: visualizador web (three.js) ou blender.",
            file=sys.stderr,
        )
        return 2

    try:
        mesh = o3d.io.read_triangle_mesh(
            str(path), enable_post_processing=True, print_progress=False
        )
        if mesh.is_empty() or len(mesh.triangles) == 0:
            print(
                "erro: malha vazia apos leitura. o ficheiro pode ter so primitivas nao triangulares. "
                "tente exportar do blender com triangulate faces ou use .stl.",
                file=sys.stderr,
            )
            return 3
        _style_mesh(mesh)

        bbox = mesh.get_axis_aligned_bounding_box()
        center = np.asarray(bbox.get_center(), dtype=np.float64)
        extent = float(np.max(bbox.get_extent()))
        if extent < 1e-12:
            print("erro: caixa limitadora degenerada (malha sem volume aparente).", file=sys.stderr)
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
        if legacy:
            _run_legacy_viewer(o3d, path, mesh_orig, mesh, center, mn, mx, n_vert, n_tri, n_comp)
        else:
            try:
                _run_draw_viewer(
                    o3d, path, mesh_orig, center, mn, mx, n_vert, n_tri, n_comp
                )
            except Exception as e:
                print(
                    f"aviso: viewer draw falhou ({e}); a tentar modo legacy.",
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
