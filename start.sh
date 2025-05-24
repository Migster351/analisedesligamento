#!/bin/bash

echo "Iniciando Sistema de Análise de Entrevistas de Desligamento..."
echo "Certifique-se de que todas as dependências foram instaladas com:"
echo "    pip install -r requirements.txt"
echo ""

# Verifica se python3 está disponível
if command -v python3 > /dev/null 2>&1; then
    echo "Iniciando aplicação com python3..."
    python3 run.py
else
    echo "Iniciando aplicação com python..."
    python run.py
fi

# Em caso de erro, mantém o terminal aberto
read -p "Pressione Enter para sair..." 