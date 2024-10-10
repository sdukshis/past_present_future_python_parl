import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.append(SCRIPT_DIR)

# from count_primes import count_primes as count_primes_cpp

import pickle
import threading
import textwrap as tw
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import pyperf

import test.support.interpreters as interpreters
# import interpreters

# import interpreters

LIMIT = 20000
CPUS = os.cpu_count()

class SyncCounter():
    def __init__(self, initial=0):
        self._lock = threading.Lock()
        self._counter = initial
    
    def get(self):
        with self._lock:
            return self._counter

    def inc(self, val=1):
        with self._lock:
            prev_val = self._counter
            self._counter += val
        return prev_val
    

def isprime(n):
    if n < 2:
        return False
    
    for i in range(2, n):
        if n % i == 0:
            return False
    
    return True

class ExecThread(threading.Thread):
    def __init__(self, begin, end, step, total_result):
        super().__init__()
        self._begin = begin
        self._end = end
        self._step = step
        self._total_result = total_result

    def run(self):
        result = 0
        for i in range(self._begin, self._end, self._step):
            result += isprime(i)

        self._total_result.inc(result)

class SubInthread(threading.Thread):
    def __init__(self, begin, end, step, total_result):
        super().__init__()
        self._begin = begin
        self._end = end
        self._step = step
        self._total_result = total_result
        self._interp = subinterpreters.create()

    def run(self):
        chan_id = subinterpreters.channel_create()
        subinterpreters.run_string(self._interp, tw.dedent("""
            # import pickle
            import _interpreters as subinterpreters

            def isprime(n):
                if n < 2:
                    return False
                
                for i in range(2, n):
                    if n % i == 0:
                        return False
                
                return True
            
            result = 0;
            for i in range(begin, end, step):
                result += isprime(i)

            subinterpreters.channel_send(chan_id, result.to_bytes(8, 'big'))

        """), shared=dict(
                begin=self._begin,
                end=self._end,
                step=self._step,
                chan_id=chan_id,
        ))

        raw_result = subinterpreters.channel_recv(chan_id)
        subinterpreters.channel_release(chan_id)
        result = int.from_bytes(raw_result, 'big')
        self._total_result.inc(result)
        subinterpreters.destroy(self._interp)

def count_primes_single():
    result = 1 # 2 is prime
    for n in range(3, LIMIT, 2):
        result += isprime(n)
    
    return result

def count_primes_multithreading():
    total_result = SyncCounter(1) # 2 is prime
    odds = [2*i + 1 for i in range(CPUS)]

    jobs = [ExecThread(odds[i], LIMIT, 2*CPUS, total_result) for i in range(CPUS)]
    for job in jobs:
        job.start()
    for job in jobs:
        job.join()
    return total_result.get()

def count_primes_mt():
    odds = [2*i + 1 for i in range(CPUS)]
    total_result = 1 # 2 is prime
    with ThreadPoolExecutor(CPUS) as executor:
        total_result += sum(executor.map(count_primes_step, odds, [LIMIT]*CPUS, [2*CPUS]*CPUS))
    return total_result

def count_primes_mp():
    odds = [2*i + 1 for i in range(CPUS)]
    total_result = 1 # 2 is prime
    with ProcessPoolExecutor(CPUS) as executor:
        total_result += sum(executor.map(count_primes_step, odds, [LIMIT]*CPUS, [2*CPUS]*CPUS))
    return total_result


def count_primes_subinterpreters():
    total_result = SyncCounter(1)
    odds = [2*i + 1 for i in range(CPUS)]

    jobs = [SubInthread(odds[i], LIMIT, 2*CPUS, total_result) for i in range(CPUS)]
    for job in jobs:
        job.start()
    for job in jobs:
        job.join()
    return total_result.get()

_PICKLED = 1

def count_primes_interpreter_worker():
    from test.support.interpreters.queues import Queue, _PICKLED

    results = Queue(result_queue_id, _fmt=_PICKLED)

    def isprime(n):
        if n < 2:
            return False
        
        for i in range(2, n):
            if n % i == 0:
                return False
        
        return True
    
    result = 0
    for i in range(BEGIN, LIMIT, STEP):
        result += isprime(i)

    results.put_nowait(result)
    # _queues.put(result_queue_id, pickle.dumps(result), 1)


def count_primes_interpreters():
    results = interpreters.create_queue(maxsize=CPUS)
    odds = [2*i + 1 for i in range(CPUS)]
   
    interps = [interpreters.create() for i in range(CPUS)]

    for begin, interp in zip(odds, interps):
        interp.prepare_main({
            "BEGIN": begin,
            "LIMIT": LIMIT,
            "STEP": 2*CPUS,
            "result_queue_id": results.id,
        })

    threads = [interp.call_in_thread(count_primes_interpreter_worker) for interp in interps]
    for thread in threads:
        thread.join()
    
    total_result = 1 # 2 is prime
    while not results.empty():
        total_result += results.get()
    return total_result

def count_primes_step(begin, end, step):
    result = 0
    for i in range(begin, end, step):
        result += isprime(i)
    
    return result

def count_primes_multiprocessing():
    odds = [2*i + 1 for i in range(CPUS)]
    with Pool(CPUS) as p:
       total_result = sum(p.starmap(count_primes_step, [(odds[i], LIMIT, 2*CPUS) for i in range(CPUS)]))
    return total_result + 1  # +1 for 2 is prime

# def count_primes_ext():
#     return count_primes_cpp(LIMIT, CPUS)

def main():
    # print(count_primes_single())
    # print(count_primes_multithreading())
    # print(count_primes_subinterpreters())
    # print(count_primes_mt())
    # print(count_primes_mp())
    # print(count_primes_interpreters())
    # print(count_primes_multiprocessing())
    # print(count_primes_ext())
    runner = pyperf.Runner(
        loops=0,
        # processes=1
    )
    runner.bench_func("count_primes_single", count_primes_single)
    # runner.bench_func("count_primes_ext", count_primes_ext)
    runner.bench_func("count_primes_mt", count_primes_mt)
    # runner.bench_func("count_primes_interpreters", count_primes_interpreters)
    # runner.bench_func("count_primes_mp", count_primes_mp)

if __name__ == "__main__":
    main()