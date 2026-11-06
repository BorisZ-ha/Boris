# Урок: модели данных (SQL + Mongo)

После того как ты открыл PriceFull XML Шуферсаль глазами, следующий шаг —
**разложить поля по таблицам**, чтобы приложение умело сравнивать корзину.

Живые серверы PostgreSQL и MongoDB **не обязательны** для этого урока.
Достаточно прочитать модели в коде и этот файл. Базы подключим, когда дойдём
до импорта и API сравнения.

---

## Зачем две базы

| Хранилище | Что кладём | Почему |
|-----------|------------|--------|
| **PostgreSQL (SQL)** | Сети, магазины, товары, цены, списки покупок | Связи, уникальность штрихкода, суммы, JOIN — удобно и понятно на собесе |
| **MongoDB** | Сырой XML прайса + метаданные скачивания | Документ «как пришёл», без схемы; удобно отлаживать парсер и не потерять оригинал |

Коротко: **Mongo = архив и сырьё**, **Postgres = то, по чему считаем «где дешевле»**.

---

## Поля XML → наши сущности

Ты уже видел в файле примерно такое:

| Поле XML | Куда в SQL | Смысл |
|----------|------------|--------|
| `ChainID` | `chains.chain_id` | Код сети |
| `StoreID` | `stores.store_id` (+ связь с сетью) | Филиал *внутри* сети |
| `ItemCode` | `products.item_code` | Штрихкод / код товара — **ключ сравнения между сетями** |
| `ItemName` | `products.name` (+ опционально `store_prices.name_as_sold`) | Название |
| `ItemPrice` | `store_prices.item_price` | Цена |
| `UnitOfMeasurePrice` | `store_prices.unit_of_measure_price` | Цена за ед. измерения |
| `bIsWeighted` | `store_prices.is_weighted` | Весовой товар? |

**Почему `ItemCode` такой важный?**  
Один и тот же йогурт в Шуферсаль и в Рами Леви должен иметь один штрихкод.
Тогда список покупок хранит «хочу этот `ItemCode`», а сравнение — это сумма
`ItemPrice` по выбранной сети для каждого кода из списка.

`StoreID` сам по себе **не глобальный**: у разных сетей может быть «магазин 091».
Поэтому в таблице `stores` уникальность — пара *(сеть + store_id)*.

---

## ER-схема (упрощённо)

```text
┌────────────┐       ┌────────────┐       ┌──────────────┐
│   Chain    │1     *│   Store    │1     *│  StorePrice  │
│ chain_id   │───────│ store_id   │───────│ item_price   │
│ name       │       │ city       │       │ is_weighted  │
└────────────┘       └────────────┘       └──────┬───────┘
                                                 │*
                                                 │
                                          ┌──────┴───────┐
                                          │   Product    │
                                          │ item_code UK │
                                          │ name         │
                                          └──────┬───────┘
                                                 │*
                                                 │
┌────────────────┐       ┌───────────────────────┴──────┐
│ ShoppingList   │1     *│ ShoppingListItem              │
│ title          │───────│ quantity                      │
└────────────────┘       └───────────────────────────────┘

Mongo (отдельно, не FK в SQL):
  raw_price_files { chain_id, store_id, xml_text | gridfs_file_id, … }
```

Стрелки «1 — *» читаются так: *одна сеть → много магазинов*;
*один магазин → много цен*; *один товар → много цен в разных магазинах*.

---

## Где смотреть код

| Файл | Содержание |
|------|------------|
| [`backend/app/models.py`](../backend/app/models.py) | SQLAlchemy: `Chain`, `Store`, `Product`, `StorePrice`, `ShoppingList`, `ShoppingListItem` |
| [`backend/app/db.py`](../backend/app/db.py) | Заготовка подключения (SQLite fallback без установки Postgres) |
| [`backend/app/mongo_schema.py`](../backend/app/mongo_schema.py) | Пример документа сырого прайса + заметка про GridFS |
| [`backend/app/main.py`](../backend/app/main.py) | Stubs: `/meta/models`, пустые списки `/products`, `/chains`, `/shopping-lists` |
| [`docker-compose.sketch.yml`](../docker-compose.sketch.yml) | *Опционально*: набросок Postgres + Mongo (не обязателен для урока) |

---

## Что сделать руками (терминал VS Code)

Корень репозитория → бэкенд → venv → зависимости → сервер
(если venv уже создавал на прошлом уроке — шаги 2–3 можно пропустить):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Потом в браузере:

1. [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) — `{"status":"ok"}`
2. [http://127.0.0.1:8000/meta/models](http://127.0.0.1:8000/meta/models) — описание таблиц и Mongo-документа
3. [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) — интерактивная документация FastAPI
4. [http://127.0.0.1:8000/products](http://127.0.0.1:8000/products) — пока `[]` (это нормально)

*(Опционально)* создать пустые таблицы через SQLAlchemy без Postgres —
подставится SQLite-файл `shopping_cart_dev.db` в `backend/`:

```bash
cd backend
source .venv/bin/activate
python -c "from app.db import Base, get_engine; from app import models; Base.metadata.create_all(get_engine()); print('tables ok')"
```

Файл `*.db` в Git не коммитим (см. `.gitignore`).

---

## Что сказать на собеседовании

> «Сырые прайсы сетей храню в Mongo как документы, а для сравнения корзины
> нормализую в PostgreSQL: сеть → магазин → цена товара. Товар идентифицирую
> по `ItemCode` (штрихкод), поэтому один список покупок можно посчитать
> по нескольким сетям.»

---

## Чего в этом уроке ещё нет (намеренно)

- Импортёр XML → Mongo → Postgres
- Планировщик скачивания несколько раз в день
- Полноценный API «сравни мою корзину»
- Обязательный Docker

Это следующие шаги после того, как модели станут привычными.
