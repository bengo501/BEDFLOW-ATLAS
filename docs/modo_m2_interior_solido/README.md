# Modo m2 — interior sólido com partículas fixas dentro

Verificação, correção e validação do modo **m2**
(`internal_cylinder_mode = "internal_cylinder_visible_no_boolean"`): o leito tem
um **interior sólido** (cilindro maciço no lugar do furo) e as **partículas ficam
fixas/embutidas dentro desse sólido**.

## O que foi verificado (e o problema encontrado)

Ao auditar o m2 no **motor Python**, encontramos um defeito: ele usava uma
**união booleana** (`fuse`) entre o núcleo sólido e as partículas. Como, num
empacotamento real, as partículas ficam **totalmente dentro** do núcleo, a união
as **absorvia** — o resultado era um cilindro maciço liso e **as partículas
sumiam**.

Verificação que comprovou o defeito (núcleo de 96 faces):

| Caso | Faces | Volume | Resultado |
|------|-------|--------|-----------|
| núcleo sólido sozinho | 96 | 6.460e-05 | — |
| **antigo m2 (fuse), partículas dentro** | **96** | **6.460e-05** | **idêntico ao núcleo → partículas absorvidas** |

O **backend Blender**, por outro lado, sempre manteve as partículas como
**objetos separados** dentro do sólido (`esferas: N malhas`), então lá o m2 já
funcionava como esperado.

## A correção

O m2 do Python passou a manter as partículas como **geometria distinta embutida**
(paridade com o Blender), em vez de absorvê-las:

| Comportamento | `inner_core` | `particle_tools` | Partículas |
|---------------|--------------|------------------|------------|
| **embedded** *(novo padrão)* | `solid_with_embedded_particles` | `embedded` | **presentes** (geometria distinta dentro do sólido) |
| **fused** *(opt-in)* | `fused_with_particles` | `applied` | absorvidas (sólido único, estanque) |

- **embedded (padrão)**: o STL contém o núcleo sólido **+** as esferas das
  partículas (sobrepostas). As partículas ficam fixas dentro do sólido e
  aparecem ao **cortar/clip** ou ao colorir os objetos.
- **fused (opcional)**: para quem quer um **sólido único estanque** (ex.: domínio
  maciço para CFD), ative no `.bed`/JSON:
  ```jsonc
  "bed": { "solid_particles_fuse": true }
  ```

Verificação da correção (com 4 partículas totalmente internas):

```
embedded: 672 faces, inner_core=solid_with_embedded_particles, 4 partículas presentes
fused   : 480 faces, partículas internas absorvidas
```

## Geometria (sem sobreposição)

Igual aos demais modos com interior, e validado:

- **Parede anelar** (`r_int..r_ext`) + **núcleo sólido** de raio **exatamente
  `r_int`** → encostam sem volume em comum.
- O núcleo ocupa **apenas o vão entre as tampas** (`z ∈ [tampa_inf, H−tampa_sup]`)
  → não invade as tampas.
- As partículas ficam dentro do núcleo (raio do centro `< r_int − r_part`).

## Como gerar e validar

### Demonstração (motor Python)

```bash
python scripts/python_modeling/m2_demo.py
```

Saída em `generated/3d/m2_demo/`:

- `m2_leito.stl` — a malha m2 real (parede + tampas + núcleo + partículas); **corte/clip** para ver as partículas dentro.
- `m2_validacao.obj` / `.mtl` — **dois objetos coloridos**: núcleo **translúcido** + partículas **sólidas** → dá para **ver as partículas dentro do sólido sem cortar**.

Abra o `m2_validacao.obj` no Blender/ParaView: o sólido translúcido com as
esferas sólidas dentro mostra, na hora, que as partículas estão fixas no interior.

### Blender (pipeline real)

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe" --background `
  --python scripts\blender_scripts\leito_extracao.py -- `
  --params dsl\wizard_templates\_test_bed_m2_visible_inner.json `
  --output "$env:TEMP\m2.blend" --formats blend
```

Procure por `esferas: 15 malhas mesh compartilhada` e
`inner_core: visible_separate` — confirma o núcleo sólido + as 15 partículas como
objetos distintos dentro dele.

### Teste automatizado (a prova)

```bash
cd scripts/python_modeling
python -m pytest tests/test_solid_embedded_particles.py -v
```

Esperado: **4 passed** — verifica o status `embedded`, que cada partícula deixa
geometria no resultado, que `embedded` tem mais faces que `fused`, e que o núcleo
não invade as tampas.

## No wizard

No questionário interativo, etapa "leito":

```
modo do interior do leito:
  [2] interior solido + particulas grudadas no cilindro solido   <- m2
```

## Arquivos relacionados

| Papel | Arquivo |
|-------|---------|
| Construção m2 (núcleo + partículas) | [`bed_shell_build.py`](../../scripts/python_modeling/bed_shell_build.py) |
| Construção m2 (Blender) | [`blender_build.py`](../../scripts/blender_scripts/packed_bed_science/blender_build.py) |
| Demonstração + OBJ de validação | [`m2_demo.py`](../../scripts/python_modeling/m2_demo.py) |
| Teste/prova | [`tests/test_solid_embedded_particles.py`](../../scripts/python_modeling/tests/test_solid_embedded_particles.py) |
| Comparação Python × Blender | [`../motor_python_vs_blender/README.md`](../motor_python_vs_blender/README.md) |
