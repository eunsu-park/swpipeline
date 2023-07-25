import argparse
import logging

# from db.log import get_logger, get_logger_only_file
# logger = get_logger("db.utils", logging.INFO)
# get_logger_only_file("sqlalchemy.engine", logging.WARN)

parser = argparse.ArgumentParser()
parser.add_argument('--db_cfg', type=str, required=True)
parser.add_argument('--sto_cfg', type=str, required=True)
parser.add_argument('--tbl_cfg', type=str, required=True)
parser.add_argument('--create', type=str, default=False, required=False)
args = parser.parse_args()

import os
import setproctitle

setproctitle.setproctitle(f"{os.path.splitext(os.path.basename(args.tbl_cfg))[0]}")

import db.config as cfg
cfg.load_tbl_config(args.tbl_cfg)
cfg.load_storage_config(args.sto_cfg)

import db.utils as utils
db_info = utils.load_config(args.db_cfg)
engine = utils.get_engine(db_info)

if args.create:
    utils.create_schema(engine)
    utils.create_tables(engine)
    exit(0)

utils.create_schema(engine)
utils.create_tables(engine)
utils.insert_and_update_data_info(engine)

scanner = utils.FileScanner(engine)
scan_flag = cfg.tbl_info['table_info']['scan_flag']
if scan_flag == True:
    scanner.scan_files()
else:
    result = scanner.update_files()
    if result == None:
        exit(1)

observer_flag = cfg.tbl_info['table_info']['observer_flag']
if observer_flag:
    import time
    from watchdog.observers import polling

    event_handler = utils.FileHandler(engine)
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