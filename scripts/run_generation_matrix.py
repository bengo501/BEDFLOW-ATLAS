#!/usr/bin/env python3
"""
runner de geração de modelos de leito — todos os tipos, nos dois backends.

executa uma matriz de casos (full_3d, modos de interior m1/m2/m3, corte 2D,
estatístico 2D, tipos de partícula, métodos de empacotamento e formatos de
export) no **motor python** e/ou no **blender**, individualmente ou todos de uma
vez.

uso:
    python scripts/run_generation_matrix.py --list
    python scripts/run_generation_matrix.py --case m3_cheese --backend python
    python scripts/run_generation_matrix.py --all --backend both
    python scripts/run_generation_matrix.py --all --backend python
    python scripts/run_generation_matrix.py --case slice2d_compare --backend blender

saída em generated/3d/generation_matrix/<backend>/<caso>/
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
import subprocess
import sys
import time
from glob import glob
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_REPO = Path(__file__).resolve().parents[1]
_PM = _REPO / "scripts" / "python_modeling"
_BS = _REPO / "scripts" / "blender_scripts"
for _p in (str(_PM), str(_BS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# --------------------------------------------------------------------------- #
# definição dos casos (JSON estruturado .bed.json — serve aos dois backends)
# --------------------------------------------------------------------------- #
_BASE: Dict[str, Any] = {
    "geometry_mode": "full_3d",
    "bed": {
        "diameter": 0.05,
        "height": 0.06,
        "wall_thickness": 0.003,
        "internal_cylinder_mode": "hollow_boolean_applied",
        "visibility": {
            "show_outer_cylinder": True,
            "show_internal_cylinder": False,
            "show_particles": True,
        },
    },
    "particles": {"kind": "sphere", "count": 12, "diameter": 0.006, "seed": 3},
    "lids": {"bottom_thickness": 0.004, "top_thickness": 0.004},
    "packing": {
        "method": "hexagonal_3d",
        "gap": 0.0005,
        "strict_validation": False,
        "mesh_segmentos": 18,
    },
    "export": {"formats": ["stl_binary"]},
}


def _case(overrides: Dict[str, Any]) -> Dict[str, Any]:
    data = copy.deepcopy(_BASE)
    for k, v in overrides.items():
        if isinstance(v, dict) and isinstance(data.get(k), dict):
            data[k] = {**data[k], **v}
        else:
            data[k] = v
    return data


# cada caso: (descrição, dados, python_ok, blender_ok)
CASES: Dict[str, Tuple[str, Dict[str, Any], bool, bool]] = {
    "full3d_sphere_hex": (
        "full_3d, esferas, hexagonal_3d",
        _case({}),
        True, True,
    ),
    "full3d_cube_spherical": (
        "full_3d, cubos, spherical_packing",
        _case({"particles": {"kind": "cube"}, "packing": {"method": "spherical_packing"}}),
        True, True,
    ),
    "full3d_cylinder_hex": (
        "full_3d, cilindros, hexagonal_3d",
        _case({"particles": {"kind": "cylinder"}}),
        True, True,
    ),
    "full3d_rigidbody": (
        "full_3d, esferas, rigid_body (DEM/Bullet)",
        _case({"particles": {"count": 12}, "packing": {"method": "rigid_body", "dem": {"steps": 3000}}}),
        True, True,
    ),
    "m2_solid_embedded": (
        "m2: interior sólido + partículas embutidas",
        _case({"bed": {"internal_cylinder_mode": "internal_cylinder_visible_no_boolean",
                       "visibility": {"show_internal_cylinder": True, "show_particles": True}}}),
        True, True,
    ),
    "m3_cheese": (
        "m3: interior sólido furado (queijo)",
        _case({"bed": {"internal_cylinder_mode": "solid_internal_cylinder_with_particle_holes",
                       "visibility": {"show_internal_cylinder": True, "show_particles": False}}}),
        True, True,
    ),
    "slice2d": (
        "corte 2D (pseudo_2d_thin_slice)",
        _case({"geometry_mode": "pseudo_2d_thin_slice",
               "slice": {"slice_enabled": True, "slice_axis": "y", "slice_thickness": 0.004}}),
        True, True,
    ),
    "slice2d_compare": (
        "corte 2D + validação 2D/3D (compare_mode=all)",
        _case({"geometry_mode": "pseudo_2d_thin_slice",
               "slice": {"slice_enabled": True, "slice_axis": "y", "slice_thickness": 0.004,
                         "compare_mode": "all"}}),
        True, True,
    ),
    "statistical2d": (
        "reconstrução estatística 2D (só motor python)",
        _case({"geometry_mode": "pseudo_2d_statistical",
               "statistical_2d": {"target_porosity": 0.4, "tolerance": 0.05, "max_attempts": 40,
                                  "slice_thickness": 0.004, "seed": 3}}),
        True, False,
    ),
    "export_multiformat": (
        "full_3d exportando stl + obj + glb",
        _case({"export": {"formats": ["stl_binary", "obj", "glb"]}}),
        True, True,
    ),
}


# --------------------------------------------------------------------------- #
# execução
# --------------------------------------------------------------------------- #
def _find_blender() -> Optional[str]:
    found = shutil.which("blender")
    if found:
        return found
    import os

    env = os.environ.get("BEDFLOW_BLENDER_EXE")
    if env and Path(env).is_file():
        return env
    for pat in (
        r"C:\Program Files\Blender Foundation\Blender*\blender.exe",
        r"C:\Program Files (x86)\Blender Foundation\Blender*\blender.exe",
    ):
        hits = sorted(glob(pat))
        if hits:
            return hits[-1]
    return None


def _outputs(out_dir: Path) -> List[str]:
    return sorted(p.name for p in out_dir.iterdir()) if out_dir.is_dir() else []


def run_python(name: str, data: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{name}.bed.json"
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    out_stl = out_dir / "model.stl"
    t0 = time.perf_counter()
    try:
        from pure_generation import generate_packed_bed_stl

        generate_packed_bed_stl(json_path, out_stl, max_passos=3000)
        ok = out_stl.is_file() and out_stl.stat().st_size > 80
        return {"status": "OK" if ok else "FAIL", "elapsed": time.perf_counter() - t0,
                "files": _outputs(out_dir), "error": None if ok else "stl vazio/ausente"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "FAIL", "elapsed": time.perf_counter() - t0,
                "files": _outputs(out_dir), "error": f"{type(exc).__name__}: {exc}"}


def run_blender(name: str, data: Dict[str, Any], out_dir: Path, blender: str) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{name}.bed.json"
    bdata = copy.deepcopy(data)
    bdata["generation_backend"] = "blender"
    json_path.write_text(json.dumps(bdata, indent=2), encoding="utf-8")
    out_blend = out_dir / "model.blend"
    script = _BS / "leito_extracao.py"
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            [blender, "--background", "--python", str(script), "--",
             "--params", str(json_path), "--output", str(out_blend), "--formats", "blend,stl"],
            capture_output=True, text=True, timeout=300, cwd=str(_REPO),
        )
        ok = proc.returncode == 0 and out_blend.is_file()
        err = None
        if not ok:
            tail = (proc.stderr or proc.stdout or "")[-300:]
            err = f"rc={proc.returncode}: {tail.strip()}"
        return {"status": "OK" if ok else "FAIL", "elapsed": time.perf_counter() - t0,
                "files": _outputs(out_dir), "error": err}
    except subprocess.TimeoutExpired:
        return {"status": "FAIL", "elapsed": time.perf_counter() - t0,
                "files": _outputs(out_dir), "error": "timeout"}


def run_case(name: str, backend: str, base_out: Path, blender: Optional[str]) -> List[Dict[str, Any]]:
    desc, data, py_ok, bl_ok = CASES[name]
    results: List[Dict[str, Any]] = []
    backends = ["python", "blender"] if backend == "both" else [backend]
    for be in backends:
        out_dir = base_out / be / name
        if be == "python":
            if not py_ok:
                results.append({"case": name, "backend": be, "status": "SKIP",
                                "elapsed": 0.0, "files": [], "error": "não suportado no motor python"})
                continue
            res = run_python(name, data, out_dir)
        else:
            if not bl_ok:
                results.append({"case": name, "backend": be, "status": "SKIP",
                                "elapsed": 0.0, "files": [], "error": "não suportado no blender"})
                continue
            if not blender:
                results.append({"case": name, "backend": be, "status": "SKIP",
                                "elapsed": 0.0, "files": [], "error": "blender não encontrado"})
                continue
            res = run_blender(name, data, out_dir, blender)
        res.update({"case": name, "backend": be})
        results.append(res)
    return results


def _print_table(results: List[Dict[str, Any]]) -> int:
    print("\n" + "=" * 78)
    print(f"  {'caso':24s} {'backend':8s} {'status':6s} {'tempo':>8s}  arquivos / erro")
    print("=" * 78)
    n_fail = 0
    for r in results:
        if r["status"] == "FAIL":
            n_fail += 1
        detail = r.get("error") or f"{len(r.get('files', []))} arquivos"
        print(f"  {r['case']:24s} {r['backend']:8s} {r['status']:6s} {r['elapsed']:7.1f}s  {str(detail)[:60]}")
    print("=" * 78)
    n_ok = sum(1 for r in results if r["status"] == "OK")
    n_skip = sum(1 for r in results if r["status"] == "SKIP")
    print(f"  total: {len(results)}  |  OK: {n_ok}  FAIL: {n_fail}  SKIP: {n_skip}")
    return n_fail


def main() -> None:
    ap = argparse.ArgumentParser(description="runner de geração de modelos (python/blender)")
    ap.add_argument("--list", action="store_true", help="lista os casos disponíveis")
    ap.add_argument("--case", help="nome do caso (ver --list)")
    ap.add_argument("--all", action="store_true", help="executa todos os casos")
    ap.add_argument("--backend", choices=["python", "blender", "both"], default="python")
    ap.add_argument("--out-dir", default=str(_REPO / "generated" / "3d" / "generation_matrix"))
    args = ap.parse_args()

    if args.list:
        print("casos disponíveis:")
        for name, (desc, _d, py, bl) in CASES.items():
            bks = ",".join([b for b, ok in (("python", py), ("blender", bl)) if ok])
            print(f"  {name:24s} {desc}  [{bks}]")
        return

    base_out = Path(args.out_dir)
    blender = _find_blender() if args.backend in ("blender", "both") else None
    if args.backend in ("blender", "both") and not blender:
        print("aviso: blender não encontrado (PATH/BEDFLOW_BLENDER_EXE/Program Files) — casos blender serão SKIP")

    names = list(CASES) if args.all else ([args.case] if args.case else [])
    if not names:
        ap.error("informe --case NAME, --all ou --list")
    for n in names:
        if n not in CASES:
            ap.error(f"caso desconhecido: {n} (use --list)")

    results: List[Dict[str, Any]] = []
    for n in names:
        print(f"\n>>> {n} ({CASES[n][0]}) — backend={args.backend}")
        results.extend(run_case(n, args.backend, base_out, blender))

    n_fail = _print_table(results)
    print(f"\nsaída em: {base_out}")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
