import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import os

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init(db_file):
    """Подключение к БД"""
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    # Создаём папку для БД, если её нет
    db_dir = os.path.dirname(db_file.strip())
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn_str = f"sqlite:///{db_file.strip()}?check_same_thread=False"
    print(f"🔗 Подключение к базе данных: {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    # Импорт всех моделей
    import models

    SqlAlchemyBase.metadata.create_all(engine)
    print("✅ База данных и таблицы созданы (если их не было)")


def create_session() -> Session:
    """Создаёт сессию для работы с БД"""
    global __factory
    if not __factory:
        raise Exception("База данных не инициализирована. Вызовите global_init() сначала.")
    return __factory()