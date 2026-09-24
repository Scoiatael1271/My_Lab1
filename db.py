"""
Модуль db.py — работа с хранилищем данных (JSON-файлы).

Обеспечивает загрузку, сохранение, импорт и экспорт данных
в форматах JSON и CSV.
"""

import json
import csv
import os
from typing import List, Dict, Any, Optional
from models import Client, Product, Order, OrderItem


class DataBase:
    """
    Класс для работы с данными через JSON-файлы.

    Parameters
    ----------
    data_dir : str
        Путь к папке с данными.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.clients_file = os.path.join(data_dir, "clients.json")
        self.products_file = os.path.join(data_dir, "products.json")
        self.orders_file = os.path.join(data_dir, "orders.json")
        self._ensure_data_dir()
        self._init_files()

    def _ensure_data_dir(self) -> None:
        """Создаёт папку data, если её нет."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
        except OSError as e:
            print(f"Ошибка создания папки: {e}")

    def _init_files(self) -> None:
        """Инициализирует пустые JSON-файлы, если они отсутствуют."""
        for filepath in [self.clients_file, self.products_file, self.orders_file]:
            if not os.path.exists(filepath):
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump([], f, ensure_ascii=False, indent=2)
                except OSError as e:
                    print(f"Ошибка создания файла {filepath}: {e}")

    # ---------- Клиенты ----------
    def load_clients(self) -> List[Client]:
        """
        Загружает список клиентов из JSON.

        Returns
        -------
        list of Client
            Список объектов Client.
        """
        try:
            with open(self.clients_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Client.from_dict(item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Ошибка загрузки клиентов: {e}")
            return []

    def save_clients(self, clients: List[Client]) -> None:
        """Сохраняет список клиентов в JSON."""
        try:
            data = [c.to_dict() for c in clients]
            with open(self.clients_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (OSError, TypeError) as e:
            print(f"Ошибка сохранения клиентов: {e}")

    def add_client(self, client: Client) -> None:
        """Добавляет клиента и сохраняет."""
        clients = self.load_clients()
        clients.append(client)
        self.save_clients(clients)

    def get_next_client_id(self) -> int:
        """Возвращает следующий свободный ID клиента."""
        clients = self.load_clients()
        if not clients:
            return 1
        return max(c.id for c in clients) + 1

    # ---------- Товары ----------
    def load_products(self) -> List[Product]:
        """Загружает список товаров из JSON."""
        try:
            with open(self.products_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Product.from_dict(item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Ошибка загрузки товаров: {e}")
            return []

    def save_products(self, products: List[Product]) -> None:
        """Сохраняет список товаров в JSON."""
        try:
            data = [p.to_dict() for p in products]
            with open(self.products_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (OSError, TypeError) as e:
            print(f"Ошибка сохранения товаров: {e}")

    def add_product(self, product: Product) -> None:
        """Добавляет товар и сохраняет."""
        products = self.load_products()
        products.append(product)
        self.save_products(products)

    def get_next_product_id(self) -> int:
        """Возвращает следующий свободный ID товара."""
        products = self.load_products()
        if not products:
            return 1
        return max(p.id for p in products) + 1

    # ---------- Заказы ----------
    def load_orders(self) -> List[Order]:
        """
        Загружает список заказов из JSON.

        Returns
        -------
        list of Order
            Список объектов Order.
        """
        try:
            with open(self.orders_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            clients = {c.id: c for c in self.load_clients()}
            orders = []
            for item in data:
                client = clients.get(item.get("client_id"))
                if client is None:
                    # Создаём временного клиента, если не найден
                    client = Client(
                        client_id=item.get("client_id", 0),
                        name=item.get("client_name", "Неизвестный"),
                        email="unknown@example.com",
                        phone="+70000000000"
                    )
                orders.append(Order.from_dict(item, client))
            return orders
        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Ошибка загрузки заказов: {e}")
            return []

    def save_orders(self, orders: List[Order]) -> None:
        """Сохраняет список заказов в JSON."""
        try:
            data = [o.to_dict() for o in orders]
            with open(self.orders_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (OSError, TypeError) as e:
            print(f"Ошибка сохранения заказов: {e}")

    def add_order(self, order: Order) -> None:
        """Добавляет заказ и сохраняет."""
        orders = self.load_orders()
        orders.append(order)
        self.save_orders(orders)

    def get_next_order_id(self) -> int:
        """Возвращает следующий свободный ID заказа."""
        orders = self.load_orders()
        if not orders:
            return 1
        return max(o.id for o in orders) + 1

    # ---------- Экспорт / Импорт CSV ----------
    def export_clients_csv(self, filepath: str) -> bool:
        """
        Экспортирует клиентов в CSV.

        Parameters
        ----------
        filepath : str
            Путь к CSV-файлу.

        Returns
        -------
        bool
            True при успехе.
        """
        try:
            clients = self.load_clients()
            with open(filepath, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["id", "name", "email", "phone", "city"])
                writer.writeheader()
                for c in clients:
                    writer.writerow(c.to_dict())
            return True
        except Exception as e:
            print(f"Ошибка экспорта клиентов в CSV: {e}")
            return False

    def import_clients_csv(self, filepath: str) -> bool:
        """Импортирует клиентов из CSV."""
        try:
            clients = self.load_clients()
            existing_ids = {c.id for c in clients}
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cid = int(row["id"])
                    if cid not in existing_ids:
                        client = Client(
                            client_id=cid,
                            name=row["name"],
                            email=row["email"],
                            phone=row["phone"],
                            city=row.get("city", "")
                        )
                        clients.append(client)
            self.save_clients(clients)
            return True
        except Exception as e:
            print(f"Ошибка импорта клиентов из CSV: {e}")
            return False

    def export_orders_csv(self, filepath: str) -> bool:
        """Экспортирует заказы в CSV."""
        try:
            orders = self.load_orders()
            with open(filepath, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["id", "client_id", "client_name", "order_date", "total"]
                )
                writer.writeheader()
                for o in orders:
                    writer.writerow({
                        "id": o.id,
                        "client_id": o.client.id,
                        "client_name": o.client.name,
                        "order_date": o.order_date,
                        "total": o.calculate_total()
                    })
            return True
        except Exception as e:
            print(f"Ошибка экспорта заказов в CSV: {e}")
            return False

    def export_to_json(self, filepath: str, data_type: str = "all") -> bool:
        """
        Экспортирует данные в один JSON-файл.

        Parameters
        ----------
        filepath : str
            Путь к файлу.
        data_type : str
            Тип данных: 'clients', 'products', 'orders' или 'all'.
        """
        try:
            result = {}
            if data_type in ("clients", "all"):
                result["clients"] = [c.to_dict() for c in self.load_clients()]
            if data_type in ("products", "all"):
                result["products"] = [p.to_dict() for p in self.load_products()]
            if data_type in ("orders", "all"):
                result["orders"] = [o.to_dict() for o in self.load_orders()]
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка экспорта в JSON: {e}")
            return False