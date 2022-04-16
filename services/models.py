from pydantic import constr
from pydantic.dataclasses import dataclass
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    code = Column(String(20), index=True, nullable=False, unique=True)
    name = Column(String(63), unique=True)
    messages = Column(Integer, nullable=False)


@dataclass
class UserModel:
    code: constr(max_length=20)
    name: constr(max_length=63)
    messages: int


mapper(UserModel, User)
