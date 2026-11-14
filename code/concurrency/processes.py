import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor


# CPU-heavy work: count primes with trial division. Each call takes a noticeable amount of time.
def count_primes(limit):
    count = 0
    for number in range(2, limit):
        divisor = 2
        while divisor * divisor <= number and number % divisor:
            divisor += 1
        if divisor * divisor > number:
            count += 1
    return count


# Module-level list. Each process gets its own copy of it.
shared_numbers = []


def add_number(number):
    shared_numbers.append(number)
    print(f"child process {os.getpid()} now sees {shared_numbers}")


def say_hello(label):
    print(f"{label} running in process {os.getpid()}")


# A Process runs a function in a new operating system process with its own memory.
def scenario_direct_process():
    print("--- creating a process directly ---")
    process = multiprocessing.Process(target=say_hello, args=("direct child",))
    process.start()
    process.join()


# The child changes its own copy of the list. The main process still sees an empty list.
def scenario_shared_memory():
    print("--- processes do not share memory ---")
    child = multiprocessing.Process(target=add_number, args=(42,))
    child.start()
    child.join()
    print("main process sees:", shared_numbers)


# The pool starts 4 processes. Each one can run on its own core, so the work runs in parallel.
def scenario_process_pool():
    print("--- process pool for CPU work ---")
    with ProcessPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(count_primes, [200_000] * 4))
    print("prime counts:", results)


if __name__ == "__main__":
    print(f"main process is {os.getpid()}")
    scenario_direct_process()
    scenario_shared_memory()
    scenario_process_pool()
