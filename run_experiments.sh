#!/bin/bash
# Este é um script de shell para executar os experimentos de concorrência.
# Ele garante que o ambiente Linux possa rodar o projeto facilmente.

echo "=========================================================="
echo "Iniciando a execução dos experimentos (Asyncio vs Threading)..."
echo "Isso pode levar alguns segundos ou minutos."
echo "=========================================================="

# Executa o script principal do Python 3
# Este script irá, por sua vez, chamar os outros dois
# e gerar o arquivo 'resultados_benchmark.csv'.
python3 executar_testes.py

echo "=========================================================="
echo "Experimentos concluídos!"
echo "Os resultados foram salvos em: results/resultados_benchmark.csv"
echo "=========================================================="