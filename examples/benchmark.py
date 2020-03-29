from csvquery import *
import time, math
from datetime import datetime

today = "2020-03-23"

# Benchmarking
def benchmark(func, start_func=lambda:0, times=5, digits=3):
    start = time.time()
    start_func()
    for _ in range(times):
        func()
    elapsed = round(time.time() - start, digits)
    print("elapsed time: "+str(elapsed).ljust(digits + 2, "0"))

def binary_vs_sequential(times = 5000):
    dataset = open_csv("data/coronavirus_data.csv").query({"date":today})

    print("\nWITHOUT INDEXING:")
    benchmark(lambda: dataset.query({"total_cases":{"gt":100, "comparison":Comparisons.integers}}), lambda: 0, times)
    print("\nWITH INDEXING:")
    benchmark(lambda: dataset.query({"total_cases":{"gt":100}}), lambda: dataset.index("total_cases", Comparisons.integers), times)
    print()

    dataset.index("total_cases")

binary_vs_sequential()
