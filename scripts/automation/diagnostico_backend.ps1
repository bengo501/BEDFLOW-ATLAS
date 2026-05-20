# Script de Diagnóstico do Backend
# Verifica se Blender, OpenFOAM e WSL estão configurados corretamente

Write-Host "=== DIAGNÓSTICO DO BACKEND ===" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Blender
Write-Host "[1/4] Verificando Blender..." -ForegroundColor Yellow
$blenderPaths = @(
    "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 3.5\blender.exe"
)

$blenderFound = $false
foreach ($path in $blenderPaths) {
    if (Test-Path $path) {
        Write-Host "  ✓ Blender encontrado: $path" -ForegroundColor Green
        $blenderFound = $true
        
        # Testar execução
        try {
            $version = & $path --version 2>&1
            Write-Host "  ✓ Versão: $($version[0])" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠️  Blender encontrado mas não executa corretamente" -ForegroundColor Yellow
        }
        break
    }
}

if (-not $blenderFound) {
    Write-Host "  ❌ Blender NÃO encontrado nos caminhos padrão" -ForegroundColor Red
    Write-Host "     Caminhos verificados:" -ForegroundColor Gray
    foreach ($path in $blenderPaths) {
        Write-Host "       - $path" -ForegroundColor Gray
    }
    Write-Host "     Solução: Instale o Blender ou configure o caminho em backend/app/services/blender_service.py" -ForegroundColor Yellow
}

# Tentar comando simples
if (-not $blenderFound) {
    try {
        $test = & blender --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Blender encontrado via PATH: blender" -ForegroundColor Green
            $blenderFound = $true
        }
    } catch {
        Write-Host "  ❌ Blender não está no PATH" -ForegroundColor Red
    }
}

Write-Host ""

# 2. Verificar Script do Blender
Write-Host "[2/4] Verificando Scripts do Blender..." -ForegroundColor Yellow
$blenderScript = "scripts\blender_scripts\leito_extracao.py"
if (Test-Path $blenderScript) {
    Write-Host "  ✓ Script encontrado: $blenderScript" -ForegroundColor Green
} else {
    Write-Host "  ❌ Script NÃO encontrado: $blenderScript" -ForegroundColor Red
    Write-Host "     Solução: Verifique se o arquivo existe no projeto" -ForegroundColor Yellow
}

Write-Host ""

# 3. Verificar WSL
Write-Host "[3/4] Verificando WSL..." -ForegroundColor Yellow
try {
    $wslList = wsl --list --quiet 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ WSL está instalado" -ForegroundColor Green
        if ($wslList.Count -gt 0) {
            Write-Host "  ✓ Distribuições instaladas:" -ForegroundColor Green
            foreach ($distro in $wslList) {
                if ($distro.Trim()) {
                    Write-Host "     - $distro" -ForegroundColor Gray
                }
            }
        } else {
            Write-Host "  ⚠️  WSL instalado mas nenhuma distribuição configurada" -ForegroundColor Yellow
            Write-Host "     Solução: Instale Ubuntu via: wsl --install" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ❌ WSL não está instalado ou não está funcionando" -ForegroundColor Red
        Write-Host "     Solução: Instale WSL2 via: wsl --install" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ Erro ao verificar WSL: $_" -ForegroundColor Red
    Write-Host "     Solução: Instale WSL2 via: wsl --install" -ForegroundColor Yellow
}

Write-Host ""

# 4. Verificar OpenFOAM no WSL
Write-Host "[4/4] Verificando OpenFOAM no WSL..." -ForegroundColor Yellow
try {
    $openfoamCheck = wsl bash -c "which simpleFoam 2>/dev/null || echo 'NOT_FOUND'" 2>&1
    if ($openfoamCheck -match "NOT_FOUND") {
        Write-Host "  ❌ OpenFOAM não encontrado no WSL" -ForegroundColor Red
        Write-Host "     Solução: Instale OpenFOAM no WSL/Ubuntu" -ForegroundColor Yellow
    } else {
        Write-Host "  ✓ OpenFOAM encontrado no WSL" -ForegroundColor Green
        $version = wsl bash -c "simpleFoam -version 2>&1 | head -1" 2>&1
        Write-Host "     Versão: $version" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ⚠️  Não foi possível verificar OpenFOAM (WSL pode não estar configurado)" -ForegroundColor Yellow
}

Write-Host ""

# 5. Verificar Script OpenFOAM
Write-Host "[5/5] Verificando Scripts OpenFOAM..." -ForegroundColor Yellow
$openfoamScript = "scripts\openfoam_scripts\setup_openfoam_case.py"
if (Test-Path $openfoamScript) {
    Write-Host "  ✓ Script encontrado: $openfoamScript" -ForegroundColor Green
} else {
    Write-Host "  ❌ Script NÃO encontrado: $openfoamScript" -ForegroundColor Red
    Write-Host "     Solução: Verifique se o arquivo existe no projeto" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== RESUMO ===" -ForegroundColor Cyan

$issues = @()
if (-not $blenderFound) {
    $issues += "Blender não encontrado"
}
if (-not (Test-Path $blenderScript)) {
    $issues += "Script do Blender não encontrado"
}
if (-not (Test-Path $openfoamScript)) {
    $issues += "Script do OpenFOAM não encontrado"
}

if ($issues.Count -eq 0) {
    Write-Host "✓ Todos os componentes básicos estão presentes!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Yellow
    Write-Host "1. Verifique os logs do backend quando tentar gerar modelos" -ForegroundColor White
    Write-Host "2. Verifique os jobs via: http://localhost:8000/api/jobs" -ForegroundColor White
    Write-Host "3. Use o script monitor_pipeline.ps1 para acompanhar o progresso" -ForegroundColor White
} else {
    Write-Host "⚠️  Problemas encontrados:" -ForegroundColor Yellow
    foreach ($issue in $issues) {
        Write-Host "  - $issue" -ForegroundColor Red
    }
}

Write-Host ""

