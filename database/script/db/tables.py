from sqlalchemy import Table, Column, BigInteger, String, DateTime, ForeignKey, MetaData, VARCHAR, CHAR, SmallInteger, Numeric, DATE, Boolean
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import DeclarativeBase, relationship

from datetime import datetime
import db.config as cfg

class Base(DeclarativeBase):
    pass

# data.data_master 테이블 정의
class DataMaster(Base):
    __tablename__ = 'data_master'
    __bind_key__ = 'data'
    __table_args__ = {'schema': 'data'}
    
    data_id = Column(TEXT, primary_key=True, nullable=False)
    data_group = Column(TEXT)
    record_created_time = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    record_modified_time = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    data_info = relationship("DataInfo", back_populates="data_master", cascade='all, delete-orphan')
    data_status = relationship("DataStatus", back_populates="data_master", cascade='all, delete-orphan')
    task_table = relationship('Task', back_populates='data_master', cascade='all, delete-orphan')


# data.data_info 테이블 정의
class DataInfo(Base):
    __tablename__ = "data_info"
    __bind_key__ = 'data'
    __table_args__ = {'schema': 'data'}

    data_id = Column(TEXT, ForeignKey('data.data_master.data_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    institute = Column(TEXT)
    observatory = Column(TEXT)
    satellite = Column(TEXT)
    model = Column(TEXT)
    telescope = Column(TEXT)
    wavelength = Column(TEXT)
    channel = Column(TEXT)
    instrument = Column(TEXT)
    record_created_time = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    record_modified_time = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    data_master = relationship('DataMaster', back_populates='data_info')
    medadata_table = relationship("MetadataTable", back_populates="data_info", cascade='all, delete-orphan')

# data.data_status 테이블 정의
class DataStatus(Base):
    __tablename__ = "data_status"
    __bind_key__ = 'data'
    __table_args__ = {'schema': 'data'}
    
    data_status_id = Column(TEXT, primary_key=True, nullable=False)
    start_time = Column(DATE)
    end_time = Column(DATE)
    storage_id = Column(TEXT, ForeignKey('hardware.hardware_storage.storage_id', ondelete='CASCADE'), nullable=False)
    file_server = Column(SmallInteger)
    data_id = Column(TEXT, ForeignKey('data.data_master.data_id', ondelete='CASCADE'), nullable=False)
    record_created_time = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    record_modified_time = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    data_master = relationship('DataMaster', back_populates='data_status')
    hardware_storage = relationship('HardwareStorage', back_populates='data_status')
    medadata_table = relationship("MetadataTable", back_populates="data_status", cascade='all, delete-orphan')


# hardware.hardware_storage 테이블 정의
class HardwareStorage(Base):
    __tablename__ = "hardware_storage"
    __bind_key__ = 'hardware'
    __table_args__ = {'schema': 'hardware'}
    
    storage_id = Column(TEXT, primary_key=True)
    storage_name = Column(TEXT)
    volume_name = Column(TEXT)
    ip = Column(TEXT)
    hostname = Column(TEXT)
    comment = Column(TEXT)
    record_created_time = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    record_modified_time = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    data_status = relationship('DataStatus', back_populates='hardware_storage', cascade='all, delete-orphan')

# hardware.hardware_server 테이블 정의
class HardwareServer(Base):
    __tablename__ = "hardware_server"
    __bind_key__ = 'hardware'
    __table_args__ = {'schema': 'hardware'}
    
    server_id = Column(TEXT, primary_key=True)
    ip = Column(TEXT)
    hostname = Column(TEXT)
    detail = Column(TEXT)
    record_created_time = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    record_modified_time = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    task_table = relationship('Task', back_populates='hardware_server', cascade='all, delete-orphan')

# task.task 테이블 정의
class Task(Base):
    __tablename__ = "task"
    __bind_key__ = 'task'
    __table_args__ = {'schema': 'task'}

    task_id = Column(TEXT, primary_key=True)
    data_id = Column(TEXT, ForeignKey('data.data_master.data_id', ondelete='CASCADE'), nullable=False)
    task_type = Column(TEXT)
    enable = Column(Boolean)
    created = Column(DateTime(timezone=True))
    updated = Column(DateTime(timezone=True))
    program = Column(TEXT)
    server_id = Column(TEXT, ForeignKey('hardware.hardware_server.server_id', ondelete='CASCADE'), nullable=False)
    record_created_time = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    record_modified_time = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    data_master = relationship('DataMaster', back_populates='task_table')
    hardware_server = relationship('HardwareServer', back_populates='task_table')
    task_metadata = relationship('TaskMetadata', back_populates='task_table', cascade='all, delete-orphan')
    task_transfer = relationship('TaskTransfer', back_populates='task_table', cascade='all, delete-orphan')

# task.task_metadata 테이블 정의
class TaskMetadata(Base):
    __tablename__ = "task_metadata"
    __bind_key__ = 'task'
    __table_args__ = {'schema': 'task'}

    task_id = Column(TEXT, ForeignKey('task.task.task_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    scan_type = Column(TEXT)
    scan_path = Column(TEXT)
    record_created_time = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    record_modified_time = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    task_table = relationship('Task', back_populates='task_metadata')

# task.task_transfer 테이블 정의
class TaskTransfer(Base):
    __tablename__ = "task_transfer"
    __bind_key__ = 'task'
    __table_args__ = {'schema': 'task'}

    task_id = Column(TEXT, ForeignKey('task.task.task_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    transfer_type = Column(TEXT)
    protocol = Column(TEXT)
    src_path = Column(TEXT)
    dst_path = Column(TEXT)
    schedule_type = Column(TEXT)
    schedule_time = Column(TEXT)
    record_created_time = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    record_modified_time = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    task_table = relationship('Task', back_populates='task_transfer')

# metadata 테이블 정의 -> 설정파일에서 변경가능
# watch하는 디렉토리에 따라 테이블 이름 다름
class MetadataTable(Base):
    tablename = cfg.tbl_info['table_info']['table_name']
    __tablename__ = tablename
    __bind_key__ = 'metadata'
    __table_args__ = {'schema': 'metadata'}

    file_id = Column(BigInteger, primary_key=True)
    file_name = Column(TEXT, nullable=False)
    file_time = Column(DateTime(timezone=True), nullable=False)
    data_id = Column(TEXT, ForeignKey('data.data_info.data_id', ondelete='CASCADE'), nullable=False)
    data_status_id = Column(TEXT, ForeignKey('data.data_status.data_status_id', ondelete='CASCADE'), nullable=False)
    file_extension = Column(TEXT)
    file_path = Column(TEXT, nullable=False, unique=True)
    file_size = Column(Numeric)
    file_created_time = Column(DateTime(timezone=True), nullable=True)
    file_modified_time = Column(DateTime(timezone=True), nullable=False)
    record_created_time = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    record_modified_time = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    data_info = relationship('DataInfo', back_populates='medadata_table', single_parent=True)
    data_status = relationship('DataStatus', back_populates='medadata_table', single_parent=True)
