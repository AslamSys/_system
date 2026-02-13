# PowerShell script para executar os testes do serviço Source Separation

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Source Separation - Running Tests" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se pytest está instalado
$pytestExists = Get-Command pytest -ErrorAction SilentlyContinue

if (-not $pytestExists) {
    Write-Host "❌ pytest não encontrado. Instalando dependências..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Executar testes
Write-Host "🧪 Executando testes..." -ForegroundColor Green
pytest tests/ -v --tb=short

# Capturar código de saída
$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "✅ Todos os testes passaram!" -ForegroundColor Green
} else {
    Write-Host "❌ Alguns testes falharam." -ForegroundColor Red
}

exit $exitCode
