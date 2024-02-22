"""
multi_cfg 파일의 정보를 가지고, scan_single.py를 여러번 실행하는 코드
"""

import logging
from db.log import get_logger
logger = get_logger("scan_multi", logging.INFO)

import os
import json
import argparse
from pathlib import Path

current_dir = os.path.dirname(os.path.realpath(__file__))
path = Path(current_dir)
parent = path.parent.absolute().parent.absolute()
etc_dir = '{}/etc'.format(str(parent))
if not os.path.exists(etc_dir):
    os.makedirs(etc_dir)
pid_list_path = os.path.join(etc_dir, 'pid_list.txt')
scan_single_path = os.path.join(current_dir, 'scan_single.py')

# 설정파일 읽어오기
parser = argparse.ArgumentParser()
parser.add_argument('--cfg', type=str, required=True)
args = parser.parse_args()

multi_cfg_path = os.path.abspath(args.cfg)
multi_cfg_path_folder = os.path.dirname(multi_cfg_path)
with open(multi_cfg_path) as config:
    info = json.load(config)

db_cfg = info['cfg_db']
if os.path.isabs(db_cfg) is False:
    db_cfg = os.path.join(multi_cfg_path_folder, db_cfg)

sto_cfg = info['cfg_storage']
if os.path.isabs(sto_cfg) is False:
    sto_cfg = os.path.join(multi_cfg_path_folder, sto_cfg)

ser_cfg = info['cfg_server']
if os.path.isabs(ser_cfg) is False:
    ser_cfg = os.path.join(multi_cfg_path_folder, ser_cfg)

tas_cfg = info['cfg_task']
if os.path.isabs(tas_cfg) is False:
    tas_cfg = os.path.join(multi_cfg_path_folder, tas_cfg)

tra_cfg = info['cfg_task_transfer']
if os.path.isabs(tra_cfg) is False:
    tra_cfg = os.path.join(multi_cfg_path_folder, tra_cfg)

met_cfg = info['cfg_task_metadata']
if os.path.isabs(met_cfg) is False:
    met_cfg = os.path.join(multi_cfg_path_folder, met_cfg)

tbl_cfgs = info['cfg_metadata']
global_scan_flag = info['global_scan_flag']

# 프로세스 실행을 위한 명령어 생성
import subprocess

# scan_single.py에 --create인수를 주어서
# DB 상에 스키마 및 테이블을 생성하고 종료함
# 이게 가장 먼저 실행되어야
# 다른 프로세스들이 오류없이 metadata 테이블을 만들고
# 내용을 추가할 수 있음

tbl_cfg_0 = os.path.join(multi_cfg_path_folder, tbl_cfgs[0])
cmc = ['python', scan_single_path, '--db_cfg', f'{db_cfg}', '--sto_cfg', f'{sto_cfg}', '--ser_cfg', f'{ser_cfg}', '--tas_cfg', f'{tas_cfg}', '--tra_cfg', f'{tra_cfg}', '--met_cfg', f'{met_cfg}', '--tbl_cfg', f'{tbl_cfg_0}', '--create']
cproc = subprocess.Popen(cmc, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
res = cproc.wait()

if res != 0:
    os.system(" ".join(cmc))

# scan_single.py로 실행할 명령어 생성
commands = {}
for tbl_cfg in tbl_cfgs:
    if os.path.isabs(tbl_cfg) is False:
        tbl_cfg = os.path.join(multi_cfg_path_folder, tbl_cfg)

    cmd = ['python', scan_single_path, '--db_cfg', f'{db_cfg}', '--sto_cfg', f'{sto_cfg}', '--ser_cfg', f'{ser_cfg}', '--tas_cfg', f'{tas_cfg}', '--tra_cfg', f'{tra_cfg}', '--met_cfg', f'{met_cfg}', '--tbl_cfg', f'{tbl_cfg}']
    if global_scan_flag is not None:
        if global_scan_flag is True:
            cmd.append('--enable_scan')
        else:
            cmd.append('--disable_scan')
    name = os.path.splitext(os.path.basename(tbl_cfg))[0]
    commands[name] = cmd

import os 
import psutil

# 실행중인 프로세스가 있을 때 pid_list 로부터 pid를 읽어와서 pid들의 이름정보를 배열로 만듬
try:
    pid_infos = {}
    with open(pid_list_path, 'r') as file:
    # Read the contents of the file
        content = file.read()

    # Convert the string to a list
    pid_list = content.split('\n')
    pid_list = [int(item) for item in pid_list if item]

    for pid in pid_list:
        process = psutil.Process(pid)
        name = process.name()
        pid_infos[name] = pid
except:
    pass

process_info = []
pid_list = []
# Start each command as a separate process
for name, command in commands.items():
    # 위에서 만든 커맨드에서 해당 pid의 이름과 같은 이름을 가진 프로세스를 만드려는 명령어가 있으면 해당 명령어를 실행하지 않음
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
    with open(pid_list_path, 'a') as file:
        # Write each list element to a new line in the file
        for item in pid_list:
            file.write(str(item) + '\n')
else:
    # Open the file in write mode
    with open(pid_list_path, 'w') as file:
    # Write each list element to a new line in the file
        for item in pid_list:
            file.write(str(item) + '\n')
    