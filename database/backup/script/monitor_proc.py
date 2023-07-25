"""
pid_list.txt파일에 있는 pid를 가진 프로세스 모니터링 코드 

--kill 옵션을 주고 실행하면 해당 프로세스들을 모두 종료시킴
"""
import os
from pathlib import Path
current_dir = os.path.dirname(os.path.realpath(__file__))
path = Path(current_dir)
parent = path.parent.absolute().parent.absolute()
etc_dir = '{}/etc'.format(str(parent))
if not os.path.exists(etc_dir):
    os.makedirs(etc_dir)
pid_list_path = os.path.join(etc_dir, 'pid_list.txt')


import psutil

# Open the file in read mode
with open(pid_list_path, 'r') as file:
    # Read the contents of the file
    content = file.read()

# Convert the string to a list
pid_list = content.split('\n')
pid_list = [int(item) for item in pid_list if item]  # Remove empty lines

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--kill', action='store_true')
parser.set_defaults(kill=False)
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

    os.remove(pid_list_path)
    exit(0)

# Monitor the status of each process
for pid in pid_list:
    try:
        process = psutil.Process(pid)
        # print(f"CPU #: {psutil.cpu_count()}")
        print(f"Process with PID {pid} exists. Status: {process.status()}. Name:{process.name()}.")
    except psutil.NoSuchProcess:
        print(f"No process found with PID {pid}")

