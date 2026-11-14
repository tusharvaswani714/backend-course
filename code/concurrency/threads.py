import sys
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

# A fake API that waits 2 seconds before answering, so the waiting is easy to see.
URL = "https://httpbin.org/delay/2"


def fetch(number):
    # urlopen blocks this thread until the server answers.
    with urllib.request.urlopen(URL) as response:
        return f"request {number} got status {response.status}"


def report(label):
    print(f"{label} running on thread: {threading.current_thread().name}")


def spawn_worker(number):
    report(f"spawned worker {number}")
    print(fetch(number))


def add_many(counter_box, lock=None):
    for _ in range(100_000):
        if lock is None:
            counter_box[0] += 1
        else:
            with lock:
                counter_box[0] += 1


def run_counter(lock=None):
    counter_box = [0]
    workers = [threading.Thread(target=add_many, args=(counter_box, lock)) for _ in range(4)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()
    return counter_box[0]


# Creating a Thread object does not start it. start() begins the work on a new OS thread.
# join() waits until that thread has finished.
def scenario_spawn_threads():
    print("--- spawning threads directly ---")
    threads = [threading.Thread(target=spawn_worker, args=(number,), name=f"spawned-{number}") for number in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


# A thread pool keeps a fixed number of threads and reuses them for many jobs.
# Here 6 requests share 3 threads, so at most 3 requests run at the same time.
def scenario_thread_pool():
    print("--- thread pool ---")
    with ThreadPoolExecutor(max_workers=3) as pool:
        # submit returns a future right away. The future holds the result once the job is done.
        futures = [pool.submit(fetch, number) for number in range(6)]
        # as_completed gives the futures in the order they finish.
        for future in as_completed(futures):
            print(future.result())


# counter += 1 is three steps: read, add, write. Two threads can read the same value
# before either writes, and one increment gets lost.
# The switch interval is set very low so threads switch often and the race shows up quickly.
def scenario_race_without_lock():
    print("--- shared data without a lock ---")
    sys.setswitchinterval(0.000001)
    print("counter without lock:", run_counter(), "(expected 400000)")
    sys.setswitchinterval(0.005)


# The lock makes sure only one thread changes the counter at a time.
def scenario_race_with_lock():
    print("--- shared data with a lock ---")
    print("counter with lock:", run_counter(threading.Lock()), "(expected 400000)")


if __name__ == "__main__":
    scenario_spawn_threads()
    scenario_thread_pool()
    scenario_race_without_lock()
    scenario_race_with_lock()
