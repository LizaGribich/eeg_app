import psutil, os
import time


def print_memory(tag=""):
    process = psutil.Process(os.getpid())
    print(f"{tag}: {process.memory_info().rss / 1024 / 1024:.2f} MB")


def start_timer():
    return time.perf_counter()


def print_time(start, tag=""):
    elapsed = time.perf_counter() - start
    print(f"{tag}: {elapsed:.4f} c")
