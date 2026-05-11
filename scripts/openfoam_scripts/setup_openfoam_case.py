#!/usr/bin/env python3
"""
script para configurar e executar simulacao cfd com openfoam
a partir do modelo 3d gerado pelo blender

workflow:
1. ler parametros do leito (bed.json)
2. exportar geometria do blender para stl
3. criar caso openfoam
4. gerar malha com snappyhexmesh
5. configurar condicoes de contorno
6. executar simulacao
7. pos-processar resultados
"""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Tuple
import sys


def _write_text_unix(path: Path, text: str) -> None:
    """lf only: openfoam e bash no wsl falham com crlf (bad interpreter ^m)."""
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def _foam_dictionary_header() -> str:
    """banner completo antes de FoamFile (openfoam 1906+ rejeita cabecalho truncado)."""
    return (
        "/*--------------------------------*- C++ -*----------------------------------*\\\n"
        "| =========                 |                                                 |\n"
        "| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |\n"
        "|  \\\\    /   O peration     | Version:  v1906+                                |\n"
        "|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |\n"
        "|    \\\\/     M anipulation  |                                                 |\n"
        "\\*---------------------------------------------------------------------------*/\n"
    )


def _repo_root_for_hints() -> Path:
    try:
        from bedflow_local_paths import project_root

        return project_root()
    except ImportError:
        return Path(__file__).resolve().parents[2]


def _windows_path_to_wsl(path: Path) -> str:
    s = str(path.resolve())
    if len(s) >= 2 and s[1] == ":":
        return f"/mnt/{s[0].lower()}{s[2:].replace(chr(92), '/')}"
    return s.replace("\\", "/")


OPENFOAM_HINT_FILE_NAME = "openfoam_wsl_bashrc.txt"


def _ensure_openfoam_hint_file(repo_root: Path) -> Path:
    """ficheiro opcional: uma linha com caminho absoluto wsl para etc/bashrc."""
    p = repo_root / "local_data" / OPENFOAM_HINT_FILE_NAME
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        _write_text_unix(
            p,
            "# caminho absoluto no wsl para etc/bashrc do openfoam (apenas uma linha ativa)\n"
            "# exemplos:\n"
            "# /opt/openfoam11/etc/bashrc\n"
            "# ubuntu apt (openfoam 1906 metapackage): /usr/share/openfoam/etc/bashrc\n"
            "# /usr/lib/openfoam/openfoam2312/etc/bashrc\n"
            "# ou exporte BEDFLOW_OPENFOAM_BASHRC nesse caminho antes de ./Allrun\n",
        )
    return p


