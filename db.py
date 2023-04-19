from sqlalchemy import Column, JSON, Integer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

PG_DSN = 'postgresql+asyncpg://wooft:Shambala@127.0.0.1:5432/asyncio'

engine = create_async_engine(PG_DSN)
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class Person(Base):
    __tablename__ = 'swapi_person'

    id = Column(Integer, primary_key=True, autoincrement=True)
    json = Column(JSON)