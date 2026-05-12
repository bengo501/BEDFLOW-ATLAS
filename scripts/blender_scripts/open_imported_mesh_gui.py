# -*- coding: utf-8 -*-
"""
abre o blender em modo gui com uma malha ou cena importada automaticamente.

uso (a partir do bed wizard ou terminal):
  blender --python open_imported_mesh_gui.py -- /caminho/absoluto/modelo.stl

fluxo para formatos que nao sao .blend:
  1) limpar a cena por omissao (api de dados, sem bpy.ops.delete no arranque)
  2) importar: em modo gui usa timer persistente; em --background corre na hora
  3) enquadrar a vista na malha (operadores com poll defensivo)

erros detalham-se no ficheiro bedflow_blender_import.log na pasta temporaria do sistema (ex.: %TEMP% no windows).

para .blend: abre a cena existente (open_mainfile), sem passo de importacao.

compatibilidade: operadores modernos (blender 4.x) e fallback para api antiga.
"""
from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

_LOG = Path(os.environ.get("TEMP", os.environ.get("TMP", "."))) / "bedflow_blender_import.log"


def _log_pre_bpy(msg: str) -> None:
    try:
        with open(_LOG, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


_log_pre_bpy("--- modulo open_imported_mesh_gui (antes de import bpy) ---")

import bpy  # noqa: E402


def _log(msg: str) -> None:
    try:
        with open(_LOG, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


_MESH_EXTS = frozenset({".stl", ".obj", ".ply", ".gltf", ".glb", ".blend"})


def _argv_mesh_path() -> Path:
    if "--" in sys.argv:
        i = sys.argv.index("--") + 1
        if i < len(sys.argv):
            return Path(sys.argv[i]).expanduser().resolve()
    for arg in reversed(sys.argv[1:]):
        p = Path(arg).expanduser()
        suf = p.suffix.lower()
        if suf in _MESH_EXTS and p.is_file():
            return p.resolve()
    print(
        "bedflow: caminho da malha em falta. use:\n"
        "  blender --python .../open_imported_mesh_gui.py -- caminho/modelo.obj\n"
        f"argv actual: {sys.argv!r}",
        file=sys.stderr,
    )
    raise SystemExit(1)


def _clear_default_scene() -> None:
    """
    esvazia objectos sem bpy.ops.* — no arranque com --python o poll dos operadores
    falha muitas vezes (sem janela 3d), o que deixa excepções e o blender fecha.
    """
    sc = bpy.context.scene
    if sc is None:
        return
    for ob in list(sc.objects):
        try:
            bpy.data.objects.remove(ob, do_unlink=True)
        except Exception:
            pass


def _ensure_new_blend_project() -> None:
    """
    esvazia a cena actual sem read_factory_settings nem read_homefile: esses
    operadores invalidam bpy.context (janela/area) no arranque com --python,
    fazendo falhar import/view3d e muitas vezes fechar o blender no windows.
    """
    _clear_default_scene()
    for nm in ("Cube", "Cube.001", "Light", "Camera"):
        ob = bpy.data.objects.get(nm)
        if ob is not None:
            try:
                bpy.data.objects.remove(ob, do_unlink=True)
            except Exception:
                pass


def _temp_override_view3d():
    """contexto VIEW_3D para operadores view3d (copia minima do leito_extracao)."""
    wm = bpy.context.window_manager
    if not wm.windows:
        return None, None, None
    win = wm.windows[0]
    for area in win.screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "WINDOW":
                    return (
                        dict(
                            window=win,
                            screen=win.screen,
                            area=area,
                            region=region,
                            scene=bpy.context.scene,
                            view_layer=bpy.context.view_layer,
                        ),
                        None,
                        None,
                    )
    area = win.screen.areas[0]
    prev = area.type
    area.type = "VIEW_3D"
    region = None
    for r in area.regions:
        if r.type == "WINDOW":
            region = r
            break
    if region is None:
        area.type = prev
        return None, None, None
    return (
        dict(
            window=win,
            screen=win.screen,
            area=area,
            region=region,
            scene=bpy.context.scene,
            view_layer=bpy.context.view_layer,
        ),
        area,
        prev,
    )


def _frame_meshes() -> None:
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        return
    try:
        if bpy.ops.object.select_all.poll():
            bpy.ops.object.select_all(action="DESELECT")
        for o in meshes:
            o.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
    except Exception:
        pass
    ovr, promoted, prev = _temp_override_view3d()
    if ovr is None:
        return
    try:
        with bpy.context.temp_override(**ovr):
            bpy.ops.view3d.view_selected()
    except Exception:
        pass
    finally:
        if promoted is not None and prev is not None:
            promoted.type = prev


def _import_stl(filepath: str) -> None:
    path = Path(filepath).expanduser().resolve()
    fp_posix = path.as_posix()
    fp_native = str(path)
    wm = getattr(bpy.ops, "wm", None)
    if wm is not None and hasattr(wm, "stl_import"):
        for fp in (fp_posix, fp_native):
            try:
                bpy.ops.wm.stl_import(filepath=fp)
                return
            except Exception:
                continue
    if hasattr(bpy.ops.import_mesh, "stl"):
        for fp in (fp_posix, fp_native):
            try:
                bpy.ops.import_mesh.stl(filepath=fp)
                return
            except Exception:
                continue
    raise RuntimeError("importacao stl nao disponivel nesta versao do blender")


def _import_obj(filepath: str) -> None:
    path = Path(filepath).expanduser().resolve()
    if not path.is_file():
        raise RuntimeError(f"ficheiro obj inexistente: {path}")
    fp_posix = path.as_posix()
    fp_native = str(path)
    wm = getattr(bpy.ops, "wm", None)
    if wm is not None and hasattr(wm, "obj_import"):
        try:
            bpy.ops.wm.obj_import(filepath=fp_native)
            return
        except Exception:
            pass
        try:
            bpy.ops.wm.obj_import(filepath=fp_posix)
            return
        except Exception:
            pass
        file_dict = {"name": path.name}
        dir_native = str(path.parent)
        dir_posix = path.parent.as_posix()
        for directory in (dir_native, dir_posix):
            for files in ([file_dict], [path.name]):
                try:
                    bpy.ops.wm.obj_import(directory=directory, files=files)
                    return
                except Exception:
                    try:
                        bpy.ops.wm.obj_import(
                            filepath=fp_native, directory=directory, files=files
                        )
                        return
                    except Exception:
                        pass
        for fp in (fp_native, fp_posix):
            try:
                bpy.ops.wm.obj_import(filepath=fp)
                return
            except Exception:
                continue
        for combo in (
            dict(filepath=fp_native, directory=dir_native, files=[file_dict]),
            dict(filepath=fp_native, directory=dir_native, files=[path.name]),
            dict(filepath=fp_posix, directory=dir_posix, files=[file_dict]),
        ):
            try:
                bpy.ops.wm.obj_import(**combo)
                return
            except Exception:
                continue
    if hasattr(bpy.ops.import_scene, "obj"):
        for fp in (fp_posix, fp_native):
            try:
                bpy.ops.import_scene.obj(filepath=fp)
                return
            except Exception:
                continue
    raise RuntimeError("importacao obj nao disponivel nesta versao do blender")


def _import_ply(filepath: str) -> None:
    wm = getattr(bpy.ops, "wm", None)
    if wm is not None and hasattr(wm, "ply_import"):
        bpy.ops.wm.ply_import(filepath=filepath)
        return
    if hasattr(bpy.ops.import_mesh, "ply"):
        bpy.ops.import_mesh.ply(filepath=filepath)
        return
    raise RuntimeError("importacao ply nao disponivel nesta versao do blender")


def _import_gltf(filepath: str) -> None:
    if hasattr(bpy.ops.import_scene, "gltf"):
        bpy.ops.import_scene.gltf(filepath=filepath)
        return
    raise RuntimeError(
        "importacao gltf/glb: operador import_scene.gltf nao encontrado "
        "(instale o addon oficial gltf se necessario)"
    )


def _import_mesh_extension(ext: str, fp: str) -> None:
    if ext == ".stl":
        _import_stl(fp)
    elif ext == ".obj":
        _import_obj(fp)
    elif ext == ".ply":
        _import_ply(fp)
    elif ext in (".gltf", ".glb"):
        _import_gltf(fp)
    else:
        raise RuntimeError(f"extensao nao suportada pelo script: {ext}")


def main() -> None:
    _log("--- bedflow open_imported_mesh_gui ---")
    _log("argv: " + repr(sys.argv))
    path = _argv_mesh_path()
    if not path.is_file():
        msg = f"bedflow: ficheiro inexistente: {path}"
        print(msg, file=sys.stderr)
        _log(msg)
        sys.exit(1)

    ext = path.suffix.lower()
    fp = str(path.resolve())

    if ext == ".blend":
        try:
            bpy.ops.wm.open_mainfile(filepath=fp)
        except Exception as e:
            tb = traceback.format_exc()
            print(f"bedflow: falha ao abrir .blend: {e}", file=sys.stderr)
            _log(f"falha open_mainfile: {e}\n{tb}")
            sys.exit(1)
        print(f"bedflow: cena aberta {fp}")
        _log(f"open_mainfile ok: {fp}")
        return

    def _deferred_import() -> None:
        try:
            _ensure_new_blend_project()
            _import_mesh_extension(ext, fp)
        except Exception as e:
            tb = traceback.format_exc()
            print(f"bedflow: falha na importacao: {e}", file=sys.stderr)
            _log(f"falha na importacao: {e}\n{tb}")
            return None
        try:
            _frame_meshes()
        except Exception as e:
            _log(f"aviso enquadrar vista: {e}\n{traceback.format_exc()}")
        print(f"bedflow: modelo importado {path.name} ({ext})")
        _log(f"import ok: {path.name} ({ext})")
        return None

    if bpy.app.background:
        _log("modo background: importacao imediata (sem timer)")
        _deferred_import()
    else:
        try:
            bpy.app.timers.register(
                _deferred_import, first_interval=0.2, persistent=True
            )
        except TypeError:
            bpy.app.timers.register(_deferred_import, first_interval=0.2)
        _log(
            "importacao agendada (timer 0.2s, persistent) para depois da gui estar pronta"
        )


if __name__ == "__main__":
    main()
