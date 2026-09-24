"""
Модуль models.py — классы данных для системы учёта заказов.

Содержит классы:
- BaseEntity (базовый класс)
- Product (товар)
- Client (клиент)
- Order (заказ)
- OrderItem (позиция заказа)

Демонстрирует ООП: инкапсуляцию, наследование и полиморфизм.
"""

from datetime import datetime
from typing import List, Optional
import re


class BaseEntity:
    """
    Базовый класс для всех сущностей системы.

    Parameters
    ----------
    entity_id : int
        Уникальный идентификатор сущности.
    name : str
        Название или имя сущности.

    Attributes
    ----------
    _id : int
        Приватный идентификатор.
    _name : str
        Приватное имя.
    """

    def __init__(self, entity_id: int, name: str):
        self._id = entity_id
        self._name = name

    @property
    def id(self) -> int:
        """Возвращает идентификатор сущности."""
        return self._id

    @property
    def name(self) -> str:
        """Возвращает имя сущности."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Устанавливает имя сущности с проверкой."""
        if not value or not isinstance(value, str):
            raise ValueError("Имя должно быть непустой строкой")
        self._name = value.strip()

    def __str__(self) -> str:
        """Строковое представление (полиморфизм)."""
        return f"{self.__class__.__name__}(id={self._id}, name={self._name})"

    def to_dict(self) -> dict:
        """
        Преобразует объект в словарь.

        Returns
        -------
        dict
            Словарь с данными сущности.
        """
        return {"id": self._id, "name": self._name}


