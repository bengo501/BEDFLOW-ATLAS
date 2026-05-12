"""
janela open3d.gui minimalista: scene + sidebar + overlays 2d fixos.
sem o3d.visualization.draw (evita painel tipo mini-blender com shaders/ibl avancados).
"""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from mesh_viewer.camera_controller import setup_orbit_camera
from mesh_viewer.cut_controller import CutController
from mesh_viewer.geometry_core import bbox_lineset, style_mesh_rgb, wire_lineset_from_mesh
from mesh_viewer.mesh_visibility_controller import MeshVisibilityController
from mesh_viewer.ui_overlay_manager import camera_overlay_lines, model_overlay_lines


def run_scientific_viewer(
    o3d: Any,
    path: Path,
    mesh_orig: Any,
    mn: np.ndarray,
    mx: np.ndarray,
    center: np.ndarray,
    n_vert: int,
    n_tri: int,
    n_comp: int,
    bed_meta: Optional[Dict[str, Any]] = None,
) -> None:
    BedflowScientificViewer(
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
    ).run()


class BedflowScientificViewer:
    _NAME_MESH = "bedflow_mesh"
    _NAME_WIRE = "bedflow_wire"
    _NAME_BBOX = "bedflow_bbox"

    def __init__(
        self,
        o3d: Any,
        path: Path,
        mesh_orig: Any,
        mn: np.ndarray,
        mx: np.ndarray,
        center: np.ndarray,
        n_vert: int,
        n_tri: int,
        n_comp: int,
        bed_meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.o3d = o3d
        self.path = path
        self.mesh_orig = copy.deepcopy(mesh_orig)
        self.mn = np.asarray(mn, dtype=np.float64)
        self.mx = np.asarray(mx, dtype=np.float64)
        self.center = np.asarray(center, dtype=np.float64)
        self.n_vert = n_vert
        self.n_tri = n_tri
        self.n_comp = n_comp
        self.ext = self.mx - self.mn
        self.bed_meta = bed_meta

        self._cut = CutController()
        self._mvp = MeshVisibilityController()
        self.alpha = 1.0
        self.mesh_rgb = (0.22, 0.48, 0.78)
        self.ibl_intensity = 38000
        self.show_ground = True

        self._tick_acc = 0.0
        self._last_cam_sig = ""
        self._model_bounds = self.mesh_orig.get_axis_aligned_bounding_box()

        import open3d.visualization.gui as gui
        import open3d.visualization.rendering as rendering

        self.gui = gui
        self.rendering = rendering

        self._mesh_mat = self._make_mesh_material()
        self._bbox_mat = self._make_bbox_material()
        self._wire_mat = self._make_wire_material()

        self.window: Any = None
        self.scene_widget: Any = None
        self._sidebar: Any = None
        self._overlay_model: Any = None
        self._overlay_cam: Any = None
        self._lbl_model_lines: List[Any] = []
        self._lbl_cam_lines: List[Any] = []

        self._slider_clip: Any = None
        self._slider_alpha: Any = None
        self._slider_ibl: Any = None
        self._color_mesh: Any = None

    def _make_mesh_material(self) -> Any:
        mat = self.rendering.MaterialRecord()
        mat.shader = (
            "defaultLitTransparency" if self.alpha < 0.995 else "defaultLit"
        )
        mat.base_color = (*self.mesh_rgb, float(self.alpha))
        return mat

    def _make_bbox_material(self) -> Any:
        mat = self.rendering.MaterialRecord()
        mat.shader = "unlitLine"
        mat.base_color = (0.95, 0.45, 0.12, 1.0)
        mat.line_width = 2.0
        return mat

    def _make_wire_material(self) -> Any:
        mat = self.rendering.MaterialRecord()
        mat.shader = "unlitLine"
        mat.base_color = (0.35, 0.38, 0.42, 1.0)
        mat.line_width = 2.0
        return mat

    def _cropped(self) -> Any:
        return self._cut.cropped_mesh(self.mesh_orig)

    def _refresh_mesh_material(self) -> None:
        try:
            self._mesh_mat.shader = (
                "defaultLitTransparency" if self.alpha < 0.995 else "defaultLit"
            )
        except Exception:
            self._mesh_mat.shader = "defaultLit"
        self._mesh_mat.base_color = (*self.mesh_rgb, float(self.alpha))

    def _remove_geom(self, name: str) -> None:
        try:
            self.scene_widget.scene.remove_geometry(name)
        except Exception:
            pass

    def _sync_scene(self) -> None:
        sc = self.scene_widget.scene
        m = self._cropped()
        style_mesh_rgb(m, self.mesh_rgb)

        self._remove_geom(self._NAME_MESH)
        self._remove_geom(self._NAME_WIRE)

        show_solid = self._mvp.show_mesh
        show_wire_geom = self._mvp.wireframe

        if show_solid:
            self._refresh_mesh_material()
            sc.add_geometry(
                self._NAME_MESH,
                m,
                self._mesh_mat,
                add_downsampled_copy_for_fast_rendering=False,
            )
            sc.show_geometry(self._NAME_MESH, True)

        if show_wire_geom:
            wl = wire_lineset_from_mesh(m)
            if wl is not None:
                sc.add_geometry(
                    self._NAME_WIRE,
                    wl,
                    self._wire_mat,
                    add_downsampled_copy_for_fast_rendering=False,
                )
                sc.show_geometry(self._NAME_WIRE, True)

        self._remove_geom(self._NAME_BBOX)
        if self._mvp.show_bbox:
            bb = bbox_lineset(self.mesh_orig)
            sc.add_geometry(
                self._NAME_BBOX,
                bb,
                self._bbox_mat,
                add_downsampled_copy_for_fast_rendering=False,
            )
            sc.show_geometry(self._NAME_BBOX, True)

        self._apply_environment()
        self._update_model_overlay_text()
        self.scene_widget.force_redraw()

    def _setup_camera_from_bounds(self) -> None:
        setup_orbit_camera(self.scene_widget, self._model_bounds, self.center, 60.0)

    def _apply_environment(self) -> None:
        sc = self.scene_widget.scene
        inner = sc.scene
        inner.enable_indirect_light(True)
        inner.set_indirect_light_intensity(float(self.ibl_intensity))
        sc.show_skybox(False)
        gp = self.rendering.Scene.GroundPlane
        sc.show_ground_plane(bool(self.show_ground), gp.XZ)

    def _section(self, title: str) -> Any:
        v = self.gui.CollapsableVert(title, 0.25 * self.em, self.gui.Margins(self.em, 0, 0, 0))
        v.set_is_open(True)
        return v

    def _dark_panel(self) -> Any:
        p = self.gui.Vert(4, self.gui.Margins(8, 8, 8, 8))
        p.background_color = self.gui.Color(0.06, 0.07, 0.09, 0.42)
        return p

    def _lbl(self, text: str, mono: bool = True) -> Any:
        lab = self.gui.Label(text)
        if mono:
            try:
                lab.font_id = self.gui.FontId.MONOSPACE
            except Exception:
                pass
        lab.text_color = self.gui.Color(0.92, 0.93, 0.95, 1.0)
        return lab

    def run(self) -> None:
        app = self.gui.Application.instance
        app.initialize()

        self.window = app.create_window(
            f"bedflow — inspeccao geometrica — {self.path.name}", 1280, 820
        )
        w = self.window
        self.em = float(w.theme.font_size)
        w.set_on_layout(self._on_layout)
        w.set_on_tick_event(self._on_tick)

        self.scene_widget = self.gui.SceneWidget()
        self.scene_widget.scene = self.rendering.Open3DScene(w.renderer)
        try:
            self.scene_widget.set_view_controls(
                self.gui.SceneWidget.Controls.ROTATE_CAMERA_SPHERE
            )
        except Exception:
            self.scene_widget.set_view_controls(
                self.gui.SceneWidget.Controls.ROTATE_CAMERA
            )

        self._build_sidebar()
        self._build_overlays()

        w.add_child(self.scene_widget)
        w.add_child(self._sidebar)
        w.add_child(self._overlay_model)
        w.add_child(self._overlay_cam)

        self._sync_scene()
        self._setup_camera_from_bounds()
        app.run()

    def _build_overlays(self) -> None:
        self._overlay_model = self._dark_panel()
        t = self._lbl("modelo", mono=True)
        self._overlay_model.add_child(t)
        for _ in range(12):
            lb = self._lbl("")
            self._lbl_model_lines.append(lb)
            self._overlay_model.add_child(lb)

        self._overlay_cam = self._dark_panel()
        t2 = self._lbl("camera", mono=True)
        self._overlay_cam.add_child(t2)
        for _ in range(8):
            lb = self._lbl("")
            self._lbl_cam_lines.append(lb)
            self._overlay_cam.add_child(lb)

        self._update_model_overlay_text()
        self._update_camera_overlay_text()

    def _update_model_overlay_text(self) -> None:
        lines = model_overlay_lines(
            self.path,
            self.n_vert,
            self.n_tri,
            self.n_comp,
            self.ext,
            self._cut,
            bed_meta=self.bed_meta,
            max_lines=len(self._lbl_model_lines),
        )
        for i in range(len(self._lbl_model_lines)):
            self._lbl_model_lines[i].text = lines[i] if i < len(lines) else ""

    def _update_camera_overlay_text(self) -> None:
        lines = camera_overlay_lines(self.scene_widget)
        if lines is None:
            return
        for i in range(len(self._lbl_cam_lines)):
            self._lbl_cam_lines[i].text = lines[i] if i < len(lines) else ""

    def _on_tick(self) -> bool:
        self._tick_acc += 1.0
        if self._tick_acc < 8.0:
            return False
        self._tick_acc = 0.0
        try:
            cam = self.scene_widget.scene.camera
            sig = str(np.asarray(cam.get_view_matrix()).round(4).tolist())
            if sig != self._last_cam_sig:
                self._last_cam_sig = sig
                self._update_camera_overlay_text()
                return True
        except Exception:
            return False
        return False

    def _build_sidebar(self) -> None:
        g = self.gui
        em = self.em
        self._sidebar = g.Vert(6, g.Margins(0.35 * em, 0.35 * em, 0.35 * em, 0.35 * em))
        self._sidebar.background_color = g.Color(0.11, 0.11, 0.13, 0.94)

        sec_m = self._section("modelo")
        self._slider_alpha = g.Slider(g.Slider.DOUBLE)
        self._slider_alpha.set_limits(0.05, 1.0)
        self._slider_alpha.double_value = self.alpha
        self._slider_alpha.set_on_value_changed(self._on_alpha)
        sec_m.add_child(g.Label("opacidade (1 = opaco, 0.05 = quase invisivel)"))
        sec_m.add_child(self._slider_alpha)

        self._color_mesh = g.ColorEdit()
        self._color_mesh.color_value = g.Color(*self.mesh_rgb, 1.0)
        self._color_mesh.set_on_value_changed(self._on_mesh_color)
        sec_m.add_child(g.Label("cor da malha"))
        sec_m.add_child(self._color_mesh)

        cb_mesh = g.Checkbox("mostrar malha")
        cb_mesh.checked = True
        cb_mesh.set_on_checked(self._on_show_mesh)
        sec_m.add_child(cb_mesh)

        cb_wire = g.Checkbox("arestas (wire sobre a malha)")
        cb_wire.checked = False
        cb_wire.set_on_checked(self._on_wire)
        sec_m.add_child(cb_wire)

        cb_bb = g.Checkbox("bounding box")
        cb_bb.checked = False
        cb_bb.set_on_checked(self._on_bbox)
        sec_m.add_child(cb_bb)

        self._sidebar.add_child(sec_m)

        sec_c = self._section("corte (crop)")
        self._slider_clip = g.Slider(g.Slider.DOUBLE)
        self._slider_clip.set_limits(0.0, 0.95)
        self._slider_clip.double_value = 0.0
        self._slider_clip.set_on_value_changed(self._on_clip_slider)
        sec_c.add_child(g.Label("intensidade do corte (0 = nenhum)"))
        sec_c.add_child(self._slider_clip)

        ax_row = g.Horiz(0.25 * em)
        for ax, idx in (("x", 0), ("y", 1), ("z", 2)):
            b = g.Button(ax)

            def _axis_factory(j: int):
                return lambda: self._set_axis(j)

            b.set_on_clicked(_axis_factory(idx))
            ax_row.add_child(b)
        sec_c.add_child(g.Label("eixo"))
        sec_c.add_child(ax_row)

        side_row = g.Horiz(0.25 * em)
        bmax = g.Button("lado max")
        bmax.set_on_clicked(lambda: self._set_side(True))
        bmin = g.Button("lado min")
        bmin.set_on_clicked(lambda: self._set_side(False))
        side_row.add_child(bmax)
        side_row.add_child(bmin)
        sec_c.add_child(side_row)

        row = g.Horiz(0.25 * em)
        bdec = g.Button(" - ")
        bdec.set_on_clicked(lambda: self._nudge_clip(-0.02))
        binc = g.Button(" + ")
        binc.set_on_clicked(lambda: self._nudge_clip(0.02))
        brst = g.Button("reset")
        brst.set_on_clicked(lambda: self._reset_clip())
        row.add_child(bdec)
        row.add_child(binc)
        row.add_child(brst)
        sec_c.add_child(row)
        self._sidebar.add_child(sec_c)

        sec_cam = self._section("camera")
        brc = g.Button("reset camera")
        brc.set_on_clicked(lambda: self._reset_camera())
        sec_cam.add_child(brc)
        self._sidebar.add_child(sec_cam)

        sec_env = self._section("ambiente")
        self._slider_ibl = g.Slider(g.Slider.INT)
        self._slider_ibl.set_limits(5000, 90000)
        self._slider_ibl.int_value = int(self.ibl_intensity)
        self._slider_ibl.set_on_value_changed(self._on_ibl)
        sec_env.add_child(g.Label("luminosidade ibl (sem skybox)"))
        sec_env.add_child(self._slider_ibl)

        cb_gr = g.Checkbox("plano de grelha (xz)")
        cb_gr.checked = True
        cb_gr.set_on_checked(self._on_ground)
        sec_env.add_child(cb_gr)

        self._sidebar.add_child(sec_env)

        sec_h = self._section("ajuda")
        bh = g.Button("ajuda / leitura")
        bh.set_on_clicked(lambda: self._help())
        sec_h.add_child(bh)
        self._sidebar.add_child(sec_h)

    def _on_alpha(self, v: float) -> None:
        self.alpha = float(v)
        self._refresh_mesh_material()
        self._sync_scene()

    def _on_mesh_color(self, c: Any) -> None:
        self.mesh_rgb = (float(c.red), float(c.green), float(c.blue))
        self._sync_scene()

    def _on_show_mesh(self, on: bool) -> None:
        self._mvp.show_mesh = bool(on)
        self._sync_scene()

    def _on_wire(self, on: bool) -> None:
        self._mvp.wireframe = bool(on)
        self._sync_scene()

    def _on_bbox(self, on: bool) -> None:
        self._mvp.show_bbox = bool(on)
        self._sync_scene()

    def _on_clip_slider(self, v: float) -> None:
        self._cut.set_clip(float(v))
        self._sync_scene()

    def _nudge_clip(self, dv: float) -> None:
        self._cut.nudge(dv)
        if self._slider_clip is not None:
            self._slider_clip.double_value = self._cut.clip_frac
        self._sync_scene()

    def _reset_clip(self) -> None:
        self._cut.reset()
        if self._slider_clip is not None:
            self._slider_clip.double_value = 0.0
        self._sync_scene()

    def _set_axis(self, i: int) -> None:
        self._cut.set_axis(i)
        self._sync_scene()

    def _set_side(self, fm: bool) -> None:
        self._cut.from_max = bool(fm)
        self._sync_scene()

    def _reset_camera(self) -> None:
        self._setup_camera_from_bounds()
        self._update_camera_overlay_text()
        self.scene_widget.force_redraw()

    def _on_ibl(self, v: int) -> None:
        self.ibl_intensity = int(v)
        self._apply_environment()
        self.scene_widget.force_redraw()

    def _on_ground(self, on: bool) -> None:
        self.show_ground = bool(on)
        self._apply_environment()
        self.scene_widget.force_redraw()

    def _help(self) -> None:
        self.window.show_message_box(
            "bedflow — inspeccao geometrica",
            "este visualizador nao edita a malha (sem tampas, sem booleans).\n\n"
            "corte: crop por caixa alinhada ao longo do eixo escolhido; "
            "remove volume a partir do extremo max ou min.\n\n"
            "opacidade: controla alpha da malha (1 = solido). em malhas semi-"
            "transparentes usa-se o shader defaultLitTransparency.\n\n"
            "arestas: linhas sobre a malha (ou so linhas se desligar a malha); "
            "em ficheiros muito grandes as arestas usam uma versao decimada "
            "apenas para visualizacao.\n\n"
            "malha unica stl/obj: parede e particulas fundidas nao se separam sem ficheiro dedicado.\n\n"
            "parametros do leito: coloque meuficheiro.bed.json junto ao .stl ou use --bed-json.\n\n"
            "atalhos na vista: trackball open3d (ver painel camera) — "
            "orbita com botao esquerdo; no blender o mesmo gesto e tipicamente "
            "o botao do meio. duplo clique esquerdo recentra o pivot num ponto.",
        )

    def _on_layout(self, ctx: Any) -> None:
        r = self.window.content_rect
        em = ctx.theme.font_size
        sidebar_w = int(round(15.5 * em))
        margin = int(round(0.5 * em))

        scene_rect = self.gui.Rect(r.x, r.y, r.width - sidebar_w, r.height)
        self.scene_widget.frame = scene_rect

        self._sidebar.frame = self.gui.Rect(
            r.get_right() - sidebar_w, r.y, sidebar_w, r.height
        )

        ow = int(min(max(232, int(round(22.5 * em))), scene_rect.width * 0.32))
        line_px = max(13, int(round(1.06 * em)))
        oh_m = int(round(10 + (len(self._lbl_model_lines) + 1) * line_px * 0.92))
        oh_m = min(oh_m, int(scene_rect.height * 0.38))
        self._overlay_model.frame = self.gui.Rect(
            scene_rect.x + margin, scene_rect.y + margin, ow, oh_m
        )

        oh_c = int(round(10 + (len(self._lbl_cam_lines) + 1) * line_px * 0.92))
        oh_c = min(oh_c, int(scene_rect.height * 0.30))
        self._overlay_cam.frame = self.gui.Rect(
            scene_rect.x + margin,
            scene_rect.get_bottom() - margin - oh_c,
            ow,
            oh_c,
        )
