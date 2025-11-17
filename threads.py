import threading
import random
import time
import collections

def produz(valor: int, buffer: collections.deque):
    buffer.append(valor)

def produtor(name: str, 
             buffer: collections.deque, 
             lock: threading.Lock, 
             empty_sem: threading.Semaphore, 
             full_sem: threading.Semaphore, 
             items_to_produce: int):

    for i in range(items_to_produce):
        time.sleep(random.uniform(0.001, 0.01)) 
        
        item = f"Item {i} (de {name})"
        empty_sem.acquire()
        lock.acquire()
        produz(item, buffer)
        lock.release()
        full_sem.release()
        
def consome(buffer: collections.deque):
    return buffer.popleft()

def consumidor(name: str, 
             buffer: collections.deque, 
             lock: threading.Lock, 
             empty_sem: threading.Semaphore, 
             full_sem: threading.Semaphore):

    while True:
        full_sem.acquire()
        lock.acquire()
        item = consome(buffer)
        lock.release()
        empty_sem.release()
        
        if item is None:
            break
        time.sleep(random.uniform(0.001, 0.02))

def main(tamanho_buffer: int, num_produtor: int, num_consumidor: int, itens_produtor: int):
    buffer = collections.deque(maxlen=tamanho_buffer) 
    empty_sem = threading.Semaphore(tamanho_buffer)
    full_sem = threading.Semaphore(0)
    lock = threading.Lock()
    
    produtor_threads = []
    consumidor_threads = []

    start_time = time.perf_counter()

    for i in range(num_produtor):
        thread = threading.Thread(target=produtor, args=(f"P-{i}", buffer, lock, empty_sem, full_sem, itens_produtor))
        thread.start()
        produtor_threads.append(thread)

    for i in range(num_consumidor):
        thread = threading.Thread(target=consumidor, args=(f"C-{i}", buffer, lock, empty_sem, full_sem))
        thread.start()
        consumidor_threads.append(thread)

    for thread in produtor_threads:
        thread.join()

    for _ in range(num_consumidor):
        empty_sem.acquire()
        lock.acquire()
        produz(None, buffer)
        lock.release()
        full_sem.release()

    for thread in consumidor_threads:
        thread.join()

    end_time = time.perf_counter()
    return end_time - start_time