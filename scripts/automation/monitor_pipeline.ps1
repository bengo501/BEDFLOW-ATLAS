# Script para monitorar o progresso do pipeline
# Uso: .\monitor_pipeline.ps1 -JobId "seu-job-id"

param(
    [Parameter(Mandatory=$false)]
    [string]$JobId = ""
)

$apiUrl = "http://localhost:8000"

  # Se não forneceu job_id, listar jobs recentes
if ([string]::IsNullOrEmpty($JobId)) {
    Write-Host "=== Jobs Recentes ===" -ForegroundColor Cyan
    try {
        # Tentar buscar jobs do pipeline completo primeiro
        $pipelineJobs = @()
        try {
            $pipelineJobs = Invoke-RestMethod -Uri "$apiUrl/api/jobs?job_type=full_pipeline" -ErrorAction SilentlyContinue
        } catch {
            # Se não houver jobs do pipeline, continuar
        }
        
        # Buscar jobs regulares
        $regularJobs = @()
        try {
            $regularJobs = Invoke-RestMethod -Uri "$apiUrl/api/jobs" -ErrorAction SilentlyContinue
        } catch {
            # Se não houver jobs regulares, continuar
        }
        
        # Combinar ambos (pipeline primeiro)
        $jobs = @()
        if ($pipelineJobs) { $jobs += $pipelineJobs }
        if ($regularJobs) { $jobs += $regularJobs }
        
        # Remover duplicatas e ordenar por data
        $jobs = $jobs | Sort-Object -Property created_at -Descending | Select-Object -First 20 -Unique
        
        if ($jobs.Count -eq 0) {
            Write-Host "Nenhum job encontrado." -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Dica: Jobs são armazenados em memória e são perdidos quando o backend é reiniciado." -ForegroundColor Gray
            Write-Host "      Inicie um novo pipeline para ver jobs ativos." -ForegroundColor Gray
            exit
        }
        
        Write-Host "`nSelecione um job para monitorar:" -ForegroundColor Yellow
        for ($i = 0; $i -lt [Math]::Min(10, $jobs.Count); $i++) {
            $job = $jobs[$i]
            $statusColor = switch ($job.status) {
                "queued" { "Yellow" }
                "running" { "Green" }
                "completed" { "Cyan" }
                "failed" { "Red" }
                default { "White" }
            }
            Write-Host "[$i] " -NoNewline
            Write-Host "$($job.job_id)" -ForegroundColor $statusColor -NoNewline
            Write-Host " - $($job.status) - $($job.progress)%"
        }
        
        $selection = Read-Host "`nDigite o número do job (ou CTRL+C para sair)"
        if ($selection -match '^\d+$' -and [int]$selection -lt $jobs.Count) {
            $JobId = $jobs[[int]$selection].job_id
        } else {
            Write-Host "Seleção inválida." -ForegroundColor Red
            exit
        }
    } catch {
        Write-Host "Erro ao listar jobs: $_" -ForegroundColor Red
        Write-Host "Certifique-se de que o backend está rodando em http://localhost:8000" -ForegroundColor Yellow
        exit
    }
}

Write-Host "`n=== Monitorando Pipeline ===" -ForegroundColor Cyan
Write-Host "Job ID: $JobId" -ForegroundColor White
Write-Host "Pressione CTRL+C para parar`n" -ForegroundColor Yellow

$lastProgress = -1
$consecutiveErrors = 0

