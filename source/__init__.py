from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/test'
app.config['JSON_SORT_KEYS'] = False
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=False)
Base = declarative_base()
from source.object import sql

Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
session.commit()

from source.views import view
from source.tool import background
