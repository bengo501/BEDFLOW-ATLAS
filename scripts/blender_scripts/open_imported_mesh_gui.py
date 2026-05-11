# -*- coding: utf-8 -*-
"""
abre o blender em modo gui com uma malha ou cena importada automaticamente.

uso (a partir do bed wizard ou terminal):
  blender --python open_imported_mesh_gui.py -- /caminho/absoluto/modelo.stl

fluxo para formatos que nao sao .blend:
  1) novo projeto — wm.read_homefile (equivalente a ficheiro > novo)
  2) limpar objectos por omissao do startup
  3) importar o ficheiro escolhido (stl/obj/ply/gltf/glb)
  4) enquadrar a vista na malha

para .blend: abre a cena existente (open_mainfile), sem passo de importacao.

compatibilidade: operadores modernos (blender 4.x) e fallback para api antiga.
"""
from __future__ import annotations

import sys
from pathlib import Path

import bpy


def _argv_mesh_path() -> Path:
    if "--" not in sys.argv:
        print("bedflow: use -- antes do caminho do ficheiro", file=sys.stderr)
        sys.exit(1)
    i = sys.argv.index("--") + 1
    if i >= len(sys.argv):
        print("bedflow: caminho em falta apos --", file=sys.stderr)
        sys.exit(1)
    return Path(sys.argv[i]).expanduser().resolve()


def _clear_default_scene() -> None:
    if bpy.ops.object.mode_set.poll():
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def _ensure_new_blend_project() -> None:
    """reinicia para um .blend novo (startup de fabrica), depois esvazia objectos."""
    try:
        # ficheiro > novo — cena coerente antes de importar malha externa
        bpy.ops.wm.read_homefile(app_template="")
    except Exception as ex:
        print(
            f"bedflow: aviso read_homefile ignorado ({ex}); a continuar com a cena actual.",
            file=sys.stderr,
        )
    _clear_default_scene()


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
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
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
        for fp in (fp_posix, fp_native):
            try:
                bpy.ops.wm.obj_import(filepath=fp)
                return
            except TypeError:
                try:
                    bpy.ops.wm.obj_import(
                        filepath=fp,
                        directory=path.parent.as_posix(),
                        files=[path.name],
                    )
                except Exception:
                    continue
            except Exception:
                continue
        try:
            bpy.ops.wm.obj_import(filepath=fp_native)
            return
        except Exception:
            pass
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


def main() -> None:
    path = _argv_mesh_path()
    if not path.is_file():
        print(f"bedflow: ficheiro inexistente: {path}", file=sys.stderr)
        sys.exit(1)

    ext = path.suffix.lower()
    fp = str(path.resolve())

    if ext == ".blend":
        bpy.ops.wm.open_mainfile(filepath=fp)
        print(f"bedflow: cena aberta {fp}")
        return

    _ensure_new_blend_project()

    try:
        if ext == ".stl":
            _import_stl(fp)
        elif ext == ".obj":
            _import_obj(fp)
        elif ext == ".ply":
            _import_ply(fp)
        elif ext in (".gltf", ".glb"):
            _import_gltf(fp)
        else:
            print(f"bedflow: extensao nao suportada pelo script: {ext}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"bedflow: falha na importacao: {e}", file=sys.stderr)
        sys.exit(1)

    _frame_meshes()
    print(f"bedflow: modelo importado {path.name} ({ext})")


if __name__ == "__main__":
    main()
