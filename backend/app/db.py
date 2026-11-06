"""
Подключение к PostgreSQL (заготовка).

На этом уроке живой сервер БД НЕ обязателен.
Файл нужен, чтобы понимать: «куда потом воткнём URL базы».

Когда будешь готов поднять Postgres (локально или в Docker):
1. Создай файл `.env` в корне или в `backend/` с строкой:
   DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/shopping_cart
2. Раскомментируй/вызови `get_engine()` из скрипта миграций или lifespan FastAPI.
"""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Общий предок всех SQLAlchemy-моделей (таблицы Postgres)."""


def get_database_url() -> str:
    """Читаем URL из окружения; для учёбы есть безопасный SQLite-fallback."""
    return os.getenv(
        "DATABASE_URL",
        # SQLite-файл — чтобы можно было поиграться без установки Postgres.
        # В проде/MVP целевой вариант: PostgreSQL (см. docs/data-models-lesson.md).
        "sqlite:///./shopping_cart_dev.db",
    )


def get_engine() -> Engine:
    """Создаёт engine. Вызывай только когда реально нужна БД."""
    url = get_database_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, echo=False, connect_args=connect_args)


def get_session_factory(engine: Engine | None = None):
    """Фабрика сессий Session — «окно» в БД на время одного запроса."""
    eng = engine or get_engine()
    return sessionmaker(bind=eng, autoflush=False, autocommit=False)
