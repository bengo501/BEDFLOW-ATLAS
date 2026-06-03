# atalho da área de trabalho — bed wizard (terminal)

Cria um ícone na **Área de Trabalho** que abre um terminal já executando o
wizard de leitos (`python bed_wizard.py`).

## arquivos

| arquivo | papel |
|---------|-------|
| [`../../bed_wizard_terminal.bat`](../../bed_wizard_terminal.bat) | launcher: abre o terminal, confere o Python/dependências e roda `bed_wizard.py` |
| [`gerar_icone.py`](gerar_icone.py) | gera `bed_wizard.ico` a partir de `frontend/image/logoCFDpipeline.png` |
| [`criar_atalho_desktop.ps1`](criar_atalho_desktop.ps1) | cria/atualiza o atalho `.lnk` na Área de Trabalho |
| [`criar_atalho_desktop.bat`](criar_atalho_desktop.bat) | atalho de clique duplo para rodar o script acima |
| `bed_wizard.ico` | ícone gerado (não versionar é opcional; é regenerável) |

## como usar

Dê **duplo-clique** em `criar_atalho_desktop.bat`

ou rode no PowerShell, a partir da raiz do repositório:

```powershell
powershell -ExecutionPolicy Bypass -File tools\desktop\criar_atalho_desktop.ps1
```

Isso cria o atalho **«BEDFLOW - bed wizard»** na Área de Trabalho. Ao abri-lo,
um terminal inicia já com o wizard rodando, usando a raiz do repositório como
pasta de trabalho.

## regenerar apenas o ícone

```powershell
python tools\desktop\gerar_icone.py
```

## observações

- O launcher usa o **py launcher** se existir, senão `python` do PATH.
- Se `rich`/`prompt_toolkit` não estiverem instalados, o launcher oferece
  instalar `dsl/requirements-terminal.txt` automaticamente.
- O caminho da Área de Trabalho é resolvido por
  `[Environment]::GetFolderPath('Desktop')`, então funciona mesmo com
  redirecionamento do **OneDrive** e nomes em português.
