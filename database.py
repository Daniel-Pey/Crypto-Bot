"""
🗄️ Настройка подключения к базе данных SQLite через SQLAlchemy
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from config import config
from models import Base
from utils.logger import logger

# ============================================================
# 🔧 НАСТРОЙКА ПОДКЛЮЧЕНИЯ К SQLITE
# ============================================================

def get_engine():
    """
    🔧 Создание движка SQLAlchemy для SQLite
    
    Returns:
        Engine: Движок SQLAlchemy
    """
    # 📝 Для SQLite нужно добавить специальные параметры
    if config.DATABASE_URL.startswith('sqlite://'):
        # 🔧 Настройка для SQLite
        engine = create_engine(
            config.DATABASE_URL,
            echo=False,  # 🚫 Отключаем логирование SQL-запросов
            connect_args={
                'check_same_thread': False,  # 🔄 Разрешаем использование из разных потоков
                'timeout': 30  # ⏱️ Таймаут ожидания блокировки (сек)
            },
            poolclass=StaticPool,  # 📦 Используем статический пул для SQLite
            pool_size=10,
            max_overflow=20
        )
        
        # 🔧 Включаем поддержку внешних ключей для SQLite
        @event.listens_for(engine, 'connect')
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute('PRAGMA foreign_keys=ON')
            cursor.close()
        
        logger.info("🗄️ SQLite база данных настроена")
    else:
        # 📦 Для других БД (PostgreSQL, MySQL и т.д.)
        engine = create_engine(
            config.DATABASE_URL,
            echo=False,
            pool_size=10,
            max_overflow=20
        )
    
    return engine

# ============================================================
# 📦 СОЗДАНИЕ ДВИЖКА И СЕССИЙ
# ============================================================

# 🔧 Создаем движок
engine = get_engine()

# 📦 Создаем фабрику сессий
session_factory = sessionmaker(bind=engine)

# 🔄 Создаем scoped_session для потокобезопасности
Session = scoped_session(session_factory)

# ============================================================
# 🛠️ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def init_db():
    """
    🚀 Инициализация базы данных
    
    Создает все таблицы, если они еще не существуют
    """
    try:
        logger.info("🗄️ Создание таблиц в базе данных...")
        Base.metadata.create_all(engine)
        logger.info("✅ Таблицы успешно созданы")
    except Exception as e:
        logger.error(f"💥 Ошибка при создании таблиц: {e}")
        raise

def get_db():
    """
    📊 Получение сессии для работы с БД
    
    Returns:
        Session: Сессия SQLAlchemy
    """
    return Session()

def close_db():
    """
    🧹 Закрытие сессии
    """
    try:
        Session.remove()
        logger.debug("🧹 Сессия закрыта")
    except Exception as e:
        logger.error(f"💥 Ошибка при закрытии сессии: {e}")

def drop_all_tables():
    """
    ⚠️ УДАЛЕНИЕ ВСЕХ ТАБЛИЦ (для тестирования)
    
    Внимание! Эта функция удаляет все данные!
    """
    try:
        logger.warning("⚠️ УДАЛЕНИЕ ВСЕХ ТАБЛИЦ!")
        Base.metadata.drop_all(engine)
        logger.info("✅ Все таблицы удалены")
    except Exception as e:
        logger.error(f"💥 Ошибка при удалении таблиц: {e}")

# ============================================================
# 📝 КОНТЕКСТНЫЙ МЕНЕДЖЕР ДЛЯ РАБОТЫ С БД
# ============================================================

from contextlib import contextmanager

@contextmanager
def db_session():
    """
    📦 Контекстный менеджер для работы с БД
    
    Использование:
        with db_session() as db:
            user = db.query(User).first()
    
    Returns:
        Session: Сессия SQLAlchemy
    """
    db = get_db()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()