"""
Модуль gui.py — графический интерфейс приложения на tkinter.

Позволяет добавлять клиентов, товары, создавать заказы,
просматривать данные и запускать анализ.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional
from datetime import datetime

from models import Client, Product, Order, OrderItem
from db import DataBase
from analysis import (
    plot_top_clients,
    plot_orders_dynamics,
    sort_orders_by_date,
    sort_orders_by_cost,
    get_top_clients,
    create_summary_dataframe
)


class OrderManagementApp:
    """
    Главное окно приложения учёта заказов.

    Attributes
    ----------
    root : tk.Tk
        Корневое окно.
    db : DataBase
        Объект базы данных.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Система учёта заказов интернет-магазина")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)

        self.db = DataBase(data_dir="data")

        self._create_widgets()
        self._refresh_all()

    def _create_widgets(self) -> None:
        """Создаёт все элементы интерфейса."""
        # --- Notebook (вкладки) ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Вкладки
        self.tab_clients = ttk.Frame(self.notebook)
        self.tab_products = ttk.Frame(self.notebook)
        self.tab_orders = ttk.Frame(self.notebook)
        self.tab_analysis = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_clients, text="Клиенты")
        self.notebook.add(self.tab_products, text="Товары")
        self.notebook.add(self.tab_orders, text="Заказы")
        self.notebook.add(self.tab_analysis, text="Анализ данных")

        self._build_clients_tab()
        self._build_products_tab()
        self._build_orders_tab()
        self._build_analysis_tab()

        # Строка статуса
        self.status_var = tk.StringVar(value="Готово")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ==================== ВКЛАДКА КЛИЕНТЫ ====================
    def _build_clients_tab(self) -> None:
        """Строит интерфейс вкладки клиентов."""
        # Форма добавления
        form_frame = ttk.LabelFrame(self.tab_clients, text="Добавить клиента", padding=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(form_frame, text="ФИО:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.client_name_entry = ttk.Entry(form_frame, width=30)
        self.client_name_entry.grid(row=0, column=1, padx=5, pady=3)

        ttk.Label(form_frame, text="Email:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=3)
        self.client_email_entry = ttk.Entry(form_frame, width=25)
        self.client_email_entry.grid(row=0, column=3, padx=5, pady=3)

        ttk.Label(form_frame, text="Телефон:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.client_phone_entry = ttk.Entry(form_frame, width=30)
        self.client_phone_entry.grid(row=1, column=1, padx=5, pady=3)

        ttk.Label(form_frame, text="Город:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=3)
        self.client_city_entry = ttk.Entry(form_frame, width=25)
        self.client_city_entry.grid(row=1, column=3, padx=5, pady=3)

        ttk.Button(form_frame, text="Добавить клиента", command=self._add_client).grid(
            row=2, column=0, columnspan=4, pady=8
        )

        # Список клиентов
        list_frame = ttk.LabelFrame(self.tab_clients, text="Список клиентов", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("id", "name", "email", "phone", "city")
        self.clients_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        self.clients_tree.heading("id", text="ID")
        self.clients_tree.heading("name", text="ФИО")
        self.clients_tree.heading("email", text="Email")
        self.clients_tree.heading("phone", text="Телефон")
        self.clients_tree.heading("city", text="Город")
        self.clients_tree.column("id", width=40)
        self.clients_tree.column("name", width=180)
        self.clients_tree.column("email", width=180)
        self.clients_tree.column("phone", width=130)
        self.clients_tree.column("city", width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)
        self.clients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки экспорта/импорта
        btn_frame = ttk.Frame(self.tab_clients)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Экспорт CSV", command=self._export_clients_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Импорт CSV", command=self._import_clients_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self._refresh_clients).pack(side=tk.LEFT, padx=5)

    def _add_client(self) -> None:
        """Добавляет нового клиента."""
        try:
            name = self.client_name_entry.get().strip()
            email = self.client_email_entry.get().strip()
            phone = self.client_phone_entry.get().strip()
            city = self.client_city_entry.get().strip()

            if not name:
                messagebox.showwarning("Ошибка", "Введите ФИО клиента")
                return

            client_id = self.db.get_next_client_id()
            client = Client(client_id, name, email, phone, city)
            self.db.add_client(client)

            self.client_name_entry.delete(0, tk.END)
            self.client_email_entry.delete(0, tk.END)
            self.client_phone_entry.delete(0, tk.END)
            self.client_city_entry.delete(0, tk.END)

            self._refresh_clients()
            self.status_var.set(f"Клиент «{name}» добавлен")
            messagebox.showinfo("Успех", f"Клиент «{name}» успешно добавлен")
        except ValueError as e:
            messagebox.showerror("Ошибка валидации", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить клиента:\n{e}")

    def _refresh_clients(self) -> None:
        """Обновляет список клиентов."""
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)
        for client in self.db.load_clients():
            self.clients_tree.insert("", tk.END, values=(
                client.id, client.name, client.email, client.phone, client.city
            ))

    def _export_clients_csv(self) -> None:
        """Экспортирует клиентов в CSV."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if filepath:
            if self.db.export_clients_csv(filepath):
                messagebox.showinfo("Успех", f"Данные экспортированы в\n{filepath}")
            else:
                messagebox.showerror("Ошибка", "Не удалось экспортировать данные")

    def _import_clients_csv(self) -> None:
        """Импортирует клиентов из CSV."""
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filepath:
            if self.db.import_clients_csv(filepath):
                self._refresh_clients()
                messagebox.showinfo("Успех", "Данные импортированы")
            else:
                messagebox.showerror("Ошибка", "Не удалось импортировать данные")

    # ==================== ВКЛАДКА ТОВАРЫ ====================
    def _build_products_tab(self) -> None:
        """Строит интерфейс вкладки товаров."""
        form_frame = ttk.LabelFrame(self.tab_products, text="Добавить товар", padding=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.product_name_entry = ttk.Entry(form_frame, width=30)
        self.product_name_entry.grid(row=0, column=1, padx=5, pady=3)

        ttk.Label(form_frame, text="Цена:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=3)
        self.product_price_entry = ttk.Entry(form_frame, width=15)
        self.product_price_entry.grid(row=0, column=3, padx=5, pady=3)

        ttk.Label(form_frame, text="Категория:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.product_category_entry = ttk.Entry(form_frame, width=30)
        self.product_category_entry.grid(row=1, column=1, padx=5, pady=3)
        self.product_category_entry.insert(0, "Общее")

        ttk.Button(form_frame, text="Добавить товар", command=self._add_product).grid(
            row=2, column=0, columnspan=4, pady=8
        )

        list_frame = ttk.LabelFrame(self.tab_products, text="Список товаров", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("id", "name", "price", "category")
        self.products_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        self.products_tree.heading("id", text="ID")
        self.products_tree.heading("name", text="Название")
        self.products_tree.heading("price", text="Цена")
        self.products_tree.heading("category", text="Категория")
        self.products_tree.column("id", width=40)
        self.products_tree.column("name", width=250)
        self.products_tree.column("price", width=100)
        self.products_tree.column("category", width=150)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(self.tab_products, text="Обновить", command=self._refresh_products).pack(pady=5)

    def _add_product(self) -> None:
        """Добавляет новый товар."""
        try:
            name = self.product_name_entry.get().strip()
            price_str = self.product_price_entry.get().strip()
            category = self.product_category_entry.get().strip() or "Общее"

            if not name:
                messagebox.showwarning("Ошибка", "Введите название товара")
                return
            if not price_str:
                messagebox.showwarning("Ошибка", "Введите цену товара")
                return

            price = float(price_str)
            product_id = self.db.get_next_product_id()
            product = Product(product_id, name, price, category)
            self.db.add_product(product)

            self.product_name_entry.delete(0, tk.END)
            self.product_price_entry.delete(0, tk.END)

            self._refresh_products()
            self.status_var.set(f"Товар «{name}» добавлен")
            messagebox.showinfo("Успех", f"Товар «{name}» успешно добавлен")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить товар:\n{e}")

    def _refresh_products(self) -> None:
        """Обновляет список товаров."""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        for product in self.db.load_products():
            self.products_tree.insert("", tk.END, values=(
                product.id, product.name, f"{product.price:.2f}", product.category
            ))

    # ==================== ВКЛАДКА ЗАКАЗЫ ====================
    def _build_orders_tab(self) -> None:
        """Строит интерфейс вкладки заказов."""
        form_frame = ttk.LabelFrame(self.tab_orders, text="Создать заказ", padding=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(form_frame, text="Клиент:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.order_client_combo = ttk.Combobox(form_frame, width=30, state="readonly")
        self.order_client_combo.grid(row=0, column=1, padx=5, pady=3)

        ttk.Label(form_frame, text="Товар:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=3)
        self.order_product_combo = ttk.Combobox(form_frame, width=25, state="readonly")
        self.order_product_combo.grid(row=0, column=3, padx=5, pady=3)

        ttk.Label(form_frame, text="Количество:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.order_qty_entry = ttk.Entry(form_frame, width=10)
        self.order_qty_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=3)
        self.order_qty_entry.insert(0, "1")

        ttk.Label(form_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=1, column=2, sticky=tk.W, padx=5, pady=3)
        self.order_date_entry = ttk.Entry(form_frame, width=15)
        self.order_date_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=3)
        self.order_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Button(form_frame, text="Создать заказ", command=self._add_order).grid(
            row=2, column=0, columnspan=4, pady=8
        )

        # Фильтры и сортировка
        filter_frame = ttk.Frame(self.tab_orders)
        filter_frame.pack(fill=tk.X, padx=10, pady=3)
        ttk.Label(filter_frame, text="Сортировка:").pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="По дате ↑", command=lambda: self._sort_orders("date", False)).pack(side=tk.LEFT, padx=2)
        ttk.Button(filter_frame, text="По дате ↓", command=lambda: self._sort_orders("date", True)).pack(side=tk.LEFT, padx=2)
        ttk.Button(filter_frame, text="По сумме ↓", command=lambda: self._sort_orders("cost", True)).pack(side=tk.LEFT, padx=2)
        ttk.Button(filter_frame, text="По сумме ↑", command=lambda: self._sort_orders("cost", False)).pack(side=tk.LEFT, padx=2)

        list_frame = ttk.LabelFrame(self.tab_orders, text="Список заказов", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("id", "client", "date", "items", "total")
        self.orders_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.orders_tree.heading("id", text="ID")
        self.orders_tree.heading("client", text="Клиент")
        self.orders_tree.heading("date", text="Дата")
        self.orders_tree.heading("items", text="Товары")
        self.orders_tree.heading("total", text="Сумма")
        self.orders_tree.column("id", width=40)
        self.orders_tree.column("client", width=150)
        self.orders_tree.column("date", width=100)
        self.orders_tree.column("items", width=250)
        self.orders_tree.column("total", width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        self.orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = ttk.Frame(self.tab_orders)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Обновить", command=self._refresh_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Экспорт заказов CSV", command=self._export_orders_csv).pack(side=tk.LEFT, padx=5)

    def _refresh_order_combos(self) -> None:
        """Обновляет выпадающие списки клиентов и товаров."""
        clients = self.db.load_clients()
        self.order_client_combo["values"] = [f"{c.id}: {c.name}" for c in clients]
        products = self.db.load_products()
        self.order_product_combo["values"] = [f"{p.id}: {p.name} ({p.price:.2f} руб.)" for p in products]

    def _add_order(self) -> None:
        """Создаёт новый заказ."""
        try:
            client_str = self.order_client_combo.get()
            product_str = self.order_product_combo.get()
            qty_str = self.order_qty_entry.get().strip()
            date_str = self.order_date_entry.get().strip()

            if not client_str or not product_str:
                messagebox.showwarning("Ошибка", "Выберите клиента и товар")
                return

            client_id = int(client_str.split(":")[0])
            product_id = int(product_str.split(":")[0])
            quantity = int(qty_str) if qty_str else 1

            clients = {c.id: c for c in self.db.load_clients()}
            products = {p.id: p for p in self.db.load_products()}

            client = clients.get(client_id)
            product = products.get(product_id)

            if not client or not product:
                messagebox.showerror("Ошибка", "Клиент или товар не найден")
                return

            order_id = self.db.get_next_order_id()
            item = OrderItem(product, quantity)
            order = Order(order_id, client, [item], date_str)
            self.db.add_order(order)

            self.order_qty_entry.delete(0, tk.END)
            self.order_qty_entry.insert(0, "1")

            self._refresh_orders()
            self.status_var.set(f"Заказ #{order_id} создан")
            messagebox.showinfo("Успех", f"Заказ #{order_id} успешно создан\nСумма: {order.calculate_total():.2f} руб.")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать заказ:\n{e}")

    def _refresh_orders(self, orders: Optional[List[Order]] = None) -> None:
        """Обновляет список заказов."""
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        if orders is None:
            orders = self.db.load_orders()
        for order in orders:
            items_str = ", ".join(f"{i.name} x{i.quantity}" for i in order.items)
            self.orders_tree.insert("", tk.END, values=(
                order.id,
                order.client.name,
                order.order_date,
                items_str,
                f"{order.calculate_total():.2f}"
            ))
        self._refresh_order_combos()

    def _sort_orders(self, by: str, reverse: bool) -> None:
        """Сортирует заказы и обновляет список."""
        orders = self.db.load_orders()
        if by == "date":
            sorted_orders = sort_orders_by_date(orders, reverse)
        else:
            sorted_orders = sort_orders_by_cost(orders, reverse)
        self._refresh_orders(sorted_orders)
        self.status_var.set(f"Заказы отсортированы по {'дате' if by == 'date' else 'сумме'}")

    def _export_orders_csv(self) -> None:
        """Экспортирует заказы в CSV."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if filepath:
            if self.db.export_orders_csv(filepath):
                messagebox.showinfo("Успех", f"Заказы экспортированы в\n{filepath}")
            else:
                messagebox.showerror("Ошибка", "Не удалось экспортировать")

    # ==================== ВКЛАДКА АНАЛИЗ ====================
    def _build_analysis_tab(self) -> None:
        """Строит интерфейс вкладки анализа."""
        info_frame = ttk.LabelFrame(self.tab_analysis, text="Анализ данных", padding=15)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(
            info_frame,
            text="Выберите вид анализа и нажмите кнопку.\nГрафики откроются в отдельном окне.",
            font=("Arial", 11)
        ).pack(pady=10)

        btn_frame = ttk.Frame(info_frame)
        btn_frame.pack(pady=20)

        ttk.Button(
            btn_frame,
            text="Топ-5 клиентов по заказам",
            command=self._show_top_clients,
            width=35
        ).pack(pady=8)

        ttk.Button(
            btn_frame,
            text="Динамика заказов по датам",
            command=self._show_orders_dynamics,
            width=35
        ).pack(pady=8)

        ttk.Button(
            btn_frame,
            text="Показать сводную таблицу",
            command=self._show_summary,
            width=35
        ).pack(pady=8)

        # Текстовая область для результатов
        self.analysis_text = tk.Text(info_frame, height=10, width=70, state=tk.DISABLED)
        self.analysis_text.pack(pady=10, fill=tk.BOTH, expand=True)

    def _show_top_clients(self) -> None:
        """Показывает топ клиентов и строит график."""
        try:
            orders = self.db.load_orders()
            if not orders:
                messagebox.showinfo("Информация", "Нет заказов для анализа")
                return
            top = get_top_clients(orders, 5)
            text = "Топ-5 клиентов по числу заказов:\n\n"
            for i, (name, count) in enumerate(top, 1):
                text += f"{i}. {name} — {count} заказ(ов)\n"
            self._set_analysis_text(text)
            plot_top_clients(orders, 5)
            self.status_var.set("Анализ: топ клиентов")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _show_orders_dynamics(self) -> None:
        """Показывает динамику заказов."""
        try:
            orders = self.db.load_orders()
            if not orders:
                messagebox.showinfo("Информация", "Нет заказов для анализа")
                return
            plot_orders_dynamics(orders)
            self.status_var.set("Анализ: динамика заказов")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _show_summary(self) -> None:
        """Показывает сводную таблицу в текстовом поле."""
        try:
            orders = self.db.load_orders()
            if not orders:
                messagebox.showinfo("Информация", "Нет заказов")
                return
            df = create_summary_dataframe(orders)
            self._set_analysis_text(df.to_string(index=False))
            self.status_var.set("Сводная таблица загружена")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _set_analysis_text(self, text: str) -> None:
        """Устанавливает текст в область анализа."""
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.insert(tk.END, text)
        self.analysis_text.config(state=tk.DISABLED)

    # ==================== ОБЩЕЕ ====================
    def _refresh_all(self) -> None:
        """Обновляет все списки."""
        self._refresh_clients()
        self._refresh_products()
        self._refresh_orders()

    def mainloop(self) -> None:
        """Запускает главный цикл приложения."""
        self.root.mainloop()