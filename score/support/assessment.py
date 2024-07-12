import tracemalloc
import time


K = 10**3


def format_time(t):
    if t >= K:
        t = t/K
        if t >= 60:
            t = str(round(t/60, 2)) + ' min'
        else:
            t = str(round(t, 2)) + ' sec'
    else:
        t = str(round(t, 2)) + ' ms'
    return t


def format_memory(m):
    if m >= K:
        m = str(round(m/K, 2)) + ' MB'
    else:
        m = str(round(m, 2)) + ' KB'
    return m


def evaluate_function(func):
    def measure(*args, **kwargs):
        # start measure
        tracemalloc.start()
        t0 = time.time()

        # run function
        result = func(*args, **kwargs)

        # stop measure
        t1 = time.time()
        memory, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # format output
        span = (t1 - t0)*K  # ms
        memory = memory/K  # KB
        peak = peak/K  # KB

        span = format_time(span)
        memory = format_memory(memory)
        peak = format_memory(peak)

        print(f'\n\033[37mFunction name:\033[35;1m {func.__name__}\033[0m')
        print(f'\033[37mElapse time  :\033[36m {span}\033[0m')
        print(f'\033[37mMemory usage :\033[36m {memory}\033[0m')
        print(f'\033[37mPeak usage   :\033[36m {peak}\033[0m')

        return result
    return measure
