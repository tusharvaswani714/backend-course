import time
import urllib.request
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

URL = "https://httpbin.org/delay/2"
COUNT = 6


# A waiting job. It spends its time waiting for the server, not computing.
def fetch(_):
    with urllib.request.urlopen(URL) as response:
        return response.status


def timed(label, run):
    started = time.perf_counter()
    statuses = run()
    print(f"{label}: {time.perf_counter() - started:.2f}s, statuses {statuses}")


# Six waiting jobs on six threads. While one thread waits, the others wait too,
# so the total time is about the time of one request.
def scenario_io_on_threads():
    def run():
        with ThreadPoolExecutor(max_workers=COUNT) as pool:
            return list(pool.map(fetch, range(COUNT)))

    timed("IO work on threads", run)


# The same six waiting jobs on six processes. It also finishes in about one request's time,
# but each process costs more memory and startup time than a thread.
def scenario_io_on_processes():
    def run():
        with ProcessPoolExecutor(max_workers=COUNT) as pool:
            return list(pool.map(fetch, range(COUNT)))

    timed("IO work on processes", run)


if __name__ == "__main__":
    scenario_io_on_threads()
    scenario_io_on_processes()
