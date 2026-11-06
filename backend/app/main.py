"""Shopping Cart API — каркас + stubs моделей данных (урок SC-4)."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import ALL_SQL_MODELS
from app.mongo_schema import describe_raw_price_file_schema

app = FastAPI(
    title="Shopping Cart API",
    description=(
        "Сравнение цен в израильских сетях. "
        "Сейчас: health + описание моделей (без полного импорта прайсов)."
    ),
    version="0.2.0",
)

# Разрешаем запросы с локального Vite-сервера во время разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Проверка, что API жив. Браузер или фронт могут дергать этот адрес."""
    return {"status": "ok"}


@app.get("/meta/models")
def meta_models() -> dict[str, Any]:
    """
    Учебный эндпоинт: какие SQL-таблицы и Mongo-коллекция задуманы.

    Не ходит в БД — только описывает модели. Удобно открыть в /docs.
    """
    sql_tables = [
        {
            "class_name": model.__name__,
            "table": model.__tablename__,
            "doc": (model.__doc__ or "").strip().split("\n", 1)[0],
        }
        for model in ALL_SQL_MODELS
    ]
    return {
        "postgres": {
            "role": "Нормализованные сети, магазины, товары, цены, списки покупок",
            "tables": sql_tables,
        },
        "mongodb": describe_raw_price_file_schema(),
        "lesson": "docs/data-models-lesson.md",
    }


@app.get("/products")
def list_products() -> list[dict[str, Any]]:
    """Заглушка: позже вернём товары из Postgres. Пока пустой список."""
    return []


@app.get("/chains")
def list_chains() -> list[dict[str, Any]]:
    """Заглушка: список сетей. Пока пусто — импортёра ещё нет."""
    return []


@app.get("/shopping-lists")
def list_shopping_lists() -> list[dict[str, Any]]:
    """Заглушка: списки покупок. Пока пусто."""
    return []
