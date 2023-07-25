import logging

# 일반적인 logger
def get_logger(logger_name=__name__, log_level=logging.DEBUG, log_file='log.log', log_format='%(asctime)s:%(name)s:%(levelname)s:%(message)s'):
    """
    Write log file
    &
    Print log
    """
    logger = logging.getLogger(logger_name)
    if (logger.hasHandlers()):
        logger.handlers.clear()
    logger.setLevel(log_level)

    formatter = logging.Formatter(log_format)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

# print없이 파일만 작성하는 logger
def get_logger_only_file(logger_name=__name__, log_level=logging.DEBUG, log_file='log.log', log_format='%(asctime)s:%(name)s:%(levelname)s:%(message)s'):
    """
    Only Write log file
    No Print
    """
    logger = logging.getLogger(logger_name)
    if (logger.hasHandlers()):
        logger.handlers.clear()
    logger.setLevel(log_level)

    formatter = logging.Formatter(log_format)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger