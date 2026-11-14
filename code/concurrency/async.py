import asyncio
import urllib.request

import httpx

# A fake API that waits the number of seconds in the path before answering.
DELAY_URL = "https://httpbin.org/delay/{seconds}"


# An async def function is a coroutine. Calling it only creates the coroutine.
# Nothing runs until it is awaited or wrapped in a task.
async def fetch(client, seconds):
    response = await client.get(DELAY_URL.format(seconds=seconds))
    return seconds, response.status_code


# A blocking function: urlopen waits, and while it waits nothing else can run on this thread.
def blocking_fetch(seconds):
    with urllib.request.urlopen(DELAY_URL.format(seconds=seconds)) as response:
        return response.status


# Pauses only this task. Other tasks keep running while it waits.
async def pause(name, seconds):
    await asyncio.sleep(seconds)
    print(f"{name} woke up after {seconds}s")


# Counts how many times the event loop got back to this task.
async def heartbeat(ticks):
    while True:
        ticks[0] += 1
        await asyncio.sleep(0)


async def cancellable(client):
    try:
        return await fetch(client, 10)
    except asyncio.CancelledError:
        # CancelledError is raised at the await. Cleanup can happen here.
        print("cancelled, cleaning up")
        raise
    finally:
        print("finally always runs")


async def broken(client):
    response = await client.get("https://httpbin.org/status/500")
    response.raise_for_status()


# await runs the coroutine and waits for its result before the next line runs.
async def scenario_await(client):
    print("--- await ---")
    print("await result:", await fetch(client, 1))


# create_task starts the coroutine in the background right away. The task can be checked and awaited later.
async def scenario_create_task(client):
    print("--- create_task ---")
    task = asyncio.create_task(fetch(client, 2))
    print("done right after creating:", task.done())
    print("result:", await task)
    print("done after awaiting:", task.done())


# gather runs everything together and returns results in the order you passed them.
async def scenario_gather(client):
    print("--- gather ---")
    results = await asyncio.gather(fetch(client, 3), fetch(client, 1), fetch(client, 2))
    print("gather results:", results)


# as_completed gives each result as soon as it finishes, so the fastest comes first.
async def scenario_as_completed(client):
    print("--- as_completed ---")
    tasks = [asyncio.create_task(fetch(client, seconds)) for seconds in [3, 1, 2]]
    for finished in asyncio.as_completed(tasks):
        seconds, status = await finished
        print(f"finished first: the {seconds}s request, status {status}")


# asyncio.sleep pauses one task without blocking the others.
async def scenario_sleep(client):
    print("--- asyncio.sleep ---")
    await asyncio.gather(pause("first", 1), pause("second", 2))


# A blocking call run directly inside async code freezes the event loop.
# The heartbeat task gets very few turns while the blocking call runs.
async def scenario_blocking_direct(client):
    print("--- blocking call directly inside async code ---")
    ticks = [0]
    other = asyncio.create_task(heartbeat(ticks))
    await asyncio.sleep(0)
    status = blocking_fetch(3)
    other.cancel()
    print(f"blocking call returned {status}, heartbeat ran {ticks[0]} times")


# The same blocking call through asyncio.to_thread runs in a thread, so the event loop stays free.
async def scenario_blocking_to_thread(client):
    print("--- same blocking call through asyncio.to_thread ---")
    ticks = [0]
    other = asyncio.create_task(heartbeat(ticks))
    await asyncio.sleep(0)
    status = await asyncio.to_thread(blocking_fetch, 3)
    other.cancel()
    print(f"blocking call returned {status}, heartbeat ran {ticks[0]} times")


# cancel() asks a task to stop. The task gets CancelledError at its next await, and can clean up.
async def scenario_cancel(client):
    print("--- cancel ---")
    job = asyncio.create_task(cancellable(client))
    # Yield once so the task starts and is waiting on the request.
    await asyncio.sleep(0)
    job.cancel()
    try:
        await job
    except asyncio.CancelledError:
        print("await raised CancelledError")
    print("job.cancelled():", job.cancelled())


# An exception in a task only shows up when you await the task or read its result.
async def scenario_exceptions(client):
    print("--- exceptions in tasks ---")
    failing = asyncio.create_task(broken(client))
    try:
        await failing
    except httpx.HTTPStatusError as error:
        print("caught from the task:", error.response.status_code)
    print("failing.done():", failing.done())


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        await scenario_await(client)
        await scenario_create_task(client)
        await scenario_gather(client)
        await scenario_as_completed(client)
        await scenario_sleep(client)
        await scenario_blocking_direct(client)
        await scenario_blocking_to_thread(client)
        await scenario_cancel(client)
        await scenario_exceptions(client)


if __name__ == "__main__":
    # asyncio.run starts the event loop, runs main, then closes the loop.
    asyncio.run(main())
