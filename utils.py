import asyncio


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def run_concurrently(coros, limit=5):
    sem = asyncio.Semaphore(limit)

    async def sem_task(coro):
        async with sem:
            return await coro

    return await asyncio.gather(*(sem_task(c) for c in coros))
