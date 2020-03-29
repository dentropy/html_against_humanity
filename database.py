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
engine = create_engine(
    "sqlite:///cards_against_humanity.sqlite",
    connect_args={'check_same_thread': False}
    )
## Also same thread is from https://stackoverflow.com/questions/48218065/programmingerror-sqlite-objects-created-in-a-thread-can-only-be-used-in-that-sa

Base = declarative_base()
Session = sessionmaker(bind=engine, autoflush=False)
## auto flush was added because of https://stackoverflow.com/questions/32922210/why-does-a-query-invoke-a-auto-flush-in-sqlalchemy

session = Session()

class UserSessions(Base):
    __tablename__ = "UserSessions"
    id = Column(Integer, primary_key=True)
    user_cookie = Column(String(32), unique=True)
    player_name = Column(String(100))

class WhiteCards(Base):
    __tablename__ = "WhiteCards"
    id = Column(Integer, primary_key=True)
    white_cards = Column(String(1024))

class BlackCards(Base):
    __tablename__ = "BlackCards"
    id = Column(Integer, primary_key=True)
    black_cards = Column(String(1024))
    num_white_cards = Column(Integer)

class Games(Base):
    __tablename__ = "Games"
    id = Column(Integer, primary_key=True)
    admin = Column(Integer)
    game_id = Column(String(7))
    game_started = Column(Boolean)
    players = Column(String(1024))# JSON list of all players playing
    turn_number = Column(Integer)
    players_hand = Column(String(1024))# Every Players hand stored as JSON
    players_white_card = Column(String(1024))# Current white card in play
    players_score = Column(String(1024))# Every players score stored as JSON
    white_cards_played = Column(String(1024))# JSON list of all white cards played
    black_cards_played = Column(String(1024))# JSON list of all black cards played
    turn_selected_player = Column(String(1024))# Who's turn it is
    turn_phase = Column(String(1024))
    turn_white_cards = Column(String(1024))# JSON object of who has gone so far this round
    turn_order = Column(String(1024))

class GameMetadata(Base):
    __tablename__ = "GameMetadata"
    id = Column(Integer, primary_key=True)

def CreateDatabase():
    Base.metadata.create_all(engine)

CreateDatabase()