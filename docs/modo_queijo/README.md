# Modo "queijo" (m3) — funcionamento

> Para **provar** que está funcionando (comandos e testes), veja **[PROVA.md](PROVA.md)**.

Este documento explica **como funciona** o modo `m3`
(`solid_internal_cylinder_with_particle_holes`) de geração de malha do leito.

## Os três modos de interior do leito

O leito é um cilindro com paredes (anel de `r_int` a `r_ext`) e tampas. O que
ocupa o **interior** (o furo de raio `r_int`) é definido por
`bed.internal_cylinder_mode`:

| # | `internal_cylinder_mode` | Interior | Partículas |
|---|--------------------------|----------|------------|
| m1 | `hollow_boolean_applied` (default) | **vazio** (leito oco) | soltas dentro do anel |
| m2 | `internal_cylinder_visible_no_boolean` | **cilindro maciço** | embutidas/grudadas no maciço |
| m3 | `solid_internal_cylinder_with_particle_holes` | **cilindro maciço furado** | **viram buracos** (somem) |

No **m3**, o interior é um cilindro **maciço** do qual a malha de cada partícula é
**subtraída** (boolean *difference*), deixando **cavidades internas** — como um
**queijo suíço**. As partículas, em si, não são exportadas: viram os furos.

> Importante: o **empacotamento não muda**. As partículas continuam sendo
> posicionadas normalmente no anel (mesmo packing dos outros modos). No m3 elas
> apenas deixam de ser exportadas como esferas e passam a ser usadas como
> **ferramentas de corte** do núcleo.

## Geometria (e por que não há sobreposição)

```
   z=H ┌───────────┐  tampa superior (raio r_ext)
       │██       ██│  ┐
       │██  N   ██│   │ parede (anel r_int..r_ext)
       │██ ÚCL ██│    │
       │██  EO  ██│   │  núcleo maciço (raio r_int),
       │██ (•)  ██│   │  SÓ no vão entre as tampas:
       │██  •   ██│   │  z ∈ [tampa_inf, H - tampa_sup]
   z=0 └───────────┘  ┘  tampa inferior
        (•) = cavidades deixadas pelas partículas
```

Para evitar malhas sobrepostas:

- **Parede × núcleo**: a parede é um **anel** (`r_int..r_ext`) e o núcleo tem raio
  **exatamente `r_int`** → eles apenas se encostam, sem volume em comum.
- **Tampas × núcleo**: o núcleo ocupa **apenas o vão interno** entre as faces
  internas das tampas (não a altura cheia), então não invade as tampas.

## Como o corte é feito (os dois backends)

O número de furos efetivamente aplicados aparece no metadado
`boolean_operation_status` (campos `particle_tools`, `inner_core`,
`n_holes_applied`) gravado no `*_pure_bed.json`.

### Motor Python (`generation_backend = python_engine`)

Arquivo: [`scripts/python_modeling/bed_shell_build.py`](../../scripts/python_modeling/bed_shell_build.py)

1. `build_bed_shell(...)` cria a **parede anelar** + tampas.
2. `_solid_cylinder_mesh(r_int, ..., z_bottom, z_top)` cria o **núcleo maciço**
   no vão entre as tampas (`_interior_span`).
3. `punch_holes_in_solid(core, centers, ...)`:
   - repara o núcleo para um **volume estanque** (`_as_trimesh_volume`);
   - escolhe o **backend booleano** (`_pick_boolean_engine`: `manifold3d`);
   - para cada partícula cria uma ferramenta (`trimesh.creation` →
     esfera/cubo/cilindro) e faz `mesh.difference(tool)`;
   - devolve a malha perfurada, o `status` (`applied`/`partial`/`failed`) e o
     **número de furos aplicados**.

> Dependência: o motor Python precisa de `trimesh` + `manifold3d`. **Sem o
> backend**, o núcleo sai **maciço (sem furos)** e o status fica `failed` com
> aviso — por isso o teste de prova é *pulado* nesse caso (ver PROVA.md).

### Blender (`generation_backend = blender`)

Arquivos: [`packed_bed_science/blender_build.py`](../../scripts/blender_scripts/packed_bed_science/blender_build.py)
e [`leito_extracao.py`](../../scripts/blender_scripts/leito_extracao.py)

1. `create_bed_by_internal_mode(...)` cria a **parede anelar**
   (`create_hollow_cylinder`) + o **núcleo** (`create_solid_inner_core`, no vão
   entre as tampas via `_interior_core_span`).
2. `create_caps(...)` cria as tampas.
3. `punch_core_with_particle_tools(core, centers, ...)`: para cada partícula,
   cria uma primitiva e aplica um modificador **Boolean DIFFERENCE** (solver
   `EXACT`); as ferramentas são removidas após o corte.

O Blender usa o **boolean nativo** — **não** precisa de `manifold3d`.

## Configuração (`.bed` / JSON)

```jsonc
"bed": {
  "diameter": 0.05,
  "height": 0.1,
  "wall_thickness": 0.002,
  "internal_cylinder_mode": "solid_internal_cylinder_with_particle_holes",
  "visibility": {
    "show_outer_cylinder": true,
    "show_internal_cylinder": true,   // exporta o núcleo perfurado
    "show_particles": false           // no m3 as partículas viram furos
  }
}
```

No **wizard** (`python bed_wizard.py`, fluxo interativo, etapa "leito"):

```
modo do interior do leito:
  [1] normal - leito oco, particulas soltas no interior
  [2] interior solido + particulas grudadas no cilindro solido
  [3] interior solido com furos das particulas (efeito queijo)   <- m3
```

Fixture de exemplo:
[`dsl/wizard_templates/_test_bed_m3_solid_holes.json`](../../dsl/wizard_templates/_test_bed_m3_solid_holes.json).

## Limitações / notas

- **Ver os furos**: as cavidades são **internas** — para enxergá-las é preciso
  **cortar** o modelo (X-Ray/Bisect no Blender, *Clip* no ParaView).
- **Partículas na superfície**: partículas que tocam a borda do núcleo viram
  "mordidas" (concavidades) em vez de bolhas fechadas — ainda é material
  removido, mas não conta como cavidade isolada na prova topológica.
- **Desempenho**: o corte é partícula a partícula; para contagens muito altas o
  m3 (Python) pode demorar. Há `max_holes` para limitar.

## Arquivos relacionados

| Papel | Arquivo |
|-------|---------|
| Constantes/normalização dos modos | [`bed_internal_modes.py`](../../scripts/python_modeling/bed_internal_modes.py) |
| Construção (Python): núcleo + furos | [`bed_shell_build.py`](../../scripts/python_modeling/bed_shell_build.py) |
| Construção (Blender): núcleo + furos | [`blender_build.py`](../../scripts/blender_scripts/packed_bed_science/blender_build.py) |
| Demo + métricas do queijo | [`cheese_demo.py`](../../scripts/python_modeling/cheese_demo.py) |
| Teste/prova automatizado | [`tests/test_solid_holes_cheese.py`](../../scripts/python_modeling/tests/test_solid_holes_cheese.py) |
| **Como provar (comandos)** | [PROVA.md](PROVA.md) |
