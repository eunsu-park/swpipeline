"""
json config 파일을 불러옴

global variable 통해 라이브러리 모든곳에서 설정파일 접근가능 하도록
하기 위해 존재하는 코드
"""

import json


def load_tbl_config(tbl_config_file):
    """
    Load config file

    Parameters
    ----------
    config_file : str
        Path to json config file

    Returns
    ----------
    info : dict
        Dictionary containing database information
    """
    global tbl_info

    with open(tbl_config_file) as config:
        tbl_info = json.load(config)
    return tbl_info

def load_storage_config(storage_config_file):
    """
    Load config file

    Parameters
    ----------
    config_file : str
        Path to json config file

    Returns
    ----------
    info : dict
        Dictionary containing database information
    """
    global storage_info

    with open(storage_config_file) as config:
        storage_info = json.load(config)
    return storage_info

def load_server_config(config_file):
    global server_info
    with open(config_file) as config:
        server_info = json.load(config)
    return server_info

def load_task_config(config_file):
    global task_info
    with open(config_file) as config:
        task_info = json.load(config)
    return task_info

def load_task_transfer_config(config_file):
    global task_transfer_info
    with open(config_file) as config:
        task_transfer_info = json.load(config)
    return task_transfer_info

def load_task_metadata_config(config_file):
    global task_metadata_info
    with open(config_file) as config:
        task_metadata_info = json.load(config)
    return task_metadata_info