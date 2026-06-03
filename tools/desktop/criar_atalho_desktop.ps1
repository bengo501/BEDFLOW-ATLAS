<#
.SYNOPSIS
    Cria (ou atualiza) um atalho na Area de Trabalho que abre um terminal
    com o wizard de leitos (.bed) do BEDFLOW-ATLAS em execucao.

.DESCRIPTION
    O atalho aponta para bed_wizard_terminal.bat na raiz do repositorio, usa a
    raiz como diretorio de trabalho e o icone tools/desktop/bed_wizard.ico.
    Se o icone ainda nao existir, ele e gerado automaticamente via gerar_icone.py.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File tools\desktop\criar_atalho_desktop.ps1
#>

$ErrorActionPreference = 'Stop'

# pastas de referencia
$here = Split-Path -Parent $MyInvocation.MyCommand.Definition          # tools\desktop
$repo = (Resolve-Path (Join-Path $here '..\..')).Path                  # raiz do repo
$bat  = Join-Path $repo 'bed_wizard_terminal.bat'
$icon = Join-Path $here 'bed_wizard.ico'

if (-not (Test-Path $bat)) {
    throw "launcher nao encontrado: $bat"
}

# garantir o icone (gera se faltar e houver python disponivel)
if (-not (Test-Path $icon)) {
    $py = Get-Command py -ErrorAction SilentlyContinue
    if (-not $py) { $py = Get-Command python -ErrorAction SilentlyContinue }
    if ($py) {
        Write-Host "gerando icone..."
        & $py.Source (Join-Path $here 'gerar_icone.py')
    } else {
        Write-Warning "python nao encontrado: o atalho usara o icone padrao do .bat"
    }
}

# caminho do atalho na Area de Trabalho (resolve OneDrive / pt-BR corretamente)
$desktop = [Environment]::GetFolderPath('Desktop')
$lnk = Join-Path $desktop 'BEDFLOW - bed wizard.lnk'

$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($lnk)
$sc.TargetPath       = $bat
$sc.WorkingDirectory = $repo
$sc.WindowStyle      = 1
$sc.Description       = 'Abre o terminal com o wizard de leitos (.bed) do BEDFLOW-ATLAS'
if (Test-Path $icon) {
    $sc.IconLocation = "$icon,0"
}
$sc.Save()

Write-Host ""
Write-Host "atalho criado com sucesso:" -ForegroundColor Green
Write-Host "  $lnk"
Write-Host "  -> alvo : $bat"
Write-Host "  -> icone: $icon"
