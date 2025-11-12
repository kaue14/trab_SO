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

buffer_1 = 5; produtor_1 = 3; consumidor_1 = 3; itens_1 = 20;
buffer_2 = 2; produtor_2 = 10; consumidor_2 = 10; itens_2 = 50;
buffer_3 = 50; produtor_3 = 5; consumidor_3 = 5; itens_3 = 200;
buffer_4 = 10; produtor_4 = 50; consumidor_4 = 50; itens_4 = 10;
buffer_5 = 10; produtor_5 = 20; consumidor_5 = 5; itens_5 = 50;
buffer_6 = 10; produtor_6 = 5; consumidor_6 = 20; itens_6 = 50;

CENARIOS = [
    {
        "nome": "1",
        "params": {"tamanho_buffer": buffer_1, "num_produtor": produtor_1, "num_consumidor": consumidor_1, "itens_produtor": itens_1}
    },
    {
        "nome": "2",
        "params": {"tamanho_buffer": buffer_2, "num_produtor": produtor_2, "num_consumidor": consumidor_2, "itens_produtor": itens_2}
    },
    {
        "nome": "3",
        "params": {"tamanho_buffer": buffer_3, "num_produtor": produtor_3, "num_consumidor": consumidor_3, "itens_produtor": itens_3}
    },
    {
        "nome": "4",
        "params": {"tamanho_buffer": buffer_4, "num_produtor": produtor_4, "num_consumidor": consumidor_4, "itens_produtor": itens_4}
    },
    {
        "nome": "5",
        "params": {"tamanho_buffer": buffer_5, "num_produtor": produtor_5, "num_consumidor": consumidor_5, "itens_produtor": itens_5}
    },
    {
        "nome": "6",
        "params": {"tamanho_buffer": buffer_6, "num_produtor": produtor_6, "num_consumidor": consumidor_6, "itens_produtor": itens_6}
    },
]

async def run_benchmark() -> List[Dict[str, Any]]:
    final_results = []

    for cenario in CENARIOS:
        nome_cenario = cenario["nome"]
        params = cenario["params"]
        print(f"\nexecutando cenario: {nome_cenario}")
        
        print(f"rodando implementacao com corrotinas")
        coop_times = []
        for i in range(REPETICOES):
            t = await run_coroutines(**params)
            coop_times.append(t)
            print(f"  Run {i+1}/{REPETICOES}: {t:.4f}s")
        
        coop_mean = statistics.mean(coop_times)
        coop_stdev = statistics.stdev(coop_times) if REPETICOES > 1 else 0.0
        
        final_results.append({
            "cenario": nome_cenario,
            "implementacao": "corrotinas",
            **params,
            "tempo_medio": coop_mean,
            "desvio_padrao": coop_stdev,
            "runs_individuais": str([round(t, 4) for t in coop_times])
        })

        print(f"rodando implementacao com threads")
        preempt_times = []
        for i in range(REPETICOES):
            t = run_threads(**params)
            preempt_times.append(t)
            print(f"  Run {i+1}/{REPETICOES}: {t:.4f}s")

        preempt_mean = statistics.mean(preempt_times)
        preempt_stdev = statistics.stdev(preempt_times) if REPETICOES > 1 else 0.0
        
        final_results.append({
            "cenario": nome_cenario,
            "implementacao": "threads",
            **params,
            "tempo_medio": preempt_mean,
            "desvio_padrao": preempt_stdev,
            "runs_individuais": str([round(t, 4) for t in preempt_times])
        })
    
    return final_results

def save_results_to_csv(results: List[Dict[str, Any]], filename: str):
    if not results:
        print("Nenhum resultado para salvar.")
        return
    
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

if __name__ == "__main__":
    print("Iniciando Benchmark de Concorrência (Asyncio vs Threading)")
    print(f"Repetições por cenário: {REPETICOES}")
    
    start_total = time.perf_counter()
    
    all_results = asyncio.run(run_benchmark())

    save_results_to_csv(all_results, "resultados_benchmark.csv")
    
    end_total = time.perf_counter()
    print(f"\nBenchmark total concluído em {end_total - start_total:.2f} segundos.")