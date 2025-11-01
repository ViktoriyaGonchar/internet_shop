"""Модель заказа."""

from typing import Dict
from dataclasses import dataclass, field
from datetime import datetime
from .cart import Cart


@dataclass
class Order:
    """Класс для представления заказа."""
    
    id: int
    cart: Cart
    total: float
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Преобразует объект Order в словарь."""
        return {
            'id': self.id,
            'cart': self.cart.to_dict(),
            'total': self.total,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Order':
        """Создаёт объект Order из словаря."""
        cart = Cart.from_dict(data['cart'])
        return cls(
            id=data['id'],
            cart=cart,
            total=data['total'],
            created_at=data.get('created_at', datetime.now().isoformat())
        )
    
    def __str__(self) -> str:
        """Строковое представление заказа."""
        date = datetime.fromisoformat(self.created_at).strftime('%Y-%m-%d %H:%M:%S')
        return f"Заказ #{self.id} от {date} | Сумма: {self.total:.2f} ₽ | Товаров: {len(self.cart.items)}"
