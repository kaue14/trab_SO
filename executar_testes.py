import asyncio
import csv
import statistics
import time
from typing import List, Dict, Any

# Importa as funções 'main' dos outros arquivos
# Renomeamos para clareza
try:
    from coroutines import main as run_cooperative
    from threads import main as run_preemptive
except ImportError:
    print("Erro: Verifique se os arquivos 'produtor_consumidor_cooperativo.py' e 'produtor_consumidor_preemptivo.py' estão no mesmo diretório.")
    exit(1)

# --- Configuração dos Testes ---

# Quantas vezes repetir cada cenário (como pedido no trabalho)
REPETICOES = 5

# Definição dos cenários de teste (as "entradas" que você pediu)
CENARIOS = [
    {
        "nome": "1. Base (Pouca Carga)",
        "params": {"buffer_size": 5, "producer_count": 3, "consumer_count": 3, "items_per_producer": 20}
    },
    {
        "nome": "2. Alta Contenção (Buffer Pequeno)",
        "params": {"buffer_size": 2, "producer_count": 10, "consumer_count": 10, "items_per_producer": 50}
    },
    {
        "nome": "3. Alta Vazão (Muitos Itens)",
        "params": {"buffer_size": 50, "producer_count": 5, "consumer_count": 5, "items_per_producer": 200}
    },
    {
        "nome": "4. Muitas Tarefas (Simulando I/O)",
        "params": {"buffer_size": 10, "producer_count": 50, "consumer_count": 50, "items_per_producer": 10}
    },
    {
        "nome": "5. Dominado por Produtores",
        "params": {"buffer_size": 10, "producer_count": 20, "consumer_count": 5, "items_per_producer": 50}
    },
    {
        "nome": "6. Dominado por Consumidores",
        "params": {"buffer_size": 10, "producer_count": 5, "consumer_count": 20, "items_per_producer": 50}
    },
]

# --- Funções de Execução ---

async def run_benchmark() -> List[Dict[str, Any]]:
    """
    Executa todos os cenários para ambas as implementações.
    """
    final_results = []

    for cenario in CENARIOS:
        nome_cenario = cenario["nome"]
        params = cenario["params"]
        print(f"\n--- Executando Cenário: {nome_cenario} ---")
        
        # --- Versão Cooperativa (Asyncio) ---
        print(f"Testando Cooperativo (asyncio)...")
        coop_times = []
        for i in range(REPETICOES):
            t = await run_cooperative(**params)
            coop_times.append(t)
            print(f"  Run {i+1}/{REPETICOES}: {t:.4f}s")
        
        coop_mean = statistics.mean(coop_times)
        coop_stdev = statistics.stdev(coop_times) if REPETICOES > 1 else 0.0
        
        final_results.append({
            "cenario": nome_cenario,
            "implementacao": "Cooperativa (asyncio)",
            **params,
            "tempo_medio": coop_mean,
            "desvio_padrao": coop_stdev,
            "runs_individuais": str([round(t, 4) for t in coop_times])
        })

        # --- Versão Preemptiva (Threading) ---
        print(f"Testando Preemptivo (threading)...")
        preempt_times = []
        for i in range(REPETICOES):
            t = run_preemptive(**params)
            preempt_times.append(t)
            print(f"  Run {i+1}/{REPETICOES}: {t:.4f}s")

        preempt_mean = statistics.mean(preempt_times)
        preempt_stdev = statistics.stdev(preempt_times) if REPETICOES > 1 else 0.0
        
        final_results.append({
            "cenario": nome_cenario,
            "implementacao": "Preemptiva (threading)",
            **params,
            "tempo_medio": preempt_mean,
            "desvio_padrao": preempt_stdev,
            "runs_individuais": str([round(t, 4) for t in preempt_times])
        })
    
    return final_results

def save_results_to_csv(results: List[Dict[str, Any]], filename: str):
    """
    Salva a lista de resultados em um arquivo CSV.
    """
    if not results:
        print("Nenhum resultado para salvar.")
        return

    # Pega os cabeçalhos do primeiro resultado
    headers = results[0].keys()
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
        print(f"\nResultados salvos com sucesso em: {filename}")
    except IOError as e:
        print(f"Erro ao salvar CSV: {e}")

# --- Ponto de Entrada Principal ---
if __name__ == "__main__":
    print("Iniciando Benchmark de Concorrência (Asyncio vs Threading)")
    print(f"Repetições por cenário: {REPETICOES}")
    
    start_total = time.perf_counter()
    
    # Executa o benchmark
    all_results = asyncio.run(run_benchmark())
    
    # Salva os resultados
    save_results_to_csv(all_results, "resultados_benchmark.csv")
    
    end_total = time.perf_counter()
    print(f"\nBenchmark total concluído em {end_total - start_total:.2f} segundos.")