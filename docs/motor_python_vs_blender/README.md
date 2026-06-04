# Motor Python × Blender — comparação e lacunas

Análise dos dois backends de geração de leito (`generation_backend`):

- **`python_engine`** — gera as malhas analiticamente em Python puro
  ([`scripts/python_modeling/`](../../scripts/python_modeling/)), sem abrir o
  Blender; empacotamento por **DEM próprio** ou geradores geométricos.
- **`blender`** — usa o Blender via `bpy`
  ([`scripts/blender_scripts/`](../../scripts/blender_scripts/)); empacotamento
  por **rigid body nativo (Bullet)**.

## 1. Geração de malha — paridade e lacunas

| Recurso | python_engine | blender | Observação |
|---------|:---:|:---:|------------|
| Parede anelar + tampas | ✅ | ✅ | Python: analítico; Blender: boolean |
| Partícula esfera / cubo / cilindro | ✅ | ✅ | |
| Modo interior m1 (oco) | ✅ | ✅ | |
| Modo interior m2 (sólido + partículas) | ✅ | ✅ | Python agora **embedded** (ver [modo_m2](../modo_m2_interior_solido/README.md)) |
| Modo interior m3 (queijo) | ✅ | ✅ | Python precisa de `manifold3d` |
| Corte 2D (thin slice) | ✅ | ✅ | Python: moldura retangular; Blender: boolean intersect |
| Reconstrução estatística 2D | ✅ | ❌ | Blender exige `python_engine` |
| Validação do corte (2D + 3D) | ✅ | parcial | combined/overlay só no Python ([validacao_corte_2d](../validacao_corte_2d/README.md)) |
| Operações booleanas | via `trimesh`+`manifold3d` | nativas (Bullet/EXACT) | Python depende de pacote externo |
| Export STL / OBJ | ✅ | ✅ | |
| Export blend / glТF / glb / fbx | ❌ | ✅ | **lacuna do Python** |
| Materiais / iluminação / render | ❌ | ✅ | Blender é uma suíte 3D completa |
| **Tampa hemisférica** | ❌ | ❌ | **lacuna nos dois**: o wizard oferece `hemispherical`, mas ambos geram tampa **plana** |

### Principais lacunas do `python_engine` (vs Blender)

1. **Formatos de export**: o Python grava STL (+OBJ nas comparações); não grava
   `.blend`, `.gltf`, `.glb`, `.fbx`.
2. **Booleanos dependem de `manifold3d`**: sem ele, m3 (queijo) e o `fuse` do m2
   não funcionam no Python (no Blender é nativo). `pip install manifold3d`.
3. **Sem materiais/render**: o Python entrega só geometria.
4. **Empacotamento físico**: o "rigid body" do Python é um **DEM simplificado**,
   não o Bullet (ver seção 2).

### Lacuna comum aos dois

- **Tampas hemisféricas não implementadas**: `criar_tampa` (Blender) e
  `create_cap_geometry` (Python) sempre fazem um **disco/cilindro plano**. O tipo
  `hemispherical` exposto no wizard é ignorado — convém implementar (domo) ou
  remover a opção.

## 2. Empacotamento rigid body — Python (DEM) × Blender (Bullet)

> Os dois compartilham os geradores **`spherical_packing`** e **`hexagonal_3d`**
> (puramente geométricos, determinísticos por seed). A diferença real está no
> **`rigid_body`**.

### Blender — rigid body nativo (Bullet)

Arquivo: [`leito_extracao.py`](../../scripts/blender_scripts/leito_extracao.py)
(`aplicar_fisica`, `configurar_simulacao_fisica`, `executar_simulacao_fisica`,
`fazer_bake_fisica`).

- Partículas = corpos **ACTIVE** (massa, `friction`, `restitution`,
  `linear/angular_damping`); leito e tampas = **PASSIVE** (alto atrito).
- Mundo de física: `rigidbody_world` com `substeps_per_frame`,
  `solver_iterations`, `use_split_impulse`, gravidade.
- Simula **quadro a quadro** (motor **Bullet**), depois faz **bake** para
  keyframes e **remove** o rigid body (congela as posições finais).
- **Colisão real** por forma (convex hull de cubo/cilindro) e **dinâmica
  rotacional completa** (as partículas giram e assentam).
- Mais **fiel fisicamente**; porosidades realistas; exige o Blender instalado.

### Python — DEM próprio (mola-amortecedor)

Arquivos: [`engine/rigid_body.py`](../../scripts/python_modeling/engine/rigid_body.py)
e [`engine/dem_solver.py`](../../scripts/python_modeling/engine/dem_solver.py).

