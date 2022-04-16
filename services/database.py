from typing import List

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import os
from sqlalchemy import create_engine, desc
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

from services.models import UserModel, User, Base

from dotenv import load_dotenv

load_dotenv()


class DBLayer:

    db_config = {
        "drivername": "postgresql+psycopg2",
        "host": "localhost",
        "port": "5432",
        "username": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "database": os.getenv("DB_NAME"),
    }

    def __init__(self):
        self.connection = psycopg2.connect(
            user=os.getenv("DB_USER"), password=os.getenv("DB_PASS")
        )
        self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.engine = None

        self.__check_database()

        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def __check_database(self):
        cursor = self.connection.cursor()
        try:
            sql_create_database = cursor.execute(
                f'create database {os.getenv("DB_NAME")}'
            )
        except Exception as e:
            print("DATABASE ALREADY EXISTS")

        cursor.close()

        self.__create_engine()

    def __create_engine(self) -> None:
        self.engine = create_engine(URL(**DBLayer.db_config))
        self.engine.connect()

    def get_user(self, user_code: str) -> list:
        result = self.session.query(User).filter(User.code == user_code)
        if len(list(result)) > 0:
            return result[0]
        else:
            return []

    def create_user(self, user_name: str, user_code: str) -> UserModel:
        new_user = UserModel(
            code=user_code,
            name=user_name,
            messages=1,
        )
        self.session.add(new_user)
        self.session.commit()

        return new_user

    def get_all_users(self) -> List[User]:
        return list(self.session.query(User).all())

    def get_winners(self) -> List[User]:
        return self.session.query(User).filter(User.messages > 0).order_by(desc(User.messages)).limit(5).all()

    def clear_db(self):
        self.session.query(User).filter(User.id > 0).delete(synchronize_session='fetch')
        self.session.commit()

DB = DBLayer()

Base.metadata.create_all(DB.engine)
