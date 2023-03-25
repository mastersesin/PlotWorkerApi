from sqlalchemy import Boolean, Column, Integer, String, LargeBinary, ForeignKey, REAL, Numeric, DateTime, DECIMAL, \
    BIGINT, Float
from source import Base
import json


class Credential(Base):
    __tablename__ = 'credential'
    id = Column(Integer, primary_key=True)
    rclone_token = Column(String, nullable=False)
    client_id = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)
    last_used_timestamp = Column(Integer, default=0)
    total_bytes_used = Column(Float, default=0)
    is_abuse_reported = Column(Boolean, default=False)

    def __repr__(self):
        return '<Id: {}>'.format(self.id)

    def to_json(self):
        return {
            'id': self.id,
            'rclone_token': json.loads(self.rclone_token),
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'last_used_time': self.last_used_timestamp,
            'total_bytes_used': self.total_bytes_used,
            'is_abuse_reported': self.is_abuse_reported
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
