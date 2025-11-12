import asyncio
import random
import time

# --- O Produtor (Corrotina) ---
async def producer(name: str, queue: asyncio.Queue, items_to_produce: int):
    """
    Uma corrotina que produz itens e os coloca na fila.
    """
    # print(f"[Produtor {name}] Iniciado.")
    for i in range(items_to_produce):
        await asyncio.sleep(random.uniform(0.001, 0.01)) # Simula I/O rápido
        item = f"Item {i} (de {name})"
        await queue.put(item)
        # print(f"[Produtor {name}] -> Produziu: {item}")
        
    # print(f"[Produtor {name}] Concluído.")

# --- O Consumidor (Corrotina) ---
async def consumer(name: str, queue: asyncio.Queue):
    """
    Uma corrotina que consome itens da fila.
    """
    # print(f"[Consumidor {name}] Iniciado. Aguardando itens...")
    while True:
        item = await queue.get()
        await asyncio.sleep(random.uniform(0.001, 0.02)) # Simula processamento rápido
        # print(f"[Consumidor {name}] <-- Consumiu: {item}")
        queue.task_done()

# --- A Rotina Principal (Orquestrador) ---
async def main(buffer_size: int, producer_count: int, consumer_count: int, items_per_producer: int):
    """
    Configura e executa o loop de eventos principal.
    Retorna o tempo total de execução.
    """
    queue = asyncio.Queue(maxsize=buffer_size)
    producer_tasks = []
    consumer_tasks = []

    start_time = time.perf_counter()

    # Cria as tarefas (tasks) dos produtores
    for i in range(producer_count):
        task = asyncio.create_task(producer(f"P-{i}", queue, items_per_producer))
        producer_tasks.append(task)

    # Cria as tarefas (tasks) dos consumidores
    for i in range(consumer_count):
        task = asyncio.create_task(consumer(f"C-{i}", queue))
        consumer_tasks.append(task)

    # 1. Espera todos os produtores terminarem
    await asyncio.gather(*producer_tasks)

    # 2. Espera a fila ficar vazia
    await queue.join()

    # 3. Cancela as tarefas dos consumidores
    for task in consumer_tasks:
        task.cancel()

    # Espera os cancelamentos serem processados
    await asyncio.gather(*consumer_tasks, return_exceptions=True)

    end_time = time.perf_counter()
    return end_time - start_time

# --- Ponto de Entrada (para execução manual) ---
if __name__ == "__main__":
    # Configurações padrão para teste manual
    BUFFER_SIZE = 5
    PRODUCER_COUNT = 3
    CONSUMER_COUNT = 3
    ITEMS_PER_PRODUCER = 10
    
    print("Executando versão Cooperativa (asyncio) manualmente...")
    total_time = asyncio.run(main(BUFFER_SIZE, PRODUCER_COUNT, CONSUMER_COUNT, ITEMS_PER_PRODUCER))
    print(f"Tempo total (manual): {total_time:.4f} segundos")