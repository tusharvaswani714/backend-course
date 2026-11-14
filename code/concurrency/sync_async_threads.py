import asyncio
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import httpx

URL = "https://httpbin.org/delay/2"
COUNT = 6


def fetch_blocking(_):
    with urllib.request.urlopen(URL) as response:
        return response.status


async def fetch_async(client):
    response = await client.get(URL)
    return response.status_code


async def run_async():
    async with httpx.AsyncClient(timeout=30) as client:
        return await asyncio.gather(*(fetch_async(client) for _ in range(COUNT)))


def timed(label, run):
    started = time.perf_counter()
    statuses = run()
    print(f"{label}: {time.perf_counter() - started:.2f}s, statuses {statuses}")


# Six requests, one after another. Each one waits 2 seconds, so the total is about 12 seconds.
def scenario_one_at_a_time():
    timed("one at a time", lambda: [fetch_blocking(number) for number in range(COUNT)])


# Six requests on six threads. The threads wait at the same time, so the total is about 2 seconds.
def scenario_threads():
    def run_with_threads():
        with ThreadPoolExecutor(max_workers=COUNT) as pool:
            return list(pool.map(fetch_blocking, range(COUNT)))

    timed("threads", run_with_threads)


# Six requests on one thread with asyncio. Each request waits without blocking the others,
# so the total is about 2 seconds, the same as threads, with less overhead per request.
def scenario_asyncio():
    timed("asyncio", lambda: asyncio.run(run_async()))


if __name__ == "__main__":
    scenario_one_at_a_time()
    scenario_threads()
    scenario_asyncio()
