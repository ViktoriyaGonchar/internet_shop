"""Сервис для работы с заказами."""

from typing import List, Optional
from models import Order


class OrderService:
    """Сервис для работы с заказами."""
    
    def __init__(self, orders: List[Order]):
        """
        Инициализирует сервис заказов.
        
        Args:
            orders: Список заказов
        """
        self.orders = orders
    
    def get_all_orders(self) -> List[Order]:
        """Возвращает все заказы."""
        return self.orders.copy()
    
    def get_order(self, order_id: int) -> Optional[Order]:
        """
        Возвращает заказ по ID.
        
        Args:
            order_id: ID заказа
            
        Returns:
            Заказ или None если не найден
        """
        for order in self.orders:
            if order.id == order_id:
                return order
        return None
    
    def get_orders_count(self) -> int:
        """Возвращает общее количество заказов."""
        return len(self.orders)
    
    def get_total_revenue(self) -> float:
        """Возвращает общую выручку от всех заказов."""
        return sum(order.total for order in self.orders)

