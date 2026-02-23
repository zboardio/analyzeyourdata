import os
import psutil
import time


def monitor_memory(interval=3):
    """RAM monitoring function"""
    process = psutil.Process(os.getpid())
    while True:
        mem = process.memory_info().rss / 1024 / 1024  # in MB
        print(f"[MEMORY] RSS: {mem:.2f} MB")
        time.sleep(interval)
