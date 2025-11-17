import asyncio
import csv
import statistics
import time
from typing import List, Dict, Any

try:
    from coroutines import main as run_coroutines
    from threads import main as run_threads
except ImportError:
    exit(1)

REPETICOES = 5

CENARIOS = [
    {
        "nome": "1",
        "params": {"tamanho_buffer": 5, "num_produtor": 3, "num_consumidor": 3, "itens_produtor": 20}
    },
    {
        "nome": "2",
        "params": {"tamanho_buffer": 2, "num_produtor": 10, "num_consumidor": 10, "itens_produtor": 50}
    },
    {
        "nome": "3",
        "params": {"tamanho_buffer": 50, "num_produtor": 5, "num_consumidor": 5, "itens_produtor": 200}
    },
    {
        "nome": "4",
        "params": {"tamanho_buffer": 10, "num_produtor": 50, "num_consumidor": 50, "itens_produtor": 10}
    },
    {
        "nome": "5",
        "params": {"tamanho_buffer": 10, "num_produtor": 20, "num_consumidor": 5, "itens_produtor": 50}
    },
    {
        "nome": "6",
        "params": {"tamanho_buffer": 10, "num_produtor": 5, "num_consumidor": 20, "itens_produtor": 50}
    },
]

async def run_benchmark() -> List[Dict[str, Any]]:
    resultados_finais = []

    for cenario in CENARIOS:
        nome_cenario = cenario["nome"]
        params = cenario["params"]
        
        print(f"\n--- Executando Cenário: {nome_cenario} ---")
        print(f"  Buffer: {params['tamanho_buffer']}, Produtores: {params['num_produtor']}, "
              f"Consumidores: {params['num_consumidor']}, Itens/Produtor: {params['itens_produtor']}")
        
        print(f"Rodando implementacao com corrotinas...")
        coop_times = []
        for i in range(REPETICOES):
            t = await run_coroutines(**params)
            coop_times.append(t)
            print(f"  Run {i+1}/{REPETICOES}: {t:.4f}s")
        
        coop_mean = statistics.mean(coop_times)
        coop_stdev = statistics.stdev(coop_times) if REPETICOES > 1 else 0.0
        
        # Adiciona os parâmetros ao resultado para o CSV
        resultados_finais.append({
            "cenario": nome_cenario,
            "implementacao": "corrotinas",
            **params, # Desempacota o dicionário de parâmetros aqui
            "tempo_medio": coop_mean,
            "desvio_padrao": coop_stdev,
            "runs_individuais": str([round(t, 4) for t in coop_times])
        })

        print(f"Rodando implementacao com threads...")
        preempt_times = []
        for i in range(REPETICOES):
            t = run_threads(**params)
            preempt_times.append(t)
            print(f"  Run {i+1}/{REPETICOES}: {t:.4f}s")

        preempt_mean = statistics.mean(preempt_times)
        preempt_stdev = statistics.stdev(preempt_times) if REPETICOES > 1 else 0.0
        
        resultados_finais.append({
            "cenario": nome_cenario,
            "implementacao": "threads",
            **params,
            "tempo_medio": preempt_mean,
            "desvio_padrao": preempt_stdev,
            "runs_individuais": str([round(t, 4) for t in preempt_times])
        })
    
    return resultados_finais

def save_results_to_csv(results: List[Dict[str, Any]], filename: str):
    headers = results[0].keys()
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
        print(f"\nResultados salvos em: {filename}")
    except IOError as e:
        print(f"Erro ao salvar CSV: {e}")

if __name__ == "__main__":
    print(f"Repetições por cenário: {REPETICOES}")
    
    start_total = time.perf_counter()
    resultados = asyncio.run(run_benchmark())
    save_results_to_csv(resultados, "resultados_benchmark.csv")
    end_total = time.perf_counter()

    print(f"\nConcluido\ntempo total: {end_total - start_total:.2f} segundos.")
