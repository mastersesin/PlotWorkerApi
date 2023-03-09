from sqlalchemy import Boolean, Column, Integer, String, LargeBinary, ForeignKey, REAL, Numeric, DateTime, DECIMAL, \
    BIGINT
from source import Base
import json


class Credential(Base):
    __tablename__ = 'credential'
    id = Column(Integer, primary_key=True)
    rclone_token = Column(String, nullable=False)
    client_id = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)
    last_used_timestamp = Column(Integer, default=0)
    used_times = Column(Integer, default=0)

    def __repr__(self):
        return '<Id: {}>'.format(self.id)

    def to_json(self):
        return {
            'id': self.id,
            'json_credential': json.loads(self.json_credential),
            'last_used_time': self.last_used_timestamp,
            'used_times': self.used_times
        }


class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    ip = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    timestamp = Column(Integer)

    def __repr__(self):
        return '<Id: {}>'.format(self.id)

    def to_json(self):
        return {
            'id': self.id,
            'ip': self.ip,
            'file_name': self.file_name,
            'timestamp': self.timestamp
        }
