"""
📦 Пакет для миграций базы данных

Для работы с миграциями используйте Alembic:
1. Установка: pip install alembic
2. Инициализация: alembic init migrations
3. Создание миграции: alembic revision --autogenerate -m "description"
4. Применение: alembic upgrade head
"""

# Этот файл нужен для того, чтобы папка migrations была Python-пакетом