import time
import threading

from sqlalchemy import and_

from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql:///trongty', echo=False)
Base = declarative_base()
from sqlalchemy import Boolean, Column, Integer, String, LargeBinary, ForeignKey, REAL, Numeric, DateTime, DECIMAL, \
    BIGINT
from source import Base
import json


class Credential(Base):
    __tablename__ = 'credential'
    id = Column(Integer, primary_key=True)
    json_credential = Column(String, nullable=False)
    email = Column(String, nullable=False)
    last_used_timestamp = Column(Integer, default=0)
    used_times = Column(Integer, default=0)

    def __repr__(self):
        return '<Id: {}>'.format(self.id)

    def to_json(self):
        return {
            'id': self.id,
            'json_credential': json.loads(self.json_credential),
            'email': self.email,
            'last_used_time': self.last_used_timestamp,
            'used_times': self.used_times
        }


Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
session.commit()


class BackgroundWorker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    @staticmethod
    def restart_credential():
        cre_record = session.query(Credential).filter(
            and_(
                Credential.used_times >= 8,
                int(time.time()) - Credential.last_used_timestamp > 24 * 60 * 60
            )
        ).all()
        for cre in cre_record:
            cre.last_used_time = 0
            cre.used_times = 0
            session.commit()

    def run(self):
        while True:
            self.restart_credential()
            print('Background service start normally')
            time.sleep(1)


b_worker = BackgroundWorker()
b_worker.start()