class OpenFOAMCaseGenerator:
    """classe para gerar e executar caso openfoam"""
    
    def __init__(self, bed_json_path: Path, output_dir: Path):
        """
        inicializar gerador de caso openfoam
        
        args:
            bed_json_path: caminho para arquivo.bed.json
            output_dir: diretorio para caso openfoam
        """
        self.bed_json_path = Path(bed_json_path)
        self.output_dir = Path(output_dir)
        self.params = self._load_params()
        self.case_name = self.bed_json_path.stem.replace('.bed', '')
        self.case_dir = self.output_dir / self.case_name
        
    def _load_params(self) -> Dict[str, Any]:
        """carregar parametros do arquivo json"""
        print(f"\n[1/8] carregando parametros de {self.bed_json_path}")
        
        if not self.bed_json_path.exists():
            raise FileNotFoundError(f"arquivo nao encontrado: {self.bed_json_path}")
        
        with open(self.bed_json_path, 'r', encoding='utf-8') as f:
            params = json.load(f)
        
        print(f"  [OK] parametros carregados")
        print(f"    - leito: {params['bed']['diameter']}m x {params['bed']['height']}m")
        print(f"    - particulas: {params['particles']['count']}")
        
        return params
    
    def export_stl_from_blender(self, blend_file: Path) -> Path:
        """
        exportar geometria do blender para stl
        
        args:
            blend_file: arquivo .blend gerado
            
        returns:
            caminho do arquivo stl gerado
        """
        print(f"\n[2/8] exportando stl do blender")
        
        if not blend_file.exists():
            raise FileNotFoundError(f"arquivo blend nao encontrado: {blend_file}")
        
        stl_target = (self.output_dir / f"{self.case_name}.stl").resolve()
        # literal python seguro: caminhos windows com \U \t etc. nao podem ir cru numa string "..."
        _stl_literal = json.dumps(str(stl_target), ensure_ascii=False)

        # criar script python para executar no blender
        export_script = f"""
import bpy
import os

# limpar selecao
bpy.ops.object.select_all(action='DESELECT')

# selecionar todos objetos
bpy.ops.object.select_all(action='SELECT')

# exportar para stl
output_path = {_stl_literal}
_out_dir = os.path.dirname(output_path)
if _out_dir:
    os.makedirs(_out_dir, exist_ok=True)

bpy.ops.export_mesh.stl(
    filepath=output_path,
    use_selection=True,
    ascii=False,  # binario e menor
    use_mesh_modifiers=True
)

print(f"STL exportado: {{output_path}}")
"""
        
        # salvar script temporario
        script_path = self.output_dir / "export_stl.py"
        _write_text_unix(script_path, export_script)
        
        # encontrar blender
        blender_paths = [
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
            "blender"
        ]
        
        blender_exe = None
        for path in blender_paths:
            if Path(path).exists() if path.startswith("C:") else True:
                blender_exe = path
                break
        
        if not blender_exe:
            raise FileNotFoundError("blender nao encontrado no sistema")
        
        # executar blender para exportar
        print(f"  executando blender...")
        result = subprocess.run([
            blender_exe,
            "--background",
            str(blend_file),
            "--python", str(script_path)
        ], capture_output=True, text=True)
        
        # limpar script temporario
        script_path.unlink()
        
        stl_path = stl_target
        
        if result.returncode == 0 and stl_path.exists():
            size_mb = stl_path.stat().st_size / (1024 * 1024)
            print(f"  [OK] stl exportado: {stl_path}")
            print(f"    tamanho: {size_mb:.2f} mb")
            return stl_path
        else:
            print(f"  [ERRO] erro ao exportar stl:")
            print(result.stderr)
            raise RuntimeError("falha ao exportar stl")
    
    def create_case_structure(self):
        """criar estrutura de diretorios do caso openfoam"""
        print(f"\n[3/8] criando estrutura do caso openfoam")
        
        # criar diretorios
        dirs = [
            self.case_dir / "0",
            self.case_dir / "constant" / "triSurface",
            self.case_dir / "constant" / "polyMesh",
            self.case_dir / "system"
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        print(f"  [OK] caso criado em: {self.case_dir}")
    
    def copy_stl_to_case(self, stl_path: Path):
        """copiar arquivo stl para o caso"""
        print(f"\n[4/8] copiando stl para caso")
        
        dest = self.case_dir / "constant" / "triSurface" / "leito.stl"
        shutil.copy(stl_path, dest)
        
        print(f"  [OK] stl copiado para: {dest}")
    
    def create_mesh_dict(self):
        """criar dicionarios de geracao de malha"""
        print(f"\n[5/8] criando configuracao de malha")

        # obter dimensoes do leito
        diameter = float(self.params["bed"]["diameter"])
        height = float(self.params["bed"]["height"])

        # cantos da caixa (bloco hex) — valores numericos: openfoam nao expande $xMin nem aceita xMin;
        # como chave de primeiro nivel no blockmeshdict
        xm = -diameter * 0.6
        xM = diameter * 0.6
        ym = -diameter * 0.6
        yM = diameter * 0.6
        zm = -height * 0.1
        zM = height * 1.1
        _v = lambda a: f"{a:.10g}"

        # criar blockmeshdict (malha de fundo)
        blockmesh = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v1906+                                |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1;

vertices
(
    ({_v(xm)} {_v(ym)} {_v(zm)})
    ({_v(xM)} {_v(ym)} {_v(zm)})
    ({_v(xM)} {_v(yM)} {_v(zm)})
    ({_v(xm)} {_v(yM)} {_v(zm)})
    ({_v(xm)} {_v(ym)} {_v(zM)})
    ({_v(xM)} {_v(ym)} {_v(zM)})
    ({_v(xM)} {_v(yM)} {_v(zM)})
    ({_v(xm)} {_v(yM)} {_v(zM)})
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (40 40 60) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    walls
    {{
        type wall;
        faces
        (
            (0 3 2 1)
            (4 5 6 7)
            (0 4 7 3)
            (2 6 5 1)
            (1 5 4 0)
            (3 7 6 2)
        );
    }}
);

mergePatchPairs
(
);

// ************************************************************************* //
"""
        
        # salvar blockmeshdict
        _write_text_unix(self.case_dir / "system" / "blockMeshDict", blockmesh)
        
        print(f"  [OK] blockMeshDict criado")
        
        # criar snappyhexmeshdict
        snappy = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  11                                    |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      snappyHexMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

castellatedMesh true;
snap            true;
addLayers       false;

geometry
{{
    leito.stl
    {{
        type triSurfaceMesh;
        name leito;
    }}
}}

castellatedMeshControls
{{
    maxLocalCells 1000000;
    maxGlobalCells 2000000;
    minRefinementCells 10;
    maxLoadUnbalance 0.10;
    nCellsBetweenLevels 3;
    
    features
    (
    );
    
    refinementSurfaces
    {{
        leito
        {{
            level (2 3);
            patchInfo
            {{
                type wall;
            }}
        }}
    }}
    
    resolveFeatureAngle 30;
    
    refinementRegions
    {{
    }}
    
    locationInMesh ({diameter * 0.5} {diameter * 0.5} {height * 0.5});
    allowFreeStandingZoneFaces true;
}}

snapControls
{{
    nSmoothPatch 3;
    tolerance 2.0;
    nSolveIter 30;
    nRelaxIter 5;
}}

addLayersControls
{{
    relativeSizes true;
    layers
    {{
    }}
    expansionRatio 1.0;
    finalLayerThickness 0.3;
    minThickness 0.1;
    nGrow 0;
    featureAngle 60;
    slipFeatureAngle 30;
    nRelaxIter 3;
    nSmoothSurfaceNormals 1;
    nSmoothNormals 3;
    nSmoothThickness 10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedianAxisAngle 90;
    nBufferCellsNoExtrude 0;
    nLayerIter 50;
}}

meshQualityControls
{{
    maxNonOrtho 65;
    maxBoundarySkewness 20;
    maxInternalSkewness 4;
    maxConcave 80;
    minVol 1e-13;
    minTetQuality 1e-30;
    minArea -1;
    minTwist 0.02;
    minDeterminant 0.001;
    minFaceWeight 0.02;
    minVolRatio 0.01;
    minTriangleTwist -1;
    nSmoothScale 4;
    errorReduction 0.75;
}}

mergeTolerance 1e-6;

// ************************************************************************* //
"""
        
        _write_text_unix(self.case_dir / "system" / "snappyHexMeshDict", snappy)
        
        print(f"  [OK] snappyHexMeshDict criado")
    
    def create_control_dicts(self):
        """criar dicionarios de controle da simulacao"""
        print(f"\n[6/8] criando configuracao de simulacao")
        
        # obter parametros cfd
        cfd = self.params.get('cfd', {})
        
        # valores padrao se nao especificados
        inlet_velocity = float(cfd.get('inlet_velocity', 0.1))
        max_iterations = int(cfd.get('max_iterations', 1000))
        
        # controlDict
        control = _foam_dictionary_header() + f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     simpleFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         {max_iterations};

deltaT          1;

writeControl    timeStep;

writeInterval   100;

purgeWrite      2;

writeFormat     binary;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;

// ************************************************************************* //
"""
        
        _write_text_unix(self.case_dir / "system" / "controlDict", control)
        
        # fvSchemes
        schemes = _foam_dictionary_header() + """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

ddtSchemes
{
    default         steadyState;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linearUpwind grad(U);
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

// ************************************************************************* //
"""
        
        _write_text_unix(self.case_dir / "system" / "fvSchemes", schemes)
        
        # fvSolution
        solution = _foam_dictionary_header() + """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.1;
        smoother        GaussSeidel;
    }

    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
    consistent      yes;

    residualControl
    {
        p               1e-4;
        U               1e-4;
    }
}

