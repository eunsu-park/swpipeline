from sqlalchemy import Table, Column, BigInteger, String, DateTime, ForeignKey, MetaData, VARCHAR, CHAR, SmallInteger, Numeric, DATE
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
    medadata_table = relationship("MetadataTable", back_populates="data_status", cascade='all, delete-orphan')
    hardware_storage = relationship('HardwareStorage', back_populates='data_status')

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

    data_status = relationship('DataStatus', back_populates='hardware_storage')

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
