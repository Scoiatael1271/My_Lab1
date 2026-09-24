"""
Модуль analysis.py — функции визуализации и анализа данных.

Использует pandas, matplotlib, seaborn и networkx.
Содержит функции с параметрами, рекурсией и лямбда-выражениями.
"""

from typing import List, Dict, Tuple, Optional
from collections import Counter
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from models import Client, Order, Product


def sort_orders_by_date(orders: List[Order], reverse: bool = False) -> List[Order]:
    """
    Собственная сортировка заказов по дате (рекурсивная реализация merge-sort).

    Parameters
    ----------
    orders : list of Order
        Список заказов.
    reverse : bool
        Если True — сортировка по убыванию.

    Returns
    -------
    list of Order
        Отсортированный список.
    """
    if len(orders) <= 1:
        return orders

    mid = len(orders) // 2
    left = sort_orders_by_date(orders[:mid], reverse)
    right = sort_orders_by_date(orders[mid:], reverse)

    return _merge_by_date(left, right, reverse)


def _merge_by_date(left: List[Order], right: List[Order], reverse: bool) -> List[Order]:
    """Вспомогательная функция слияния для сортировки по дате."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if reverse:
            condition = left[i].order_date >= right[j].order_date
        else:
            condition = left[i].order_date <= right[j].order_date
        if condition:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def sort_orders_by_cost(orders: List[Order], reverse: bool = True) -> List[Order]:
    """
    Сортировка заказов по стоимости с использованием лямбда-выражения.

    Parameters
    ----------
    orders : list of Order
        Список заказов.
    reverse : bool
        Если True — по убыванию стоимости.

    Returns
    -------
    list of Order
        Отсортированный список.
    """
    return sorted(orders, key=lambda o: o.calculate_total(), reverse=reverse)


def get_top_clients(orders: List[Order], n: int = 5) -> List[Tuple[str, int]]:
    """
    Возвращает топ-N клиентов по числу заказов.

    Parameters
    ----------
    orders : list of Order
        Список заказов.
    n : int
        Количество клиентов в топе.

    Returns
    -------
    list of tuple
        Список пар (имя_клиента, количество_заказов).
    """
    counter = Counter(o.client.name for o in orders)
    # Используем лямбда для сортировки
    top = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:n]
    return top


def get_orders_dynamics(orders: List[Order]) -> Dict[str, int]:
    """
    Считает количество заказов по датам.

    Parameters
    ----------
    orders : list of Order
        Список заказов.

    Returns
    -------
    dict
        Словарь {дата: количество}.
    """
    dates = [o.order_date for o in orders]
    counter = Counter(dates)
    # Сортируем по дате с лямбдой
    sorted_dates = sorted(counter.items(), key=lambda x: x[0])
    return dict(sorted_dates)


def plot_top_clients(orders: List[Order], n: int = 5, save_path: Optional[str] = None) -> None:
    """
    Строит столбчатую диаграмму топ-клиентов.

    Parameters
    ----------
    orders : list of Order
        Список заказов.
    n : int
        Количество клиентов.
    save_path : str, optional
        Путь для сохранения графика.
    """
    try:
        top = get_top_clients(orders, n)
        if not top:
            print("Нет данных для построения графика топ-клиентов")
            return

        names = [item[0] for item in top]
        counts = [item[1] for item in top]

        plt.figure(figsize=(11, 7))
        ax = sns.barplot(x=counts, y=names, palette="viridis", hue=names, legend=False)
        plt.title(f"Топ-{n} клиентов по числу заказов", fontsize=14, fontweight="bold")
        plt.xlabel("Количество заказов", fontsize=12)
        plt.ylabel("Клиент", fontsize=12)

        # Подписи значений на столбцах (крупные и заметные)
        for i, count in enumerate(counts):
            ax.text(count + 0.15, i, f" {count}", va="center", fontsize=13, fontweight="bold")

        # Расширяем ось X, чтобы цифры не обрезались
        max_count = max(counts) if counts else 1
        ax.set_xlim(0, max_count * 1.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
        plt.show()
    except Exception as e:
        print(f"Ошибка построения графика топ-клиентов: {e}")


def plot_orders_dynamics(orders: List[Order], save_path: Optional[str] = None) -> None:
    """
    Строит график динамики количества заказов по датам.

    Parameters
    ----------
    orders : list of Order
        Список заказов.
    save_path : str, optional
        Путь для сохранения графика.
    """
    try:
        dynamics = get_orders_dynamics(orders)
        if not dynamics:
            print("Нет данных для построения динамики заказов")
            return

        dates = list(dynamics.keys())
        counts = list(dynamics.values())

        plt.figure(figsize=(12, 6))
        sns.lineplot(x=dates, y=counts, marker="o", color="steelblue")
        plt.title("Динамика количества заказов по датам")
        plt.xlabel("Дата")
        plt.ylabel("Количество заказов")
        plt.xticks(rotation=45)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
        plt.show()
    except Exception as e:
        print(f"Ошибка построения динамики заказов: {e}")


def build_client_graph(
    orders: List[Order],
    clients: List[Client],
    by: str = "city",
    save_path: Optional[str] = None
) -> None:
    """
    Строит граф связей клиентов (по городу или общим товарам).

    Parameters
    ----------
    orders : list of Order
        Список заказов.
    clients : list of Client
        Список клиентов.
    by : str
        Критерий связи: 'city' или 'products'.
    save_path : str, optional
        Путь для сохранения графика.
    """
    try:
        G = nx.Graph()

        # Добавляем узлы
        for client in clients:
            G.add_node(client.name, city=client.city)

        if by == "city":
            # Связываем клиентов из одного города
            city_groups: Dict[str, List[str]] = {}
            for client in clients:
                if client.city:
                    city_groups.setdefault(client.city, []).append(client.name)
            for city, names in city_groups.items():
                for i in range(len(names)):
                    for j in range(i + 1, len(names)):
                        G.add_edge(names[i], names[j], relation=city)
        else:
            # Связываем по общим товарам
            client_products: Dict[str, set] = {}
            for order in orders:
                name = order.client.name
                products = {item.name for item in order.items}
                if name in client_products:
                    client_products[name].update(products)
                else:
                    client_products[name] = products

            names = list(client_products.keys())
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    common = client_products[names[i]] & client_products[names[j]]
                    if common:
                        G.add_edge(names[i], names[j], relation=", ".join(common))

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, seed=42)
        nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=800)
        nx.draw_networkx_edges(G, pos, alpha=0.5)
        nx.draw_networkx_labels(G, pos, font_size=9)
        plt.title(f"Граф связей клиентов (по {'городу' if by == 'city' else 'общим товарам'})")
        plt.axis("off")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
        plt.show()
    except Exception as e:
        print(f"Ошибка построения графа: {e}")


def create_summary_dataframe(orders: List[Order]) -> pd.DataFrame:
    """
    Создаёт сводный DataFrame по заказам.

    Parameters
    ----------
    orders : list of Order
        Список заказов.

    Returns
    -------
    pandas.DataFrame
        Таблица с данными заказов.
    """
    records = []
    for order in orders:
        records.append({
            "order_id": order.id,
            "client": order.client.name,
            "city": order.client.city,
            "date": order.order_date,
            "total": order.calculate_total(),
            "items_count": len(order.items)
        })
    return pd.DataFrame(records)


def recursive_sum(numbers: List[float], index: int = 0) -> float:
    """
    Рекурсивный подсчёт суммы списка чисел (демонстрация рекурсии).

    Parameters
    ----------
    numbers : list of float
        Список чисел.
    index : int
        Текущий индекс.

    Returns
    -------
    float
        Сумма.
    """
    if index >= len(numbers):
        return 0.0
    return numbers[index] + recursive_sum(numbers, index + 1)