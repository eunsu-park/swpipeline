import os
import signal
import logging
import pytz
import json
import datetime as d
from datetime import datetime
from sqlalchemy import create_engine, update, select, insert, inspect, func

from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy.schema import CreateSchema, DropSchema
from watchdog.events import FileSystemEventHandler
from tqdm import tqdm

import db.config as cfg
from db.log import get_logger
from db.tables import Base, DataMaster, DataInfo, DataStatus, HardwareStorage, MetadataTable

logger = get_logger(__name__, logging.INFO)

def load_config(config_file):
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

    with open(config_file) as config:
        info = json.load(config)
    return info


# File scanner and event handler -----------------------------------------------
class FileHandler(FileSystemEventHandler):
    """
    File system event handler

    Description
    -----------
    This class handles file system events and updates the database accordingly.

    Attributes
    ----------
    engine : sqlalchemy.engine
        Database engine

    Methods
    -------
    on_created(event)
        Handle file/folder creation event
    on_modified(event)
        Handle file/folder modification event
    on_moved(event)
        Handle file/folder move event
    on_deleted(event)
        Handle file/folder deletion event
    """

    def __init__(self, engine):
        self.engine = engine
        self.data_infos = cfg.tbl_info['table_info']['data_info']

    def on_created(self, event):
        if not event.is_directory:
            for data_info in self.data_infos:
                if data_info['data_path'] in event.src_path:
                    logger.info(f"Detect: {event.event_type} {event.src_path}")
                    isok = insert_file_info(self.engine, event.src_path, data_info)
                    if isok: 
                        logger.info(f"Commit: {event.event_type} {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            logger.info(f"Detect: {event.event_type} {event.src_path}")
            isok = True
            result = update_modified_file_info(self.engine, event.src_path)
            if result == None:
                for data_info in self.data_infos:
                    if data_info['data_path'] in event.src_path:
                        isok = isok and insert_file_info(self.engine, event.src_path, data_info)
            isok = isok and result
            if isok:
                logger.info(f"Commit: {event.event_type} {event.src_path}")

    def on_moved(self, event):
        if not event.is_directory:
            for data_info in self.data_infos:
                if data_info['data_path'] in event.src_path:
                    logger.info(f"Detect: {event.event_type} {event.src_path} {event.dest_path}")
                    isok = update_moved_file_info(self.engine, event.src_path, event.dest_path, data_info)
                    if isok:
                        logger.info(f"Commit: {event.event_type} {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"Detect: {event.event_type} {event.src_path}")
            isok = delete_file_info(self.engine, event.src_path)
            if isok:
                logger.info(f"Commit: {event.event_type} {event.src_path}")


class FileScanner:
    """ 
    File scanner 

    Description
    -----------
    This class scans a directory and adds all files and folders to the database.

    Attributes
    ----------
    engine : sqlalchemy.engine
        Database engine

    Methods
    -------
    scan_files(directory)
        Scan a directory and add all files and folders to the database
    """

    def __init__(self, engine):
        self.engine = engine

    def scan_files(self):
        delete_missing_files(self.engine)
        data_infos = cfg.tbl_info['table_info']['data_info']
        for data_info in data_infos:
            watching_path = data_info['data_path']
            file_count = sum(len(files) for _, _, files in os.walk(watching_path))
            with tqdm(total=file_count) as pbar:
                pbar.set_description(f"Scanning Files: [{data_info['data_group']}]")
                for root, dirs, files in os.walk(watching_path):
                    # add_folder_info(self.engine, root)
                    # for dirname in sorted(dirs):
                    #     folderpath = os.path.join(root, dirname)
                    #     add_folder_info(self.engine, folderpath)
                    for filename in files:
                        filepath = os.path.join(root, filename)
                        add_file_info(self.engine, filepath, data_info)
                        pbar.update(1)

    def update_files(self):
        delete_missing_files(self.engine)
        Session = sessionmaker(bind=self.engine)
        with Session() as session:
            result = session.execute(
                func.max(MetadataTable.file_modified_time)
            )
            r = next(result)
            max_date = r[0]
            if max_date == None:
                logger.error("Scan Could Not Be Completed")
                return None
            
            data_infos = cfg.tbl_info['table_info']['data_info']
            for data_info in data_infos:
                watching_path = data_info['data_path']
                file_count = sum(len(files) for _, _, files in os.walk(watching_path))
                with tqdm(total=file_count, disable=False) as pbar:
                    pbar.set_description(f"Check Modified/Created Files: [{data_info['data_group']}]")
                    for root, _, files in os.walk(watching_path):
                        # add_folder_info(self.engine, root)
                        # for dirname in sorted(dirs):
                        #     folderpath = os.path.join(root, dirname)
                        #     add_folder_info(self.engine, folderpath)
                        for filename in files:
                            filepath = os.path.join(root, filename)
                            _, mtime = get_stats_from_filepath(filepath)
                            pbar.update(1)
                            if mtime > max_date:
                                add_file_info(self.engine, filepath, data_info)
                                # logger.info(f'DB updated: {filepath}')
            return True
                
            #  file_infos = session.execute(
            #         select(MetadataTable)
            #     ).scalars().all()
                

            # for dirname in dirs:
            #     folderpath = os.path.join(root, dirname)
            #     add_folder_info(self.engine, folderpath)
            # for filename in files:
            #     filepath = os.path.join(root, filename)
            #     add_file_info(self.engine, filepath, self.info)


# create engine ------------------------------------------------
def get_engine(info):
    """ 
    Create database engine

    Parameters
    ----------
    info : dict
        Dictionary containing database information which is loaded from a json

    Returns
    ----------
    engine : sqlalchemy.engine
        Database engine
    """

    url_info = info['database']['url']
    engine_info = info['database']['engine']

    # Create engine
    url_object = URL.create(
        drivername=url_info['drivername'],
        username=url_info['username'],
        password=url_info['password'],
        host=url_info['host'],
        port=url_info['port'],
        database=url_info['database']
    )
    # return create_engine(url_object, echo=engine_info['echo'])
    return create_engine(url_object, echo=engine_info['echo'], connect_args={"options": "-c timezone=utc"})


# Create & Delete schema ------------------------------------------------
def create_schema(engine):
    """
    Create schema

    Parameters
    ----------
    engine : sqlalchemy.engine
        Database engine
    """
    insp = inspect(engine)

    schema_names = ["data", "metadata", "hardware"]
    for schema_name in schema_names:
        if not insp.has_schema(schema_name):
            Session = sessionmaker(bind=engine)
            with Session() as session:
                logger.info(CreateSchema(schema_name))
                session.execute(CreateSchema(schema_name))
                session.commit()


def delete_schema(engine):
    insp = inspect(engine)

    schema_names = ["data", "metadata", "hardware"]
    for schema_name in schema_names:
        if insp.has_schema(schema_name):
            Session = sessionmaker(bind=engine)
            with Session() as session:
                session.execute(DropSchema(schema_name))
                session.commit()

# Create & Delete tables ----------------------------------------------------------------
def create_tables(engine):
    """
    Create tables

    Parameters
    ----------
    engine : sqlalchemy.engine
        Database engine
    """
    Base.metadata.create_all(engine)

def delete_tables(engine):
    """
    Delete tables

    Parameters
    ----------
    engine : sqlalchemy.engine
        Database engine
    """
    Base.metadata.drop_all(engine)
    # FileInfo.__table__.drop(bind=engine, checkfirst=True)
    # FolderInfo.__table__.drop(bind=engine, checkfirst=True)

# Data Info ---------------------------------------------------------------------------------
def insert_and_update_data_info(engine):
    """
    Add data info into database

    Parameters
    ----------
    engine : sqlalchemy.engine
        Database engine
    """

    Session = sessionmaker(bind=engine)
    with Session() as session:
        data_infos = cfg.tbl_info['table_info']['data_info']
        storage_infos = cfg.storage_info['storage_info']

        for storage_info in storage_infos:
            storage_id = storage_info['storage_id']

            storage_name = storage_info['storage_name']
            volume_name = storage_info['volume_name']
            ip = storage_info['ip']
            hostname = storage_info['hostname']
            comment = storage_info['comment']
            
            storage_id_exists = session.execute(
                                    select(HardwareStorage)
                                    .where(HardwareStorage.storage_id == storage_id)
                                ).scalar_one_or_none()
                    
            if storage_id_exists == None:
                session.execute(
                    insert(HardwareStorage)
                    .values(
                        storage_id = storage_id,
                        storage_name = storage_name,
                        volume_name = volume_name,
                        ip = ip,
                        hostname = hostname,
                        comment = comment,
                    )
                )

                session.commit()
            else:
                session.execute(
                    update(HardwareStorage)
                    .where(HardwareStorage.storage_id == storage_id)
                    .values(
                        storage_name = storage_name,
                        volume_name = volume_name,
                        ip = ip,
                        hostname = hostname,
                        comment = comment,
                    )
                )

                session.commit()

        for data_info in data_infos:
            data_group = data_info['data_group']
            member_infos = data_info['member_info']
            pbar = tqdm(member_infos, disable=False)
            for member_info in pbar:
                pbar.set_description(f"Insert & Update Data Info: [{data_group}]")
                data_id = member_info['data_id']
                storage_id = member_info['storage_id']
                data_status_id = data_id + '_' + storage_id
                
                institute = member_info['institute']
                observatory = member_info['observatory']
                satellite = member_info['satellite']
                model = member_info['model']
                telescope = member_info['telescope']
                wavelength = member_info['wavelength']
                channel = member_info['channel']
                instrument = member_info['instrument']
                storage_info = next(d for i,d in enumerate(storage_infos) if d['storage_id'] == storage_id)
                storage_name = storage_info['storage_name']
                volume_name = storage_info['volume_name']
                ip = storage_info['ip']
                hostname = storage_info['hostname']
                comment = storage_info['comment']

                file_server = member_info['file_server']

                data_id_exists = session.execute(
                                    select(DataMaster)
                                    .where(DataMaster.data_id == data_id)
                                ).scalar_one_or_none()

                if data_id_exists == None:
                    session.execute(
                        insert(DataMaster)
                        .values(
                            data_id = data_id,
                            data_group = data_group,
                        )
                    )

                    session.execute(
                        insert(DataInfo)
                        .values(
                            data_id = data_id,
                            institute = institute,
                            observatory = observatory,
                            satellite = satellite,
                            model = model,
                            telescope = telescope,
                            wavelength = wavelength,
                            channel = channel,
                            instrument = instrument,
                        )
                    )

                    session.flush()
                else:
                    session.execute(
                        update(DataMaster)
                        .where(DataMaster.data_id == data_id)
                        .values(
                            data_group = data_group,
                        )
                    )

                    session.execute(
                        update(DataInfo)
                        .where(DataInfo.data_id == data_id)
                        .values(
                            institute = institute,
                            observatory = observatory,
                            satellite = satellite,
                            model = model,
                            telescope = telescope,
                            wavelength = wavelength,
                            channel = channel,
                            instrument = instrument,
                        )
                    )

                    session.flush()

                storage_id_exists = session.execute(
                                    select(HardwareStorage)
                                    .where(HardwareStorage.storage_id == storage_id)
                                ).scalar_one_or_none()
                    
                if storage_id_exists == None:
                    session.execute(
                        insert(HardwareStorage)
                        .values(
                            storage_id = storage_id,
                            storage_name = storage_name,
                            volume_name = volume_name,
                            ip = ip,
                            hostname = hostname,
                            comment = comment,
                        )
                    )

                    session.flush()
                else:
                    session.execute(
                        update(HardwareStorage)
                        .where(HardwareStorage.storage_id == storage_id)
                        .values(
                            storage_name = storage_name,
                            volume_name = volume_name,
                            ip = ip,
                            hostname = hostname,
                            comment = comment,
                        )
                    )

                    session.flush()
                
                data_status_id_exists = session.execute(
                                    select(DataStatus)
                                    .where(DataStatus.data_status_id == data_status_id)
                                ).scalar_one_or_none()
                
                if data_status_id_exists == None:
                    session.execute(
                        insert(DataStatus)
                        .values(
                            data_status_id = data_status_id,
                            storage_id = storage_id,
                            file_server = file_server,
                            data_id = data_id
                        )
                    )

                    session.flush()
                else:
                    session.execute(
                        update(DataStatus)
                        .where(DataStatus.data_status_id == data_status_id)
                        .values(
                            storage_id = storage_id,
                            file_server = file_server,
                            data_id = data_id
                        )
                    )

                    session.flush()
        
        session.commit()

# File -----------------------------------------------------------------------------------
def add_file_info(engine, filepath, data_info):
    """
    Add file info into database

    Parameters
    ----------
    engine : sqlalchemy.engine
        Database engine
    filepath : str
        Path to file
    """
    filepath = os.path.abspath(filepath)

    Session = sessionmaker(bind=engine)
    with Session() as session:
        file_info = session.execute(
                        select(MetadataTable)
                        .where(MetadataTable.file_path == filepath)
                    ).scalar_one_or_none()
        if file_info == None:
            isok = insert_file_info(engine, filepath, data_info)
            #if isok: 
            #    logger.info(f"DB Insert: {filepath}")
            return
        else:
            isok = update_modified_file_info(engine, filepath)
            #if isok: 
            #    logger.info(f"DB Update: {filepath}")
            return  # Record already exists

def delete_missing_files(engine):
    """
    Delete missing files

    Parameters
    ----------
    engine : sqlalchemy.engine
        Database engine
    """
    data_ids = []
    for data_info in cfg.tbl_info['table_info']['data_info']:
        member_infos = data_info['member_info']
        for member_info in member_infos:
            data_id = member_info['data_id']
            data_ids.append(data_id)
    table_name = cfg.tbl_info['table_info']['table_name']
    Session = sessionmaker(bind=engine)
    with Session() as session:
        file_infos = session.execute(
                        select(MetadataTable)
                    ).scalars().all()
        if file_infos:
            pbar = tqdm(file_infos)
            for file_info in pbar:
                pbar.set_description(f"Check deleted files [{table_name}]")    
                if not file_info.data_id in data_ids:
                    delete_file_info(engine, file_info.file_path)
                    logger.info(f'DB Deleted: {file_info.file_path}')
                if not os.path.exists(file_info.file_path):
                    delete_file_info(engine, file_info.file_path)
                    # session.delete(file_info)
                    # session.commit()
                    logger.info(f'DB Deleted: {file_info.file_path}')
                
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

def insert_file_info(engine, file_path, data_info):
    """
    Insert file info into database

    Parameters
    ----------
    engine : sqlalchemy.engine
        Database engine
    file_path : str
        Path to file
    info : dict
        Dictionary containing configuration information
    """

    Session = sessionmaker(bind=engine)
    with Session() as session:
        member_infos = data_info['member_info']
        for member_info in member_infos:
            fileformats = member_info['file_format']
            data_id = member_info['data_id']
            storage_id = member_info['storage_id']
            data_status_id = data_id + '_' + storage_id
            for fileformat in fileformats:
                file_name, file_extension, file_time = get_infos_from_filepath(file_path, fileformat)
                if file_name == None:
                    continue
                file_size, mtime = get_stats_from_filepath(file_path)

                old_status = session.execute(
                                            select(DataStatus)
                                            .where(DataStatus.data_status_id == data_status_id)
                                            ).scalar_one_or_none()
                
                if old_status.start_time == None:
                    session.execute(
                                    update(DataStatus)
                                    .where(DataStatus.data_status_id == data_status_id)
                                    .values(start_time = file_time.date())
                                    )
                elif file_time.date() < old_status.start_time:
                    session.execute(
                                    update(DataStatus)
                                    .where(DataStatus.data_status_id == data_status_id)
                                    .values(start_time = file_time.date())
                                    )

                if old_status.end_time == None:
                    session.execute(
                                    update(DataStatus)
                                    .where(DataStatus.data_status_id == data_status_id)
                                    .values(end_time = file_time.date())
                                    )
                elif file_time.date() > old_status.end_time:
                    session.execute(
                                    update(DataStatus)
                                    .where(DataStatus.data_status_id == data_status_id)
                                    .values(end_time = file_time.date())
                                    )
                    
                session.execute(
                    insert(MetadataTable)
                    .values(
                        file_name = file_name,
                        file_time = file_time,
                        data_id = data_id,
                        data_status_id = data_status_id,
                        file_extension = file_extension,
                        file_path = file_path,
                        file_size = file_size,
                        # file_created_time = ctime,
                        file_modified_time = mtime
                    )
                )
                session.commit()

            if file_name == None:
                continue
    return True
        

def update_modified_file_info(engine, file_path):
    """
    Update modified file info in database

    Parameters
    ----------
    engine : sqlalchemy.engine
        Database engine
    filepath : str
        Path to file
    """
    Session = sessionmaker(bind=engine)
    with Session() as session:
            file_info = session.execute(
                                        select(MetadataTable)
                                        .where(MetadataTable.file_path == file_path)
                                        ).scalar_one_or_none()
            
            if file_info == None:
                logger.error(f"Can Not Update Info {file_path}")
                logger.error("Scan Could Not Be Completed")
                return None

            file_size, mtime = get_stats_from_filepath(file_path)

            is_changed = int(file_info.file_size) != int(file_size)
            # is_created = file_info.file_created_time != ctime
            is_modified = file_info.file_modified_time != mtime
            if is_changed or is_modified:
                session.execute(
                    update(MetadataTable)
                    .where(MetadataTable.file_path == file_path)
                    .values(
                        file_size = file_size,
                        # file_created_time = ctime,
                        file_modified_time = mtime
                    )
                )
                session.commit()
                # logger.info(f'DB Updated: {file_path}')

    return True


def update_moved_file_info(engine, src_path, dest_path, data_info):
    """
    Update moved file info in database

    Parameters
    ----------
    engine : sqlalchemy.engine
        Database engine
    src_path : str
        Path to source file
    dest_path : str
        Path to destination file
    """
    src_path = os.path.abspath(src_path)
    dest_path = os.path.abspath(dest_path)

    Session = sessionmaker(bind=engine)
    with Session() as session:
        member_infos = data_info['member_info']

        for member_info in member_infos:
            fileformats = member_info['file_format']
            data_id = member_info['data_id']
            storage_id = member_info['storage_id']
            data_status_id = data_id + '_' + storage_id
            for fileformat in fileformats:
                file_name, file_extension, file_time = get_infos_from_filepath(dest_path, fileformat)
                if file_name == None:
                    continue
                file_size, mtime = get_stats_from_filepath(dest_path)

                old_status = session.execute(
                                            select(DataStatus)
                                            .where(DataStatus.data_status_id == data_status_id)
                                            ).scalar_one_or_none()
                
                if old_status.start_time == None:
                    session.execute(
                                    update(DataStatus)
                                    .where(DataStatus.data_status_id == data_status_id)
                                    .values(start_time = file_time.date())
                                    )
                elif file_time.date() < old_status.start_time:
                    session.execute(
                                    update(DataStatus)
                                    .where(DataStatus.data_status_id == data_status_id)
                                    .values(start_time = file_time.date())
                                    )

                if old_status.end_time == None:
                    session.execute(
                                    update(DataStatus)
                                    .where(DataStatus.data_status_id == data_status_id)
                                    .values(end_time = file_time.date())
                                    )
                elif file_time.date() > old_status.end_time:
                    session.execute(
                                    update(DataStatus)
                                    .where(DataStatus.data_status_id == data_status_id)
                                    .values(end_time = file_time.date())
                                    )
                    
                session.execute(
                    update(MetadataTable)
                    .where(MetadataTable.file_path == src_path)
                    .values(
                        file_name = file_name,
                        file_time = file_time,
                        data_id = data_id,
                        data_status_id = data_status_id,
                        file_extension = file_extension,
                        file_path = dest_path,
                        file_size = file_size,
                        # file_created_time = ctime,
                        file_modified_time = mtime
                    )
                )
                session.commit()
                # logger.info(f'DB updated: {dest_path}')
            if file_name == None:
                continue
    return True

def delete_file_info(engine, filepath):
    """
    Delete file info from database

    Parameters
    ----------
    engine : sqlalchemy.engine
        Database engine
    filepath : str
        Path to file
    """
    filepath = os.path.abspath(filepath)

    Session = sessionmaker(bind=engine)
    with Session() as session:
        session = Session()
        file_info = session.execute(
                        select(MetadataTable)
                        .where(MetadataTable.file_path == filepath)
                    ).scalar_one_or_none()
        if file_info == None:
            return  True # Record does not exist
        else:
            session.delete(file_info)
            session.commit()
            # logger.info(f'DB deleted: {filepath}')
            return True