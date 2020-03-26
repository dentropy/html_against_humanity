#!/usr/bin/python3
import os
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

print("Create sqlite database")
engine = create_engine("sqlite:///cards_against_humanity.sqlite")

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class UserSessions(Base):
    __tablename__ = "UserSessions"
    id = Column(Integer, primary_key=True)
    user_cookie = Column(String(32), unique=True)

class Cards(Base):
    __tablename__ = "Cards"
    id = Column(Integer, primary_key=True)

class Games(Base):
    __tablename__ = "Games"
    id = Column(Integer, primary_key=True)
    cost = Column(Integer)

class GameMetadata(Base):
    __tablename__ = "GameMetadata"
    id = Column(Integer, primary_key=True)

def CreateDatabase():
    Base.metadata.create_all(engine)

CreateDatabase()