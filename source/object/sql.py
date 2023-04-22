from sqlalchemy import Boolean, Column, Integer, String, LargeBinary, ForeignKey, REAL, Numeric, DateTime, DECIMAL, \
    BIGINT, Float
from source import Base
import json

from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def get_access_token_from_refresh_token(credential_json_string):
    creds: Credentials = service_account.Credentials.from_service_account_info(
        json.loads(credential_json_string),
        scopes=['https://www.googleapis.com/auth/drive']
    )
    creds.refresh(Request())
    return creds.token


class Credential(Base):
    __tablename__ = 'credential'
    id = Column(Integer, primary_key=True)
    sa_json_string = Column(String, nullable=False)
    last_used_timestamp = Column(Integer, default=0)
    total_bytes_used = Column(Float, default=0)
    is_abuse_reported = Column(Boolean, default=False)

    def __repr__(self):
        return '<Id: {}>'.format(self.id)

    def to_json(self):
        return {
            'id': self.id,
            'access_token': get_access_token_from_refresh_token(self.sa_json_string),
            'last_used_time': self.last_used_timestamp,
            'total_bytes_used': self.total_bytes_used,
            'is_abuse_reported': self.is_abuse_reported
        }


class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    ip = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    project_name = Column(String, nullable=False)
    timestamp = Column(Integer)

    def __repr__(self):
        return '<Id: {}>'.format(self.id)

    def to_json(self):
        return {
            'id': self.id,
            'ip': self.ip,
            'file_name': self.file_name,
            'project_name': self.project_name,
            'timestamp': self.timestamp
        }
