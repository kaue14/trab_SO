import threading
import queue  # Fila 'thread-safe'
import random
import time

# --- O Produtor (Função de Thread) ---
def producer(name: str, q: queue.Queue, items_to_produce: int):
    """
    Uma função que roda em um thread, produz itens e os coloca na fila.
    """
    # print(f"[Produtor {name}] Iniciado.") # Removido para limpar a saída do benchmark
    for i in range(items_to_produce):
        time.sleep(random.uniform(0.001, 0.01)) # Simula I/O rápido
        item = f"Item {i} (de {name})"
        q.put(item)
        # print(f"[Produtor {name}] -> Produziu: {item}")
        
    # print(f"[Produtor {name}] Concluído.")

# --- O Consumidor (Função de Thread) ---
def consumer(name: str, q: queue.Queue):
    """
    Uma função que roda em um thread e consome itens da fila.
    """
    # print(f"[Consumidor {name}] Iniciado. Aguardando itens...")
    while True:
        item = q.get()
        if item is None: # Sinal de parada
            q.task_done()
            break
            
        time.sleep(random.uniform(0.001, 0.02)) # Simula processamento rápido
        # print(f"[Consumidor {name}] <-- Consumiu: {item}")
        q.task_done()

# --- A Rotina Principal (Thread Principal) ---
def main(buffer_size: int, producer_count: int, consumer_count: int, items_per_producer: int):
    """
    Configura e executa os threads.
    Retorna o tempo total de execução.
    """
    q = queue.Queue(maxsize=buffer_size)
    producer_threads = []
    consumer_threads = []

    start_time = time.perf_counter()

    # Cria e inicia os threads dos produtores
    for i in range(producer_count):
        thread = threading.Thread(target=producer, args=(f"P-{i}", q, items_per_producer))
        thread.start()
        producer_threads.append(thread)

    # Cria e inicia os threads dos consumidores
    for i in range(consumer_count):
        thread = threading.Thread(target=consumer, args=(f"C-{i}", q))
        thread.start()
        consumer_threads.append(thread)

    # 1. Espera todos os produtores terminarem
    for thread in producer_threads:
        thread.join()

    # 2. Espera a fila ficar vazia
    q.join()

    # 3. Envia sinal de parada para os consumidores
    for _ in range(consumer_count):
        q.put(None)

    # 4. Espera os consumidores terminarem
    for thread in consumer_threads:
        thread.join()

    end_time = time.perf_counter()
    return end_time - start_time

# --- Ponto de Entrada (para execução manual) ---
if __name__ == "__main__":
    # Configurações padrão para teste manual
    BUFFER_SIZE = 5
    PRODUCER_COUNT = 3
    CONSUMER_COUNT = 3
    ITEMS_PER_PRODUCER = 10

    print("Executando versão Preemptiva (threading) manualmente...")
    total_time = main(BUFFER_SIZE, PRODUCER_COUNT, CONSUMER_COUNT, ITEMS_PER_PRODUCER)
    print(f"Tempo total (manual): {total_time:.4f} segundos")