relaxationFactors
{
    fields
    {
        p               0.3;
    }
    equations
    {
        U               0.7;
    }
}

// ************************************************************************* //
"""
        
        _write_text_unix(self.case_dir / "system" / "fvSolution", solution)
        
        print(f"  [OK] arquivos de controle criados")
    
    def create_initial_conditions(self):
        """criar condicoes iniciais e de contorno"""
        print(f"\n[7/8] criando condicoes iniciais")
        
        # obter parametros
        cfd = self.params.get('cfd', {})
        inlet_velocity = float(cfd.get('inlet_velocity', 0.1))
        
        # arquivo U (velocidade)
        u_file = _foam_dictionary_header() + f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 {inlet_velocity});

boundaryField
{{
    leito
    {{
        type            noSlip;
    }}
    
    walls
    {{
        type            noSlip;
    }}
}}

// ************************************************************************* //
"""
        
        _write_text_unix(self.case_dir / "0" / "U", u_file)
        
        # arquivo p (pressao)
        p_file = _foam_dictionary_header() + """FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    leito
    {
        type            zeroGradient;
    }
    
    walls
    {
        type            zeroGradient;
    }
}

// ************************************************************************* //
"""
        
        _write_text_unix(self.case_dir / "0" / "p", p_file)
        
        # transportProperties
        fluid_viscosity = float(cfd.get('fluid_viscosity', 1.5e-5))
        
        transport = _foam_dictionary_header() + f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

