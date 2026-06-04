# Geração de modelos — runner de todos os tipos + melhorias do motor python

Este documento cobre três entregas:

1. **Runner de geração** — um script que executa **todos os tipos de geração de
   modelo** (separados ou todos de uma vez) no **motor python** e no **blender**.
2. **Assentamento do DEM** — melhoria que torna o `rigid_body` do motor python
   geometricamente **válido**.
3. **Export glTF/GLB/OBJ** — formatos extra no motor python.

---

## 1. Runner de geração (`scripts/run_generation_matrix.py`)

Executa uma matriz de casos cobrindo: `full_3d`, modos de interior **m1/m2/m3**,
**corte 2D** (thin slice) e **estatístico 2D**, tipos de partícula
(esfera/cubo/cilindro), métodos de empacotamento (hexagonal/spherical/rigid_body)
e formatos de export. Cada caso é um JSON que serve **aos dois backends**.

### Comandos

```bash
# listar os casos
python scripts/run_generation_matrix.py --list

# UM caso, num backend
python scripts/run_generation_matrix.py --case m3_cheese --backend python
python scripts/run_generation_matrix.py --case slice2d_compare --backend blender

# TODOS os casos, num backend
python scripts/run_generation_matrix.py --all --backend python
python scripts/run_generation_matrix.py --all --backend blender

# TODOS os casos, nos DOIS backends
python scripts/run_generation_matrix.py --all --backend both
```

Saída em `generated/3d/generation_matrix/<backend>/<caso>/` (o `.stl`/`.blend`
gerado + sidecars). No fim, imprime uma tabela com **status (OK/FAIL/SKIP)**,
tempo e nº de arquivos por caso, e sai com código ≠ 0 se algo falhar (útil em CI).

### Casos

| Caso | O que gera | python | blender |
|------|------------|:---:|:---:|
| `full3d_sphere_hex` | full_3d, esferas, hexagonal | ✅ | ✅ |
| `full3d_cube_spherical` | full_3d, cubos, spherical | ✅ | ✅ |
| `full3d_cylinder_hex` | full_3d, cilindros, hexagonal | ✅ | ✅ |
| `full3d_rigidbody` | full_3d, esferas, **rigid_body** (DEM/Bullet) | ✅ | ✅ |
| `m2_solid_embedded` | **m2**: interior sólido + partículas embutidas | ✅ | ✅ |
| `m3_cheese` | **m3**: interior sólido furado (queijo) | ✅ | ✅ |
| `slice2d` | **corte 2D** (pseudo_2d_thin_slice) | ✅ | ✅ |
| `slice2d_compare` | corte 2D + validação 2D/3D (`compare_mode=all`) | ✅ | ✅ |
| `statistical2d` | reconstrução estatística 2D | ✅ | ❌ (só python) |
| `export_multiformat` | full_3d exportando **stl + obj + glb** | ✅ | ✅ |

> O blender é localizado automaticamente (PATH, `BEDFLOW_BLENDER_EXE` ou
> `C:\Program Files\Blender Foundation\Blender*`). Sem blender, os casos blender
> ficam `SKIP`.

### Como “testes separados e todos de uma vez”

- **separado**: `--case <nome>` roda um tipo de geração.
- **todos**: `--all` roda a matriz inteira.
- **por backend**: `--backend python|blender|both`.

---

## 2. Assentamento do DEM (rigid_body do motor python)

O `rigid_body` do motor python é um **DEM** (contato mola-amortecedor). Os
contatos *soft* deixavam **micro-sobreposições** residuais, e a validação estrita
(distância ≥ `r_i+r_j+gap`) **acusava** esses contatos — o empacotamento saía
“inválido”.

Foi adicionada uma etapa de **resolução de contatos** (relaxação por projeção de
posição) ao fim do DEM ([`engine/dem_solver.py`](../../scripts/python_modeling/engine/dem_solver.py),
`_resolve_overlaps`): separa cada par sobreposto até `distância ≥ r_i+r_j+gap` e
reaplica as paredes, usando **os mesmos limites da validação**. Correções-chave:

- célula do spatial-hash = `2·raio + gap` (antes `2·raio` perdia pares
  sobrepostos a >1 célula);
- limites radiais/axiais idênticos a `radial_bounds()`/`z_bounds()` (sem
  dobrar o raio);
- tolerância de convergência abaixo da tolerância da validação (`1e-9`).

**Resultado:** o `rigid_body` agora produz empacotamentos **válidos**.

| | antes | depois |
|---|---|---|
| validação geométrica | falhava (pares/dom. violados) | **passa** (0 violações) |
| sobreposição máx. | ~1e-3 m | **< 1e-9 m** |

Parâmetros (em `packing.dem`): `resolve_contacts` (default `true`),
`contact_max_iters` (1500), `contact_tolerance` (`1e-9`).

> Limitação: a relaxação remove sobreposições, mas o **assentamento por
> gravidade** ainda depende dos passos do DEM (`packing.dem.steps`). Cenários
> muito densos (próximos do close-packing **com** gap) podem reter resíduo —
> fisicamente esperado. Veja [comparação com o Bullet](../motor_python_vs_blender/README.md).

Prova:

```bash
cd scripts/python_modeling
python -m pytest tests/test_dem_settling.py -v        # 3 passed
```

---

## 3. Export glTF / GLB / OBJ (motor python)

O motor python sempre grava **STL**; agora honra `export.formats` do `.bed`/JSON
para gravar também **OBJ**, **glTF** e **GLB**
([`mesh_export_formats.py`](../../scripts/python_modeling/mesh_export_formats.py)).
OBJ é nativo; glTF/GLB usam `trimesh`. `blend`/`fbx` continuam só no backend
blender (geram aviso no motor python).

```jsonc
"export": { "formats": ["stl_binary", "obj", "glb", "gltf"] }
```

Gera, ao lado do `.stl`: `<nome>.obj`, `<nome>.glb`, `<nome>.gltf` (+ buffers).
O sidecar registra `export_formats_files`. **GLB** é o recomendado (binário
autocontido); o `.gltf` do trimesh grava buffers `.bin` separados.

Prova:

```bash
cd scripts/python_modeling
python -m pytest tests/test_export_formats.py -v      # 4 passed
```

---

## Resumo dos testes

```bash
cd scripts/python_modeling
python -m pytest tests/test_dem_settling.py tests/test_export_formats.py -v
# + a matriz completa:
python scripts/run_generation_matrix.py --all --backend both
```

## Arquivos relacionados

| Papel | Arquivo |
|-------|---------|
| Runner de geração | [`scripts/run_generation_matrix.py`](../../scripts/run_generation_matrix.py) |
| Resolução de contatos (DEM) | [`engine/dem_solver.py`](../../scripts/python_modeling/engine/dem_solver.py) |
| Export de formatos | [`mesh_export_formats.py`](../../scripts/python_modeling/mesh_export_formats.py) |
| Testes | [`tests/test_dem_settling.py`](../../scripts/python_modeling/tests/test_dem_settling.py), [`tests/test_export_formats.py`](../../scripts/python_modeling/tests/test_export_formats.py) |
| Comparação python × blender | [`../motor_python_vs_blender/README.md`](../motor_python_vs_blender/README.md) |