- `rigid_body` é, na prática, um **preset do DEM**: `run_dem_packing` com mais
  amortecimento e menos passos (`steps ≤ 15000`, `damping ≥ 0.35`).
- Modelo de contato **mola-amortecedor** (`stiffness`, `damping`, `friction`,
  `restitution`); vizinhança por **spatial hash**; integração **Euler explícita**.
- Parede cilíndrica por força + **clamp** rígido; **detecção de repouso** por
  velocidade máxima.
- **Só esferas na colisão**: cubo/cilindro usam **raio circunscrito** (a malha
  exportada mantém a forma real, mas a física não).
- **Sem rotação**: o `Particle` tem campos `orientation`/`angular_velocity`, mas
  o solver **não os integra** (só posição/velocidade).

### Diferenças observadas (exemplo: 60 esferas)

| Aspecto | python_engine (DEM) | blender (Bullet) |
|---------|---------------------|------------------|
| Modelo de contato | mola-amortecedor (soft) | Bullet (impulsos) |
| Rotação das partículas | ❌ (posição só) | ✅ |
| Colisão de cubo/cilindro | raio circunscrito | forma convexa real |
| Assentamento (settle) | pode **não convergir** no nº de passos | converge melhor |
| Validação geométrica estrita | pode **falhar** (contatos soft deixam micro-sobreposição) | mais consistente |
| Custo | **O(passos × pares)**; ~86 s p/ 60 esferas, 15000 passos | depende do Blender |
| Dependência externa | nenhuma (numpy) | Blender instalado |
| Determinismo | por `seed` | spawn por `seed`; integração do Bullet |

> Medição real (60 esferas, bed Ø0.05×0.08): o DEM terminou em `settled=False`
> após 15000 passos, com a validação estrita acusando micro-sobreposições típicas
> de contato soft. É o comportamento esperado do DEM, **não** um travamento — mas
> mostra que o resultado do `rigid_body` Python **não é equivalente** ao do Bullet.

## 3. Recomendações (não implementadas — para discussão)

Para aproximar o `python_engine` do Blender:

1. **DEM**: aceitar micro-sobreposição na validação (tolerância de contato soft),
   ou ajustar `stiffness`/passos para assentar melhor; vetorizar com NumPy para
   ganhar velocidade; opcionalmente adicionar **dinâmica rotacional** para
   cubos/cilindros.
2. **Export**: adicionar `.obj`/`.gltf` gerais (já há escritor OBJ em
   `slice_compare.py`) e, se útil, `.glb`.
3. **Tampas hemisféricas**: implementar o domo nos dois backends (ou remover a
   opção do wizard).
4. **Documentar a dependência** `manifold3d` para m2(fuse)/m3 no `python_engine`.

## Como reproduzir as observações

```bash
# rigid_body no motor python (imprime settled/porosidade/tempo)
cd scripts/python_modeling
python -c "from engine.pipeline import run_packing; \
r=run_packing(dict(diameter=0.05,wall_thickness=0.003,height=0.08,bottom_thickness=0.004,\
top_thickness=0.004,gap=0.0005,particle_diameter=0.008,particle_kind='sphere',\
particle_count=60,packing_method='rigid_body',strict_validation=False,packing={'seed':5})); \
print('settled', r.metadata['generation'].get('settled'), 'porosidade', round(r.porosity,3))"
```

```powershell
# rigid body nativo no blender (Bullet)
& "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe" --background `
  --python scripts\blender_scripts\leito_extracao.py -- `
  --params dsl\wizard_templates\_test_bed_m1_hollow_boolean.json `
  --output "$env:TEMP\m1.blend" --formats blend,stl
```

## Arquivos relacionados

| Papel | Arquivo |
|-------|---------|
| DEM / rigid_body (Python) | [`engine/dem_solver.py`](../../scripts/python_modeling/engine/dem_solver.py), [`engine/rigid_body.py`](../../scripts/python_modeling/engine/rigid_body.py) |
| Física Bullet (Blender) | [`leito_extracao.py`](../../scripts/blender_scripts/leito_extracao.py) |
| Geração de malha (Python) | [`pure_bed_mesh.py`](../../scripts/python_modeling/pure_bed_mesh.py), [`bed_shell_build.py`](../../scripts/python_modeling/bed_shell_build.py) |
| Geração de malha (Blender) | [`packed_bed_science/blender_build.py`](../../scripts/blender_scripts/packed_bed_science/blender_build.py) |
