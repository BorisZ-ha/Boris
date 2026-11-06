# Архитектура Shopping Cart (черновик)

Кратко: **что куда кладём** и **зачем**. Полный пайплайн цен — на следующих уроках.

## Слои

| Слой | Папка / технология | Роль |
|------|--------------------|------|
| UI | `frontend/` — React + TypeScript + Vite | Список покупок, результат сравнения (русский UI) |
| API | `backend/` — FastAPI + uvicorn | HTTP-эндпоинты: продукты, корзина, сравнение |
| Основная БД | PostgreSQL | Нормализованные товары, магазины, цены, списки (`backend/app/models.py`) |
| Сырые дампы | MongoDB | XML/документы прайсов «как пришли» (`backend/app/mongo_schema.py`) |
| Импорт | Python-скрипты / сервисы *(позже)* | Скачать → распарсить → положить в Mongo → нормализовать в Postgres |

Урок по моделям (ER, SQL vs Mongo, ItemCode): [`docs/data-models-lesson.md`](data-models-lesson.md).

## Поток данных (целевой)

```
Портал сети (XML/gzip)
        ↓
   импорт (Python)
        ↓
   MongoDB (raw)  →  нормализация  →  PostgreSQL
                                              ↓
                                         FastAPI
                                              ↓
                                      React (Vite)
```

Сейчас: каркас UI + API stubs (`/health`, `/meta/models`, пустые списки).
Живые Postgres/Mongo и Docker **не** обязательны, чтобы понять модели.

## Сети MVP (интерес)

Shufersal, Yochananof, Osher Ad, Rami Levy — публичные прайсы по закону о прозрачности цен.

## Что не в этом каркасе

- Авторизация, скрапинг «в обход», полный импорт прайсов
- Docker Compose с Postgres/Mongo
- Мобильное приложение
