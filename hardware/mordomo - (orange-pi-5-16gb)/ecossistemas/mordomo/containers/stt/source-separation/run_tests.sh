#!/bin/bash

# Script para executar os testes do serviço Source Separation

echo "======================================"
echo "Source Separation - Running Tests"
echo "======================================"
echo ""

# Verificar se pytest está instalado
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest não encontrado. Instalando dependências..."
    pip install -r requirements.txt
fi

# Executar testes
echo "🧪 Executando testes..."
pytest tests/ -v --tb=short

# Capturar código de saída
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Todos os testes passaram!"
else
    echo "❌ Alguns testes falharam."
fi

exit $EXIT_CODE
