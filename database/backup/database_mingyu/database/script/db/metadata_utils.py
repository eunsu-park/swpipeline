import os
import datetime as d
from datetime import datetime

def get_infos_from_filepath(file_path, fileformat):
    """
    Get file stats

    Parameters
    ----------
    file_path : str
        Path to file

    Returns
    ----------
    filename : str 
        File name
    fileextension : str
        File extension
    filefolderpath : str
        Parent folder path which contains the file
    mtime : str
        File modification time
    """
    _, extension = os.path.splitext(fileformat)
    file_path = os.path.abspath(file_path)
    basename = os.path.basename(file_path)

    try:
        file_time = datetime.strptime(basename, fileformat).replace(tzinfo=d.timezone.utc)
        # file_time = file_time.date()
    except ValueError:
        return None, None, None 
    
    file_name, file_extension = os.path.splitext(basename)
    if file_extension == extension:
        file_extension = file_extension.replace('.', '')
    else:
        return None, None, None
    
    return file_name, file_extension, file_time
    
def get_stats_from_filepath(file_path):

    file_path = os.path.abspath(file_path)
    basename = os.path.basename(file_path)

    stat_info = os.stat(file_path)
    # ctime = stat_info.st_ctime
    mtime = datetime.astimezone(datetime.fromtimestamp(stat_info.st_mtime), tz=d.timezone.utc)
    # mtime = datetime.fromtimestamp(stat_info.st_mtime).replace(tzinfo=pytz.timezone('Asia/Seoul'))
    # ctime, mtime = [datetime.astimezone(datetime.fromtimestamp(dt), tz=d.timezone.utc) for dt in [ctime, mtime]]

    file_size = stat_info.st_size
    # a = ctime.astimezone(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    # print(a)
    return file_size, mtime