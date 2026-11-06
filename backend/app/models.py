"""
SQL-модели Shopping Cart (PostgreSQL / SQLAlchemy).

Связь с XML Шуферсаль (PriceFull):
  ChainID  → Chain.chain_id
  StoreID  → Store.store_id  (внутри конкретной сети)
  ItemCode → Product.item_code  ← главный ключ сравнения между сетями
  ItemName → Product.name (или StorePrice.name_as_sold — имя «как в прайсе»)
  ItemPrice → StorePrice.item_price
  UnitOfMeasurePrice → StorePrice.unit_of_measure_price
  bIsWeighted → StorePrice.is_weighted

Зачем нормализуем:
  Один товар (один штрихкод) может продаваться в разных магазинах по разной цене.
  Список покупок ссылается на Product, а сравнение суммирует StorePrice по выбранным сетям.

Живой Postgres для этого урока не нужен — достаточно читать классы и комментарии.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Chain(Base):
    """
    Сеть магазинов (Шуферсаль, Рами Леви, …).

    В XML: поле ChainID (например у Шуферсаль — свой числовой код сети).
    """

    __tablename__ = "chains"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Код сети из прайса — сохраняем как строку: у разных порталов формат разный.
    chain_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    # Короткий ярлык для UI: "shufersal", "rami_levy", …
    slug: Mapped[str] = mapped_column(String(64), unique=True)

    stores: Mapped[list[Store]] = relationship(back_populates="chain")

    def __repr__(self) -> str:
        return f"<Chain {self.slug} chain_id={self.chain_id}>"


class Store(Base):
    """
    Конкретный филиал сети.

    В XML: StoreID. Важно: StoreID уникален *внутри* сети, не глобально.
    Поэтому UniqueConstraint(chain_id FK + store_id).
    """

    __tablename__ = "stores"
    __table_args__ = (
        UniqueConstraint("chain_pk", "store_id", name="uq_store_per_chain"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    chain_pk: Mapped[int] = mapped_column(ForeignKey("chains.id"), index=True)
    # Код филиала из XML, напр. "091" для supersal91.
    store_id: Mapped[str] = mapped_column(String(32))
    name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    chain: Mapped[Chain] = relationship(back_populates="stores")
    prices: Mapped[list[StorePrice]] = relationship(back_populates="store")

    def __repr__(self) -> str:
        return f"<Store chain_pk={self.chain_pk} store_id={self.store_id}>"


class Product(Base):
    """
    Товар «в мире приложения» — одна запись на ItemCode (штрихкод / код товара).

    ItemCode — то, по чему мы сравниваем один и тот же товар в разных сетях.
    Имя может чуть отличаться у сетей; каноническое имя храним здесь,
    а «как написано в прайсе» можно дублировать в StorePrice.name_as_sold.
    """

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Главный бизнес-ключ из XML ItemCode.
    item_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(512))
    # Опционально: единица измерения из прайса (кг, л, шт) — уточним при импорте.
    unit_of_measure: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    prices: Mapped[list[StorePrice]] = relationship(back_populates="product")
    list_items: Mapped[list[ShoppingListItem]] = relationship(back_populates="product")

    def __repr__(self) -> str:
        return f"<Product {self.item_code} {self.name[:40]!r}>"


class StorePrice(Base):
    """
    Цена конкретного товара в конкретном магазине на момент снимка прайса.

    Одна строка ≈ одна запись Item из PriceFull для данного Store.
    Позже импортёр будет UPSERT-ить по (store, product) или хранить историю —
    для MVP достаточно «текущая цена» + updated_at.
    """

    __tablename__ = "store_prices"
    __table_args__ = (
        UniqueConstraint("store_pk", "product_pk", name="uq_price_per_store_product"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    store_pk: Mapped[int] = mapped_column(ForeignKey("stores.id"), index=True)
    product_pk: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)

    # ItemPrice — цена за упаковку / за единицу продажи.
    item_price: Mapped[Decimal] = mapped_column(Numeric(12, 3))
    # UnitOfMeasurePrice — цена за единицу измерения (удобно сравнивать весовые).
    unit_of_measure_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 3), nullable=True
    )
    # bIsWeighted: True = весовой товар (цена часто за кг).
    is_weighted: Mapped[bool] = mapped_column(Boolean, default=False)
    # Имя «как в XML» — может отличаться от Product.name.
    name_as_sold: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    store: Mapped[Store] = relationship(back_populates="prices")
    product: Mapped[Product] = relationship(back_populates="prices")

    def __repr__(self) -> str:
        return f"<StorePrice store={self.store_pk} product={self.product_pk} {self.item_price}>"


class ShoppingList(Base):
    """
    Список покупок пользователя (пока без логина — просто сущность для MVP).

    Позже: user_id / сессия. Сейчас достаточно title + created_at.
    """

    __tablename__ = "shopping_lists"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256), default="Мой список")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    items: Mapped[list[ShoppingListItem]] = relationship(
        back_populates="shopping_list",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ShoppingList {self.id} {self.title!r}>"


class ShoppingListItem(Base):
    """
    Строка списка: какой Product и сколько штук/кг.

    Сравнение корзины = для каждой сети суммировать
    quantity * StorePrice.item_price по выбранным магазинам/сетям.
    """

    __tablename__ = "shopping_list_items"
    __table_args__ = (
        UniqueConstraint(
            "shopping_list_pk",
            "product_pk",
            name="uq_item_per_list_product",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    shopping_list_pk: Mapped[int] = mapped_column(
        ForeignKey("shopping_lists.id"), index=True
    )
    product_pk: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    # Для штучных — целое; для весовых можно 0.5 кг и т.п.
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("1"))

    shopping_list: Mapped[ShoppingList] = relationship(back_populates="items")
    product: Mapped[Product] = relationship(back_populates="list_items")

    def __repr__(self) -> str:
        return (
            f"<ShoppingListItem list={self.shopping_list_pk} "
            f"product={self.product_pk} qty={self.quantity}>"
        )


# Удобный список для stubs / документации API.
ALL_SQL_MODELS = (
    Chain,
    Store,
    Product,
    StorePrice,
    ShoppingList,
    ShoppingListItem,
)
