import logging
# from logging.handlers import TimedRotatingFileHandler
from db.mpfhandler import MultProcTimedRotatingFileHandler

import os
from pathlib import Path

# 일반적인 logger
def get_logger(logger_name=__name__, log_level=logging.DEBUG, log_file='log.log', log_format='%(asctime)s:%(name)s:%(levelname)s:%(message)s'):
    """
    Write log file
    &
    Print log
    """

    # 로그 저장 경로
    current_dir = os.path.dirname(os.path.realpath(__file__))
    path = Path(current_dir)
    parent = path.parent.absolute().parent.absolute().parent.absolute()
    log_dir = '{}/logs'.format(str(parent))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_path = os.path.join(log_dir, log_file)

    # 로거 생성
    logger = logging.getLogger(logger_name)
    if (logger.hasHandlers()):
        logger.handlers.clear()
    logger.setLevel(log_level)

    formatter = logging.Formatter(log_format)

    # file_handler = logging.FileHandler(log_file)
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    timedfilehandler = MultProcTimedRotatingFileHandler(filename=log_path, when='midnight', interval=1, encoding='utf-8')
    timedfilehandler.setFormatter(formatter)
    timedfilehandler.suffix = "%Y%m%d"
    logger.addHandler(timedfilehandler)
    return logger

# # print없이 파일만 작성하는 logger
# def get_logger_only_file(logger_name=__name__, log_level=logging.DEBUG, log_file='log.log', log_format='%(asctime)s:%(name)s:%(levelname)s:%(message)s'):
#     """
#     Only Write log file
#     No Print
#     """
#     logger = logging.getLogger(logger_name)
#     if (logger.hasHandlers()):
#         logger.handlers.clear()
#     logger.setLevel(log_level)

#     formatter = logging.Formatter(log_format)
#     file_handler = logging.FileHandler(log_file)
#     file_handler.setFormatter(formatter)

#     logger.addHandler(file_handler)
#     return logger


