from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config import config
from models import Base

# Создаем engine
engine = create_engine(
    config.DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20
)

# Создаем фабрику сессий
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def init_db():
    """Создает все таблицы в базе данных"""
    Base.metadata.create_all(engine)

def get_db():
    """Возвращает сессию для работы с БД"""
    return Session()

def close_db():
    """Закрывает сессию"""
    Session.remove()