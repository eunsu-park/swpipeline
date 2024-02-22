"""
DB 모듈 메인 코드
"""

import argparse

# from db.log import get_logger, get_logger_only_file
# logger = get_logger("db.utils", logging.INFO)
# get_logger_only_file("sqlalchemy.engine", logging.WARN)

parser = argparse.ArgumentParser()
parser.add_argument('--db_cfg', type=str, required=True)
parser.add_argument('--sto_cfg', type=str, required=True)
parser.add_argument('--ser_cfg', type=str, required=True)
parser.add_argument('--tas_cfg', type=str, required=True)
parser.add_argument('--tra_cfg', type=str, required=True)
parser.add_argument('--met_cfg', type=str, required=True)
parser.add_argument('--tbl_cfg', type=str, required=True)
parser.add_argument('--create', action='store_true')
parser.set_defaults(create=False)
parser.add_argument('--enable_scan', dest='global_scan', action='store_true')
parser.add_argument('--disable_scan', dest='global_scan', action='store_false')
parser.set_defaults(global_scan=None)
args = parser.parse_args()

import os
import setproctitle
# 프로세스 이름 변경
setproctitle.setproctitle(f"{os.path.splitext(os.path.basename(args.tbl_cfg))[0]}")

# global 설정 variable 생성
import db.config as cfg
cfg.load_tbl_config(args.tbl_cfg)
cfg.load_storage_config(args.sto_cfg)
cfg.load_server_config(args.ser_cfg)
cfg.load_task_config(args.tas_cfg)
cfg.load_task_transfer_config(args.tra_cfg)
cfg.load_task_metadata_config(args.met_cfg)

# DB 접속 엔진 생성
import db.db_utils as db_utils
db_info = db_utils.load_config(args.db_cfg)
engine = db_utils.get_engine(db_info)

# 혹시 --create가 인수로 주어졌을 때
# DB 상에 스키마 및 테이블을 생성하고 종료함
# 이게 가장 먼저 실행되어야
# 다른 프로세스들이 오류없이 metadata 테이블을 만들고
# 내용을 추가할 수 있음
if args.create == True:
    db_utils.create_schema(engine)
    db_utils.create_tables(engine)
    db_utils.insert_and_update_data_info(engine)
    exit(0)

db_utils.create_schema(engine)
db_utils.create_tables(engine)
db_utils.insert_and_update_data_info(engine)

scanner = db_utils.FileScanner(engine)
scan_flag = cfg.tbl_info['table_info']['scan_flag']
check_change_flag = cfg.tbl_info['table_info']['check_change_flag']
if args.global_scan is not None:
    scan_flag = args.global_scan
if scan_flag == True:
    scanner.scan_files()
elif check_change_flag == True:
    result = scanner.update_files()
    if result == None:
        exit(1)

observer_flag = cfg.tbl_info['table_info']['observer_flag']
if observer_flag:
    import time
    from watchdog.observers import polling

    event_handler = db_utils.FileHandler(engine)
    observer = polling.PollingObserver()

    data_infos = cfg.tbl_info['table_info']['data_info']
    for data_info in data_infos:
        watching_path = data_info['data_path']
        observer.schedule(event_handler, path=watching_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()