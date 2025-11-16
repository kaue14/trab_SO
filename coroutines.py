import asyncio
import random
import time

async def producer(name: str, queue: asyncio.Queue, items_to_produce: int):
    for i in range(items_to_produce):
        await asyncio.sleep(random.uniform(0.001, 0.01))
        item = f"Item {i} (de {name})"
        await queue.put(item)

async def consumer(name: str, queue: asyncio.Queue):
    while True:
        item = await queue.get()
        await asyncio.sleep(random.uniform(0.001, 0.02))
        queue.task_done()

async def main(tamanho_buffer: int, num_produtor: int, num_consumidor: int, itens_produtor: int):
    queue = asyncio.Queue(maxsize=tamanho_buffer)
    task_produtor = []
    task_consumidor = []

    start_time = time.perf_counter()

    for i in range(num_produtor):
        task = asyncio.create_task(producer(f"P-{i}", queue, itens_produtor))
        task_produtor.append(task)

    for i in range(num_consumidor):
        task = asyncio.create_task(consumer(f"C-{i}", queue))
        task_consumidor.append(task)

    await asyncio.gather(*task_produtor)

    await queue.join()

    for task in task_consumidor:
        task.cancel()

    await asyncio.gather(*task_consumidor, return_exceptions=True)

    end_time = time.perf_counter()
    return end_time - start_time