# Validação do corte 2D — gerar o 3D junto para comparar

Ao gerar um modelo **2D** (modo `pseudo_2d_thin_slice` — a "fatia fina"), o
pipeline pode gerar **também o modelo 3D** (o leito completo, **antes** do corte)
e arquivos que põem os dois lado a lado ou sobrepostos. Assim dá para **comparar
e validar** se o corte 2D foi bem executado.

> O corte 2D em si (parede retangular fina, partículas na espessura do plano,
> companheiro 3D) está documentado no código de `thin_slice_build.py` /
> `slice_compare.py`. Este README cobre a **saída de validação** e como usá-la.

## As opções de saída (`compare_mode`)

| `compare_mode` | O que gera | Para quê |
|----------------|------------|----------|
| `off` | só a fatia 2D | não validar (mais leve) |
| `separate` *(padrão)* | 2D **+** 3D em **arquivos separados** | baixar os dois e abrir lado a lado |
| `combined` | acima **+** 2D e 3D **juntos, lado a lado** (um arquivo) | comparar os dois num só arquivo |
| `overlay` | acima **+** **2D dentro do 3D**, na posição do corte (um arquivo) | validar a **posição/forma** do corte |
| `all` | `separate` + `combined` + `overlay` | gerar tudo |

Essas opções cobrem exatamente os quatro pedidos:

1. **gerar o 3D junto** → qualquer modo ≠ `off` (o `_full3d` é sempre gerado);
2. **baixar os dois modelos** → `separate` (dois arquivos);
3. **baixar os dois juntos** → `combined` (um arquivo, lado a lado);
4. **2D dentro do 3D** → `overlay` (um arquivo, sobreposto na posição do corte).

## Arquivos gerados (ao lado da fatia `<nome>.stl`)

| Arquivo | Modo | Conteúdo |
|---------|------|----------|
| `<nome>.stl` | sempre | a **fatia 2D** |
| `<nome>_full3d.stl` (+ `_full3d_pure_bed.json`) | `separate`+ | o **leito 3D** completo, antes do corte |
| `<nome>_compare.obj` / `.mtl` / `.stl` | `combined`/`all` | 2D e 3D **lado a lado** (o 3D deslocado em X) |
| `<nome>_overlay.obj` / `.mtl` / `.stl` | `overlay`/`all` | **2D dentro do 3D** (mesma posição do corte) |

- O **`.obj`** traz **dois objetos nomeados e coloridos** (`bed_3d` e `slice_2d`):
  no _overlay_ o leito 3D fica **translúcido** (`d = 0.22`) e a fatia 2D fica
  **sólida/laranja**, então a fatia aparece **dentro** do leito — ideal para ver
  se o corte casa com a seção do leito.
- O **`.stl`** é o mesmo, em malha única (compatível com qualquer visualizador);
  no _overlay_ as malhas se sobrepõem, então use um **plano de corte** para ver a
  fatia dentro do leito.
- O `*_pure_bed.json` (sidecar da fatia) registra `compare_mode` e a lista
  `comparison_files`.

## Como usar

### No wizard (recomendado)

```bash
python bed_wizard.py
```

No questionário, em **geometry_mode** escolha `pseudo_2d_thin_slice`; em seguida,
na seção **"parametros da fatia fina"**, aparece:

```
saida de validacao do corte (2D vs 3D):
  [1] 3D em arquivo separado (baixar os dois modelos)        -> separate
  [2] 2D e 3D juntos, lado a lado (um arquivo)                -> combined
  [3] 2D dentro do 3D, na posicao do corte (um arquivo)       -> overlay
  [4] todos (separado + lado a lado + sobreposto)             -> all
  [5] so 2D (nao gerar o 3D)                                   -> off
```

### No `.bed` / JSON

```jsonc
"slice": {
  "slice_enabled": true,
  "slice_axis": "y",
  "slice_thickness": 0.004,
  "compare_mode": "overlay"     // off | separate | combined | overlay | all
}
```

> Compatível com o flag legado `preserve_full_3d`: `false` equivale a
> `compare_mode = "off"`; ausente, o padrão é `separate` (gera o 3D).

## Gerar uma demonstração

