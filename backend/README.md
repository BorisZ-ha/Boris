# Backend (FastAPI)

См. корневой [README.md](../README.md) — разделы «Запуск бэкенда» и **«Урок: модели»**.

## Файлы урока моделей

| Файл | Зачем |
|------|--------|
| `app/models.py` | SQLAlchemy: Chain, Store, Product, StorePrice, ShoppingList, ShoppingListItem |
| `app/db.py` | Подключение (SQLite fallback без живого Postgres) |
| `app/mongo_schema.py` | Пример документа сырого прайса для Mongo |
| `app/main.py` | `GET /health`, `GET /meta/models`, пустые списки |

Теория (русский): [`docs/data-models-lesson.md`](../docs/data-models-lesson.md).

## Быстрый старт

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Проверка: http://127.0.0.1:8000/meta/models
