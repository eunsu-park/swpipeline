import psutil

# Open the file in read mode
with open('pid_list.txt', 'r') as file:
    # Read the contents of the file
    content = file.read()

# Convert the string to a list
pid_list = content.split('\n')
pid_list = [int(item) for item in pid_list if item]  # Remove empty lines

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--kill', type=bool, default=False, required=False)
args = parser.parse_args()

if args.kill:
    # Terminate each process
    for pid in pid_list:
        try:
            process = psutil.Process(pid)
            process.terminate()
            print(f"Process with PID {pid} terminated")
        except psutil.NoSuchProcess:
            print(f"No process found with PID {pid}")

    os.remove('pid_list.txt')
    exit(0)

# Monitor the status of each process
for pid in pid_list:
    try:
        process = psutil.Process(pid)
        # print(f"CPU #: {psutil.cpu_count()}")
        print(f"Process with PID {pid} exists. Status: {process.status()}. Name:{process.name()}.")
    except psutil.NoSuchProcess:
        print(f"No process found with PID {pid}")

