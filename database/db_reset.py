"""
!!! (개발목적)
db_cfg에 적혀있는 DB에 존재하는 data, metadata, hardware 스키마에 존재하는 
모든 테이블 및 3개의 스키마를 전부 지우는 코드
"""

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--db_cfg', type=str, required=True)
args = parser.parse_args()

import json

with open(args.db_cfg) as config:
    db_info = json.load(config)

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy.schema import DropSchema, CreateSchema

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
    return create_engine(url_object, echo=True, connect_args={"options": "-c timezone=utc"})

engine = get_engine(db_info)

insp = inspect(engine)

schema_names = ["data", "metadata", "hardware"]
for schema_name in schema_names:
    if insp.has_schema(schema_name):
        Session = sessionmaker(bind=engine)
        with Session() as session:
            session.execute(DropSchema(schema_name, cascade=True))
            session.commit()

schema_names = ["data", "metadata", "hardware"]
for schema_name in schema_names:
    if not insp.has_schema(schema_name):
        Session = sessionmaker(bind=engine)
        with Session() as session:
            session.execute(CreateSchema(schema_name))
            session.commit()