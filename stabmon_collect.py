#!/usr/bin/env python3

import sys
import psutil
import time
import datetime
import requests
import io
import argparse

# Write to file every N seconds
WRITE_TO_FILE_INTERVAL = 5

# Default values for CLI arguments
URL_TO_PING = "http://google.com"
DEFAULT_LOG_FILE = 'stabmon.csv'
STATS_INTERVAL = 1


def get_max_cpu_process():
    max_cpu = 0
    max_proc = ""
    # Find most CPU-intensive process
    for proc in psutil.process_iter():
        try:
            # Process CPU usage can be more than 100%
            cpu = proc.cpu_percent() / psutil.cpu_count()
            if cpu > max_cpu:
                max_cpu = cpu
                max_proc = proc.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return max_proc + ": " + str(round(max_cpu, 2))


def get_max_mem_process():
    max_mem = 0
    max_proc = ""
    # Find most Memory-intensive process
    for proc in psutil.process_iter():
        try:
            mem = int(proc.memory_info().vms / 1024 / 1024)
            if mem > max_mem:
                max_mem = mem
                max_proc = proc.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return max_proc + ": " + str(max_mem)


def net_call(url):
    if not url:
        return 0, ""
    try:
        response = requests.head(url, timeout=5)
        return int(response.elapsed.total_seconds() * 1000), ""
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return 5000, str(sys.exc_info()[0])


def collect_stats(url):
    mem = psutil.virtual_memory()
    mem_usage = int((1 - mem.available / mem.total) * 100)
    latency, err = net_call(url)
    max_mem_proc = get_max_mem_process()
    max_cpu_proc = get_max_cpu_process()
    return f'{datetime.datetime.now().isoformat()}, {psutil.cpu_percent()}, "{max_cpu_proc}", {mem_usage}, "{max_mem_proc}", {latency}, "{err}"\n'


def main():
    parser = argparse.ArgumentParser(description='Log CPU, memory and network latency to CSV.')
    parser.add_argument("--log", help=f'Log file location, defaults to "{DEFAULT_LOG_FILE}"', default=DEFAULT_LOG_FILE)
    parser.add_argument("--url", help=f"URL for network availability check. HTTP HEAD request will be issued. Use your router's favicon (e.g. http://192.168.1.1/favicon.ico). Defaults to {URL_TO_PING}", default=URL_TO_PING)
    parser.add_argument("--interval", type=float, help=f"Interval for resource usage checking, seconds. Defaults to {STATS_INTERVAL} seconds", default=STATS_INTERVAL)
    args = parser.parse_args()
    print(f"Logging to {args.log}")

    if not args.url:
        print("Network availability check is disabled")

    while True:
        # Print to buffer and periodically write it to file.
        # This takes care of log file being deleted (e.g. by log rotator)
        buffer = io.StringIO()
        for x in range(int(WRITE_TO_FILE_INTERVAL / args.interval)):
            buffer.write(collect_stats(args.url))
            time.sleep(args.interval)

        f = open(args.log, "a")
        f.write(buffer.getvalue())
        f.close()
        buffer.close()


if __name__ == "__main__":
    main()
