import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def count_primes(limit):
    count = 0
    for number in range(2, limit):
        divisor = 2
        while divisor * divisor <= number and number % divisor:
            divisor += 1
        if divisor * divisor > number:
            count += 1
    return count


def run_directly(jobs):
    return [count_primes(job) for job in jobs]


def run_with_threads(jobs):
    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        return list(pool.map(count_primes, jobs))


def run_with_processes(jobs):
    with ProcessPoolExecutor(max_workers=len(jobs)) as pool:
        return list(pool.map(count_primes, jobs))


def timed(label, run, jobs):
    started = time.perf_counter()
    run(jobs)
    print(f"{label}: {time.perf_counter() - started:.2f}s")


JOB = 400_000
JOBS = [JOB] * 4


# One job, no threads. This is the time for a single piece of work.
def scenario_one_job_no_threads():
    timed("1 job, no threads", run_directly, [JOB])


# Four jobs, no threads. A plain loop runs them one after another, so it takes about four times as long.
def scenario_four_jobs_no_threads():
    timed("4 jobs, no threads", run_directly, JOBS)


# Four jobs on four threads. The GIL lets only one thread run Python at a time,
# so the total time stays about the same as the plain loop.
def scenario_four_jobs_threads():
    timed("4 jobs, 4 threads", run_with_threads, JOBS)


# Four jobs on four processes. Each process has its own GIL and can run on its own core,
# so the four jobs run at the same time.
def scenario_four_jobs_processes():
    timed("4 jobs, 4 processes", run_with_processes, JOBS)


if __name__ == "__main__":
    scenario_one_job_no_threads()
    scenario_four_jobs_no_threads()
    scenario_four_jobs_threads()
    scenario_four_jobs_processes()
