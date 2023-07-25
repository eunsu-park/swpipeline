import logging
from db.log import get_logger
logger = get_logger("scan_multi", logging.INFO, 'log.log')

import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--cfg', type=str, required=True)
# parser.add_argument('--add', type=bool, required=False)
args = parser.parse_args()

with open(args.cfg) as config:
    info = json.load(config)

db_cfg = info['cfg_db']
sto_cfg = info['cfg_storage']
tbl_cfgs = info['cfg_metadata']

# 프로세스 실행을 위한 명령어 생성
import subprocess

cmc = ['python', 'scan_single.py', '--db_cfg', f'{db_cfg}', '--sto_cfg', f'{sto_cfg}', '--tbl_cfg', f'{tbl_cfgs[0]}', '--create', 'True']
cproc = subprocess.Popen(cmc, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
cproc.wait()

commands = []
for tbl_cfg in tbl_cfgs:
    cmd = ['python', 'scan_single.py', '--db_cfg', f'{db_cfg}', '--sto_cfg', f'{sto_cfg}', '--tbl_cfg', f'{tbl_cfg}']
    commands.append(cmd)

import os 
import psutil

# 실행중인 프로세스가 있을 때
# pid_list 로부터 pid를 읽어와서
# pid들의 이름정보를 배열로 만듬
try:
    with open('pid_list.txt', 'r') as file:
    # Read the contents of the file
        content = file.read()

    # Convert the string to a list
    pid_list = content.split('\n')
    pid_list = [int(item) for item in pid_list if item]

    pid_infos = {}
    for pid in pid_list:
        process = psutil.Process(pid)
        name = process.name()
        pid_infos[name] = pid
except:
    pass

process_info = []
pid_list = []
# Start each command as a separate process
for command in commands:
    name = os.path.splitext(os.path.basename(command[-1]))[0]
    # 위에서 만든 커맨드에서 해당 pid의 이름과 같은 이름을 가진 프로세르를 만드려는 명령어가 있으면
    # 해당 명령어를 실행하지 않음
    if pid_infos:
        if name in pid_infos.keys():
            logger.info(f"Process '{name}' already exists with PID: {pid_infos[name]}")
            continue
    # process_info.append({'name': name, 'pid': pid})
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pid = process.pid
    logger.info(f"Process '{name}' started with PID: {pid}")
    pid_list.append(pid)

if pid_infos:
    # Open the file in append mode
    with open('pid_list.txt', 'a') as file:
        # Write each list element to a new line in the file
        for item in pid_list:
            file.write(str(item) + '\n')
else:
    # Open the file in write mode
    with open('pid_list.txt', 'w') as file:
    # Write each list element to a new line in the file
        for item in pid_list:
            file.write(str(item) + '\n')
    