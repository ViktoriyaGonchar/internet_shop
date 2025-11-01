"""Репозиторий для работы с заказами (Single Responsibility Principle)."""

from typing import List, Optional
from models import Order
from storage import IStorage


class OrderRepository:
    """Репозиторий для работы с заказами."""
    
    def __init__(self, storage: IStorage):
        """
        Инициализирует репозиторий заказов.
        
        Args:
            storage: Реализация интерфейса хранилища
        """
        self.storage = storage
    
    def get_all(self) -> List[Order]:
        """Возвращает все заказы."""
        orders_data = self.storage.load_orders()
        return [Order.from_dict(odata) for odata in orders_data]
    
    def get_by_id(self, order_id: int) -> Optional[Order]:
        """Возвращает заказ по ID."""
        orders = self.get_all()
        for order in orders:
            if order.id == order_id:
                return order
        return None
    
    def save(self, order: Order) -> Order:
        """Сохраняет заказ."""
        orders_data = self.storage.load_orders()
        orders_data.append(order.to_dict())
        self.storage.save_orders(orders_data)
        return order
    
    def save_all(self, orders: List[Order]) -> None:
        """Сохраняет все заказы."""
        orders_data = [o.to_dict() for o in orders]
        self.storage.save_orders(orders_data)

