"""
Форма документа MongoDB для сырого прайс-файла.

Зачем Mongo, а не только Postgres:
  - XML с портала приходит «как есть» (тысячи Item, служебные поля, странные типы).
  - Нам полезно хранить оригинал + метаданные скачивания для отладки и повторного парса.
  - Нормализованные цены для сравнения корзины — уже в PostgreSQL (см. models.py).

Живой MongoDB для этого урока НЕ обязателен.
Ниже — пример словаря (как выглядел бы один документ в коллекции `raw_price_files`).
"""

from __future__ import annotations

from typing import Any

# Имя коллекции в Mongo (договорённость для будущих скриптов импорта).
RAW_PRICE_FILES_COLLECTION = "raw_price_files"

# Пример документа. В реальном коде его создаст импортёр после скачивания .gz/.xml.
RAW_PRICE_FILE_EXAMPLE: dict[str, Any] = {
    # Mongo сам добавит _id: ObjectId(...), если не задать.
    "chain_id": "7290027600007",  # пример: ChainID из XML (у Шуферсаль свой)
    "store_id": "091",  # StoreID — филиал supersal91
    "source": "shufersal",  # ярлык портала
    "file_kind": "PriceFull",  # PricesFull / PromoFull / Stores и т.д.
    "original_filename": "PriceFull7290027600007-091-202511061200.xml",
    "downloaded_at": "2025-11-06T12:05:00+02:00",  # ISO-8601
    "content_type": "application/xml",
    # Вариант A (простой, для маленьких сэмплов на учёбе):
    # весь XML текстом прямо в документе.
    "xml_text": "<?xml version=\"1.0\"?>...<Root>...<Item>...</Item>...</Root>",
    # Вариант B (позже, для больших файлов): хранить байты в GridFS,
    # а в документе оставить только ссылку.
    # "gridfs_file_id": "<ObjectId файла в GridFS>",
    # "storage": "gridfs",
    "storage": "inline",  # "inline" | "gridfs"
    "parse_status": "pending",  # pending | ok | error
    "parse_error": None,
    "item_count_hint": None,  # после парса можно записать число Item
    "notes": "Учебный сэмпл; большие XML лучше не коммитить в Git (см. data/samples/).",
}


def describe_raw_price_file_schema() -> dict[str, Any]:
    """Краткое описание полей — отдаём через FastAPI stub."""
    return {
        "collection": RAW_PRICE_FILES_COLLECTION,
        "purpose": (
            "Сырой прайс сети «как скачали»: метаданные + XML (inline) "
            "или ссылка на GridFS для крупных файлов."
        ),
        "fields": {
            "chain_id": "ChainID из XML",
            "store_id": "StoreID из XML",
            "source": "Какой портал/сеть (shufersal, …)",
            "file_kind": "Тип файла: PriceFull, PromoFull, …",
            "original_filename": "Имя файла на диске/портале",
            "downloaded_at": "Когда скачали (ISO-8601)",
            "content_type": "Обычно application/xml",
            "xml_text": "Опционально: весь XML, если файл небольшой",
            "gridfs_file_id": "Опционально: id в GridFS вместо xml_text",
            "storage": "inline или gridfs",
            "parse_status": "Статус нормализации в Postgres",
            "parse_error": "Текст ошибки, если parse_status=error",
            "item_count_hint": "Сколько Item нашли после парса",
            "notes": "Свободные заметки",
        },
        "example": RAW_PRICE_FILE_EXAMPLE,
        "gridfs_note": (
            "GridFS — способ Mongo хранить большие файлы кусками. "
            "Для урока достаточно inline xml_text на маленьком сэмпле; "
            "GridFS подключим, когда появятся полные PriceFull на десятки МБ."
        ),
    }