transportModel  Newtonian;

nu              {fluid_viscosity};

// ************************************************************************* //
"""
        
        _write_text_unix(self.case_dir / "constant" / "transportProperties", transport)
        
        # turbulenceProperties
        turbulence = _foam_dictionary_header() + """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      turbulenceProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

simulationType laminar;

// ************************************************************************* //
"""
        
        _write_text_unix(self.case_dir / "constant" / "turbulenceProperties", turbulence)
        
        print(f"  [OK] condicoes iniciais criadas")
    
    def create_run_script(self):
        """criar script allrun para executar caso"""
        print(f"\n[8/8] criando script de execucao")

        repo = _repo_root_for_hints()
        hint_disk = _ensure_openfoam_hint_file(repo)
        hint_wsl_json = json.dumps(_windows_path_to_wsl(hint_disk))

        allrun = (
            """#!/usr/bin/env bash
# hint: export BEDFLOW_OPENFOAM_BASHRC=/opt/openfoam11/etc/bashrc  ou edite:
# """
            + str(hint_disk).replace("\\", "/")
            + """
FOAM_USER_HINT_FILE="""
            + hint_wsl_json
            + """

cd "${0%/*}" || exit 1

foam_source_env() {
  local b="" try="" n="" globs

  if [ -n "${BEDFLOW_OPENFOAM_BASHRC:-}" ] && [ -f "$BEDFLOW_OPENFOAM_BASHRC" ]; then
    # shellcheck source=/dev/null
    source "$BEDFLOW_OPENFOAM_BASHRC"
    return 0
  fi
  if [ -n "${WM_PROJECT_DIR:-}" ] && [ -f "${WM_PROJECT_DIR}/etc/bashrc" ]; then
    # shellcheck source=/dev/null
    source "${WM_PROJECT_DIR}/etc/bashrc"
    return 0
  fi
  if [ -f "$FOAM_USER_HINT_FILE" ]; then
    b=$(grep -v '^[[:space:]]*#' "$FOAM_USER_HINT_FILE" | grep -v '^[[:space:]]*$' | head -1 | sed 's/\\r//g')
    b=$(echo "$b" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    if [ -n "$b" ] && [ -f "$b" ]; then
      # shellcheck source=/dev/null
      source "$b"
      return 0
    fi
  fi

  # ubuntu/debian: metapacote "openfoam" (ex. v1906) — dpkg -L aponta para /usr/share/openfoam/etc/bashrc
  if [ -f /usr/share/openfoam/etc/bashrc ]; then
    # shellcheck source=/dev/null
    source /usr/share/openfoam/etc/bashrc
    return 0
  fi

  for try in \\
      /opt/openfoam12/etc/bashrc \\
      /opt/openfoam11/etc/bashrc \\
      /opt/openfoam10/etc/bashrc \\
      /opt/openfoam9/etc/bashrc \\
      /opt/openfoam8/etc/bashrc \\
      /usr/lib/openfoam/openfoam2312/etc/bashrc \\
      /usr/lib/openfoam/openfoam2306/etc/bashrc \\
      /usr/lib/openfoam/openfoam2212/etc/bashrc \\
      /usr/lib/openfoam/openfoam2112/etc/bashrc \\
      /usr/lib/openfoam/openfoam2012/etc/bashrc \\
      /usr/lib/openfoam/openfoam1912/etc/bashrc \\
      /usr/lib/openfoam/openfoam1906/etc/bashrc \\
      /usr/lib/openfoam/openfoam1812/etc/bashrc \\
      /usr/lib/openfoam/openfoam1806/etc/bashrc
  do
    if [ -f "$try" ]; then
      # shellcheck source=/dev/null
      source "$try"
      return 0
    fi
  done

  shopt -s nullglob
  globs=(/opt/openfoam*/etc/bashrc)
  n=${#globs[@]}
  shopt -u nullglob
  if [ "$n" -gt 0 ] && command -v sort >/dev/null 2>&1; then
    try=$(printf '%s\\n' "${globs[@]}" | sort -V 2>/dev/null | tail -1)
    if [ -n "$try" ] && [ -f "$try" ]; then
      # shellcheck source=/dev/null
      source "$try"
      return 0
    fi
  fi

  shopt -s nullglob
  globs=(/usr/lib/openfoam/openfoam*/etc/bashrc)
  n=${#globs[@]}
  shopt -u nullglob
  if [ "$n" -gt 0 ] && command -v sort >/dev/null 2>&1; then
    try=$(printf '%s\\n' "${globs[@]}" | sort -V 2>/dev/null | tail -1)
    if [ -n "$try" ] && [ -f "$try" ]; then
      # shellcheck source=/dev/null
      source "$try"
      return 0
    fi
  fi

  for try in \\
      "$HOME/OpenFOAM/OpenFOAM-v2412/etc/bashrc" \\
      "$HOME/OpenFOAM/OpenFOAM-v2312/etc/bashrc" \\
      "$HOME/OpenFOAM/OpenFOAM-v2306/etc/bashrc" \\
      "$HOME/OpenFOAM/OpenFOAM-v2212/etc/bashrc" \\
      "$HOME/OpenFOAM/OpenFOAM-v2112/etc/bashrc"
  do
    if [ -f "$try" ]; then
      # shellcheck source=/dev/null
      source "$try"
      return 0
    fi
  done

  if command -v blockMesh >/dev/null 2>&1; then
    return 0
  fi

  echo "[ERRO] openfoam nao encontrado no wsl."
  echo "  opcoes:"
  echo "  1) sudo apt update && sudo apt install -y openfoam  (ou pacote openfoam.com / esp.org)"
  echo "  2) no ficheiro (uma linha): $FOAM_USER_HINT_FILE"
  echo "     ex: /usr/share/openfoam/etc/bashrc (ubuntu apt) ou /opt/openfoam11/etc/bashrc"
  echo "  3) no ~/.bashrc: export BEDFLOW_OPENFOAM_BASHRC=/caminho/para/etc/bashrc"
  return 1
}

foam_source_env || exit 1

echo "========================================="
echo " executando caso openfoam"
echo "========================================="

echo ""
echo "1. gerando malha de fundo (blockMesh)..."
blockMesh > log.blockMesh 2>&1
if [ $? -ne 0 ]; then
    echo "erro no blockMesh! veja log.blockMesh"
    exit 1
fi
echo "   [OK] malha de fundo criada"

echo ""
echo "2. gerando malha refinada (snappyHexMesh)..."
echo "   (isso pode demorar alguns minutos...)"
snappyHexMesh -overwrite > log.snappyHexMesh 2>&1
if [ $? -ne 0 ]; then
    echo "erro no snappyHexMesh! veja log.snappyHexMesh"
    exit 1
fi
echo "   [OK] malha refinada criada"

echo ""
echo "3. verificando qualidade da malha..."
checkMesh > log.checkMesh 2>&1
echo "   (veja log.checkMesh para detalhes)"

echo ""
echo "4. executando simulacao (simpleFoam)..."
echo "   (monitorando convergencia...)"
simpleFoam > log.simpleFoam 2>&1 &
FOAM_PID=$!

# monitorar convergencia
while kill -0 $FOAM_PID 2>/dev/null; do
    if [ -f log.simpleFoam ]; then
        LAST_TIME=$(grep "^Time = " log.simpleFoam | tail -1)
        printf "\\r   %s" "$LAST_TIME"
    fi
    sleep 2
done
wait $FOAM_PID
FOAM_EXIT=$?

echo ""
if [ $FOAM_EXIT -eq 0 ]; then
    echo "   [OK] simulacao concluida!"
else
    echo "   [ERRO] erro na simulacao! veja log.simpleFoam"
    exit 1
fi

echo ""
echo "========================================="
echo " caso executado com sucesso!"
echo "========================================="
echo ""
echo "proximos passos:"
echo "  - visualizar: touch caso.foam && paraview caso.foam"
echo "  - pos-processar: postProcess -func sample"
echo ""

# criar arquivo .foam para paraview
touch caso.foam

exit 0
"""
        )

        allrun_path = self.case_dir / "Allrun"
        _write_text_unix(allrun_path, allrun)
        
        # tornar executavel (no wsl)
        try:
            allrun_path.chmod(0o755)
        except:
            pass  # windows nao suporta chmod
        
        print(f"  [OK] script Allrun criado")
        print(
            f"  [i] se o wsl nao encontrar openfoam, instale-o ou "
            f"coloque o caminho do etc/bashrc em: {hint_disk}"
        )
    
    def run(self, blend_file: Path, execute_simulation: bool = True):
        """
        executar todo o processo

        args:
            blend_file: arquivo .blend gerado pelo blender, ou .stl ja exportado (perfil python)
            execute_simulation: se true, executa a simulacao apos criar o caso
        """
        print(f"\n{'='*60}")
        print(f"  configuracao de caso openfoam")
        print(f"{'='*60}")

        try:
            blend_file = Path(blend_file)
            if blend_file.suffix.lower() == ".stl":
                stl_path = blend_file.resolve()
                if not stl_path.exists():
                    raise FileNotFoundError(f"stl nao encontrado: {stl_path}")
                print(f"\n[2/8] usando stl existente (sem blender): {stl_path}")
            else:
                stl_path = self.export_stl_from_blender(blend_file)
            
            # criar estrutura do caso
            self.create_case_structure()
            
            # copiar stl
            self.copy_stl_to_case(stl_path)
            
            # criar dicionarios de malha
            self.create_mesh_dict()
            
            # criar dicionarios de controle
            self.create_control_dicts()
            
            # criar condicoes iniciais
            self.create_initial_conditions()
            
            # criar script de execucao
            self.create_run_script()
            
            print(f"\n{'='*60}")
            print(f"  [OK] caso openfoam configurado com sucesso!")
            print(f"{'='*60}")
            print(f"\ncaso criado em: {self.case_dir}")
            print(f"\npara executar a simulacao:")
            print(f"  cd {self.case_dir}")
            print(f"  ./Allrun")
            print(f"\nou execute este script com --run")
            
            if execute_simulation:
                self.execute_simulation()
            
            return True
            
        except Exception as e:
            print(f"\n[ERRO] erro: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def execute_simulation(self):
        """executar simulacao openfoam"""
        print(f"\n{'='*60}")
        print(f"  executando simulacao openfoam")
        print(f"{'='*60}")
        print(f"\ndiretorio: {self.case_dir}")
        print(f"isso pode demorar varios minutos...")
        print(f"pressione ctrl+c para cancelar")
        print()
        
        try:
            # executar allrun
            result = subprocess.run(
                ["./Allrun"],
                cwd=self.case_dir,
                shell=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"\n[OK] simulacao concluida com sucesso!")
                print(f"\narquivos de resultado em: {self.case_dir}")
                print(f"\nvisualizar:")
                print(f"  cd {self.case_dir}")
                print(f"  paraview caso.foam")
            else:
                print(f"\n[ERRO] simulacao falhou com codigo {result.returncode}")
                print(f"verifique os arquivos de log em {self.case_dir}")
                
        except KeyboardInterrupt:
            print(f"\n\nsimulacao cancelada pelo usuario")
        except Exception as e:
            print(f"\n[ERRO] erro ao executar simulacao: {e}")


def main():
    """funcao principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='configurar e executar caso openfoam a partir de modelo blender'
    )
    parser.add_argument(
        'bed_json',
        type=str,
        help='caminho para arquivo .bed.json'
    )
    parser.add_argument(
        'blend_file',
        type=str,
        help='caminho para .blend (exporta stl) ou .stl ja gerado (perfil python)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='generated/cfd',
        help='diretorio de saida para caso openfoam'
    )
    parser.add_argument(
        '--run',
        action='store_true',
        help='executar simulacao apos criar caso'
    )
    
    args = parser.parse_args()
    
    # criar gerador
    generator = OpenFOAMCaseGenerator(
        bed_json_path=Path(args.bed_json),
        output_dir=Path(args.output_dir)
    )
    
    # executar
    success = generator.run(
        blend_file=Path(args.blend_file),
        execute_simulation=args.run
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

