# encaminha para scripts/automation (mantem compatibilidade na raiz)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
& (Join-Path $Root "scripts\automation\monitor_pipeline.ps1") @args
