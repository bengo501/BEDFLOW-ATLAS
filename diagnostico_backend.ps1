# encaminha para scripts/automation (mantem compatibilidade na raiz)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
& (Join-Path $Root "scripts\automation\diagnostico_backend.ps1") @args
