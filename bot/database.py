import os
import asyncio
import asyncpg
import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL")


class QueryHistory(Base):
    """Таблица для хранения истории запросов"""
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    query_time = Column(DateTime)
    product_sku = Column(String)


async def create_database():
    """Функция для создания БД"""
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS query_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            query_time TIMESTAMP,
            product_sku TEXT
        )
    ''')
    await conn.close()


async def add_query_to_history(user_id: int, product_sku: str):
    """Функция для добавления запроса в БД"""
    query_time = datetime.datetime.now()

    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        INSERT INTO query_history (user_id, query_time, product_sku)
        VALUES ($1, $2, $3)
    ''', user_id, query_time, product_sku)
    await conn.close()


async def get_last_5_queries():
    """Функция для получения 5 последних запросов из БД"""
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch('''
        SELECT user_id, query_time, product_sku
        FROM query_history
        ORDER BY query_time DESC
        LIMIT 5
    ''')
    await conn.close()
    return rows


async def setup_database():
    """Функция для создания базы данных и таблицы"""
    await create_database()

    engine = create_engine(DATABASE_URL, echo=True)
    Session = sessionmaker(bind=engine)