while ($true) {
    try {
        # Tentar primeiro o endpoint do pipeline completo
        $response = $null
        try {
            $response = Invoke-RestMethod -Uri "$apiUrl/api/pipeline/job/$JobId" -ErrorAction Stop
        } catch {
            # Se não encontrar no pipeline, tentar endpoint regular
            try {
                $response = Invoke-RestMethod -Uri "$apiUrl/api/job/$JobId" -ErrorAction Stop
            } catch {
                throw $_
            }
        }
        
        $consecutiveErrors = 0
        
        Clear-Host
        Write-Host "=== STATUS DO PIPELINE ===" -ForegroundColor Cyan
        Write-Host "Job ID: $($response.job_id)" -ForegroundColor White
        Write-Host "Tipo: $($response.job_type)" -ForegroundColor Gray
        Write-Host "Status: " -NoNewline
        
        switch ($response.status) {
            "queued" { 
                Write-Host $response.status -ForegroundColor Yellow
                Write-Host "  ⏳ Aguardando para iniciar..." -ForegroundColor Yellow
            }
            "running" { 
                Write-Host $response.status -ForegroundColor Green
                Write-Host "  🔄 Executando..." -ForegroundColor Green
            }
            "completed" { 
                Write-Host $response.status -ForegroundColor Cyan
                Write-Host "  ✅ Concluído com sucesso!" -ForegroundColor Green
            }
            "failed" { 
                Write-Host $response.status -ForegroundColor Red
                Write-Host "  ❌ Falhou!" -ForegroundColor Red
            }
        }
        
        # Barra de progresso
        $progress = $response.progress
        Write-Host "`nProgresso: " -NoNewline
        Write-Host "$progress%" -ForegroundColor Green -NoNewline
        Write-Host " [" -NoNewline
        
        $barLength = 50
        $filled = [Math]::Floor($progress / 100 * $barLength)
        $empty = $barLength - $filled
        
        Write-Host ("█" * $filled) -NoNewline -ForegroundColor Green
        Write-Host ("░" * $empty) -NoNewline -ForegroundColor Gray
        Write-Host "]"
        
        # Indicar etapa atual baseado no progresso
        if ($progress -lt 15) {
            Write-Host "Etapa: Compilação .bed → .json" -ForegroundColor Cyan
        } elseif ($progress -lt 40) {
            Write-Host "Etapa: Modelagem 3D (Blender)" -ForegroundColor Cyan
        } elseif ($progress -lt 50) {
            Write-Host "Etapa: Criando caso OpenFOAM" -ForegroundColor Cyan
        } elseif ($progress -lt 100) {
            Write-Host "Etapa: Simulação CFD (WSL)" -ForegroundColor Cyan
        } else {
            Write-Host "Etapa: Concluído!" -ForegroundColor Green
        }
        
        # Timestamps
        Write-Host "`nCriado em: $($response.created_at)" -ForegroundColor Gray
        Write-Host "Última atualização: $($response.updated_at)" -ForegroundColor Gray
        
        # Arquivos gerados
        if ($response.output_files -and $response.output_files.Count -gt 0) {
            Write-Host "`nArquivos gerados ($($response.output_files.Count)):" -ForegroundColor Yellow
            $response.output_files | ForEach-Object {
                Write-Host "  ✓ $_" -ForegroundColor Green
            }
        }
        
        # Logs recentes
        if ($response.logs -and $response.logs.Count -gt 0) {
            Write-Host "`nÚltimos logs:" -ForegroundColor Yellow
            $response.logs[-8..-1] | ForEach-Object {
                if ($_ -match "✓|sucesso|completed") {
                    Write-Host "  $_" -ForegroundColor Green
                } elseif ($_ -match "✗|erro|error|failed") {
                    Write-Host "  $_" -ForegroundColor Red
                } elseif ($_ -match "⚠️|warning") {
                    Write-Host "  $_" -ForegroundColor Yellow
                } else {
                    Write-Host "  $_" -ForegroundColor White
                }
            }
        }
        
        # Mensagem de erro se houver
        if ($response.error_message) {
            Write-Host "`n❌ Erro: $($response.error_message)" -ForegroundColor Red
        }
        
        # Finalizar se concluído ou falhou
        if ($response.status -eq "completed") {
            Write-Host "`n" + ("="*50) -ForegroundColor Green
            Write-Host "✅ PIPELINE CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
            Write-Host ("="*50) -ForegroundColor Green
            if ($response.metadata.case_dir) {
                Write-Host "`n📁 Caso CFD: $($response.metadata.case_dir)" -ForegroundColor Cyan
            }
            break
        }
        
        if ($response.status -eq "failed") {
            Write-Host "`n" + ("="*50) -ForegroundColor Red
            Write-Host "❌ PIPELINE FALHOU!" -ForegroundColor Red
            Write-Host ("="*50) -ForegroundColor Red
            break
        }
        
        # Detectar se progresso está travado
        if ($progress -eq $lastProgress -and $response.status -eq "running") {
            $consecutiveErrors++
            if ($consecutiveErrors -gt 20) {
                Write-Host "`n⚠️  Progresso não mudou há mais de 1 minuto." -ForegroundColor Yellow
                Write-Host "   Verifique os logs do backend para mais detalhes." -ForegroundColor Yellow
            }
        } else {
            $consecutiveErrors = 0
        }
        
        $lastProgress = $progress
        Start-Sleep -Seconds 3
        
    } catch {
        $consecutiveErrors++
        Write-Host "`n❌ Erro ao consultar status: $_" -ForegroundColor Red
        
        if ($consecutiveErrors -gt 5) {
            Write-Host "`n⚠️  Muitos erros consecutivos. Verificando se backend está rodando..." -ForegroundColor Yellow
            try {
                $health = Invoke-RestMethod -Uri "$apiUrl/health" -TimeoutSec 2
                Write-Host "Backend está respondendo." -ForegroundColor Green
            } catch {
                Write-Host "Backend não está respondendo. Certifique-se de que está rodando." -ForegroundColor Red
                break
            }
        }
        
        Start-Sleep -Seconds 5
    }
}

Write-Host "`nMonitoramento encerrado." -ForegroundColor Gray