```bash
python scripts/python_modeling/slice_compare_demo.py            # gera tudo (all)
python scripts/python_modeling/slice_compare_demo.py overlay    # só o overlay
```

Saída em `generated/3d/slice_compare_demo/`:

```
leito.stl                 fatia 2D
leito_full3d.stl          leito 3D (antes do corte)
leito_compare.obj/.mtl/.stl   2D e 3D lado a lado
leito_overlay.obj/.mtl/.stl   2D dentro do 3D (translúcido)
```

### Ver / validar

- **Blender / ParaView / visualizadores OBJ**: abra `leito_overlay.obj` — o leito
  3D translúcido com a fatia 2D sólida dentro mostra, de imediato, se o corte está
  na posição certa e se a seção bate.
- **Lado a lado**: abra `leito_compare.obj` (ou `.stl`) para comparar a fatia 2D
  com o leito 3D um ao lado do outro.
- **STL only**: no `leito_overlay.stl`, use um **Clip/Bisect** para revelar a
  fatia dentro do leito.

## Testes (prova de que funciona)

```bash
cd scripts/python_modeling
python -m pytest tests/test_slice_compare.py -v
```

Esperado: **7 passed**. Os testes verificam que cada `compare_mode` gera os
arquivos certos, que o _combined_ fica mais largo (lado a lado), que o _overlay_
mantém a largura do 3D (2D dentro), e que o `.obj` tem dois objetos + materiais
(leito translúcido).

## Como funciona (resumo técnico)

Tudo no **motor Python** (`generation_backend = python_engine`):

1. [`engine/pipeline.py`](../../scripts/python_modeling/engine/pipeline.py)
   `_build_and_export_mesh`: ao fatiar, além da malha 2D, constrói o leito 3D
   completo (mesmas partículas, sem cortar) e exporta `<nome>_full3d.stl`.
2. [`slice_compare.py`](../../scripts/python_modeling/slice_compare.py)
   `export_slice_comparison(...)`: a partir das duas malhas (2D e 3D), monta os
   arquivos `_compare` (3D deslocado em X) e `_overlay` (na posição original),
   gravando `.obj` (dois objetos coloridos via `write_obj_multi`) e `.stl`.
3. [`geometry_modes.py`](../../scripts/python_modeling/geometry_modes.py)
   `resolve_slice_config`: normaliza `compare_mode` (e o legado `preserve_full_3d`).
4. [`wizard_json_loader.py`](../../dsl/wizard_json_loader.py)
   `patch_compiled_json_slice`: **mescla** as chaves de slice do wizard
   (`compare_mode` etc.) no JSON compilado — a gramática `.bed` não conhece essas
   chaves, então elas são preservadas aqui.
5. [`bed_wizard.py`](../../dsl/bed_wizard.py)
   `_fill_slice_params_interactive`: expõe o menu de validação.

### Observações

- **Backend Blender**: o caminho do Blender já preserva o 3D num
  `_full3d.blend`/`.stl` separado (validação básica). Os arquivos combinados/
  sobrepostos (`_compare`/`_overlay`) são gerados pelo **motor Python**; para o
  Blender, abra o `.blend` (que mantém os objetos) ou gere a comparação a partir
  do STL pelo motor Python.
- **Coordenadas**: a fatia 2D e o leito 3D são construídos **no mesmo referencial**
  (a fatia fica em `slice_position` no eixo do corte), então o _overlay_ alinha
  naturalmente — é isso que permite validar a posição do corte.

## Arquivos relacionados

| Papel | Arquivo |
|-------|---------|
| Saídas de comparação (OBJ/STL) | [`slice_compare.py`](../../scripts/python_modeling/slice_compare.py) |
| Pipeline (2D + 3D + comparação) | [`engine/pipeline.py`](../../scripts/python_modeling/engine/pipeline.py) |
| Config `compare_mode` | [`geometry_modes.py`](../../scripts/python_modeling/geometry_modes.py) |
| Exposição no wizard | [`bed_wizard.py`](../../dsl/bed_wizard.py) |
| Demonstração | [`slice_compare_demo.py`](../../scripts/python_modeling/slice_compare_demo.py) |
| Teste/prova | [`tests/test_slice_compare.py`](../../scripts/python_modeling/tests/test_slice_compare.py) |
