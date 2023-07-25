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