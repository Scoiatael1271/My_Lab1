"""
Точка входа в программу — система учёта заказов интернет-магазина.

Запуск:
    python main.py
"""

from gui import OrderManagementApp


if __name__ == "__main__":
    app = OrderManagementApp()
    app.mainloop()