class Product(BaseEntity):
    """
    Класс товара.

    Parameters
    ----------
    product_id : int
        Идентификатор товара.
    name : str
        Название товара.
    price : float
        Цена товара.
    category : str, optional
        Категория товара.
    """

    def __init__(self, product_id: int, name: str, price: float, category: str = "Общее"):
        super().__init__(product_id, name)
        self._price = 0.0
        self.price = price  # используем setter
        self._category = category

    @property
    def price(self) -> float:
        """Возвращает цену товара."""
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        """Устанавливает цену с проверкой."""
        try:
            value = float(value)
            if value < 0:
                raise ValueError("Цена не может быть отрицательной")
            self._price = value
        except (TypeError, ValueError) as e:
            raise ValueError(f"Некорректная цена: {e}")

    @property
    def category(self) -> str:
        """Возвращает категорию."""
        return self._category

    def calculate_total(self, quantity: int = 1) -> float:
        """
        Рассчитывает стоимость (полиморфизм).

        Parameters
        ----------
        quantity : int
            Количество товара.

        Returns
        -------
        float
            Общая стоимость.
        """
        return self._price * quantity

    def to_dict(self) -> dict:
        """Преобразует товар в словарь."""
        data = super().to_dict()
        data.update({
            "price": self._price,
            "category": self._category
        })
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Создаёт объект Product из словаря."""
        return cls(
            product_id=data["id"],
            name=data["name"],
            price=data["price"],
            category=data.get("category", "Общее")
        )


class Client(BaseEntity):
    """
    Класс клиента.

    Parameters
    ----------
    client_id : int
        Идентификатор клиента.
    name : str
        ФИО клиента.
    email : str
        Электронная почта.
    phone : str
        Номер телефона.
    city : str, optional
        Город проживания.
    """

    # Регулярные выражения для проверки
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    PHONE_PATTERN = re.compile(r"^(\+7|8)?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$")

    def __init__(self, client_id: int, name: str, email: str, phone: str, city: str = ""):
        super().__init__(client_id, name)
        self._email = ""
        self._phone = ""
        self.email = email
        self.phone = phone
        self._city = city

    @property
    def email(self) -> str:
        """Возвращает email."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        """Устанавливает email с проверкой регулярным выражением."""
        if not self.EMAIL_PATTERN.match(value):
            raise ValueError(f"Некорректный email: {value}")
        self._email = value

    @property
    def phone(self) -> str:
        """Возвращает телефон."""
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        """Устанавливает телефон с проверкой регулярным выражением."""
        # Упрощаем номер для проверки
        cleaned = re.sub(r"[\s\-\(\)]", "", value)
        if not re.match(r"^(\+7|8)?\d{10}$", cleaned):
            raise ValueError(f"Некорректный номер телефона: {value}")
        self._phone = value

    @property
    def city(self) -> str:
        """Возвращает город."""
        return self._city

    def to_dict(self) -> dict:
        """Преобразует клиента в словарь."""
        data = super().to_dict()
        data.update({
            "email": self._email,
            "phone": self._phone,
            "city": self._city
        })
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Client":
        """Создаёт объект Client из словаря."""
        return cls(
            client_id=data["id"],
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            city=data.get("city", "")
        )


class OrderItem(Product):
    """
    Позиция заказа (наследование от Product).

    Parameters
    ----------
    product : Product
        Исходный товар.
    quantity : int
        Количество.
    """

    def __init__(self, product: Product, quantity: int = 1):
        super().__init__(
            product_id=product.id,
            name=product.name,
            price=product.price,
            category=product.category
        )
        self._quantity = max(1, quantity)

    @property
    def quantity(self) -> int:
        """Возвращает количество."""
        return self._quantity

    def calculate_total(self, quantity: Optional[int] = None) -> float:
        """
        Рассчитывает стоимость позиции (полиморфизм — переопределение).

        Parameters
        ----------
        quantity : int, optional
            Количество (если None — используется своё).

        Returns
        -------
        float
            Общая стоимость позиции.
        """
        qty = quantity if quantity is not None else self._quantity
        return self._price * qty

    def to_dict(self) -> dict:
        """Преобразует позицию в словарь."""
        data = super().to_dict()
        data["quantity"] = self._quantity
        return data


class Order(BaseEntity):
    """
    Класс заказа.

    Parameters
    ----------
    order_id : int
        Идентификатор заказа.
    client : Client
        Клиент, сделавший заказ.
    items : list of OrderItem
        Список позиций заказа.
    order_date : str, optional
        Дата заказа в формате YYYY-MM-DD.
    """

    def __init__(
        self,
        order_id: int,
        client: Client,
        items: Optional[List[OrderItem]] = None,
        order_date: Optional[str] = None
    ):
        super().__init__(order_id, f"Заказ #{order_id}")
        self._client = client
        self._items = items if items is not None else []
        self._order_date = order_date or datetime.now().strftime("%Y-%m-%d")

    @property
    def client(self) -> Client:
        """Возвращает клиента."""
        return self._client

    @property
    def items(self) -> List[OrderItem]:
        """Возвращает список позиций."""
        return self._items

    @property
    def order_date(self) -> str:
        """Возвращает дату заказа."""
        return self._order_date

    def add_item(self, item: OrderItem) -> None:
        """Добавляет позицию в заказ."""
        self._items.append(item)

    def calculate_total(self) -> float:
        """
        Рассчитывает общую стоимость заказа (полиморфизм).

        Returns
        -------
        float
            Сумма всех позиций.
        """
        total = 0.0
        for item in self._items:
            total += item.calculate_total()
        return total

    def to_dict(self) -> dict:
        """Преобразует заказ в словарь."""
        return {
            "id": self._id,
            "client_id": self._client.id,
            "client_name": self._client.name,
            "order_date": self._order_date,
            "items": [item.to_dict() for item in self._items],
            "total": self.calculate_total()
        }

    @classmethod
    def from_dict(cls, data: dict, client: Client) -> "Order":
        """Создаёт объект Order из словаря."""
        items = []
        for item_data in data.get("items", []):
            product = Product(
                product_id=item_data["id"],
                name=item_data["name"],
                price=item_data["price"],
                category=item_data.get("category", "Общее")
            )
            items.append(OrderItem(product, item_data.get("quantity", 1)))
        return cls(
            order_id=data["id"],
            client=client,
            items=items,
            order_date=data.get("order_date")
        )