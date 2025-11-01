"""Модель корзины покупок."""

from typing import Dict
from dataclasses import dataclass, field
from .product import Product


@dataclass
class Cart:
    """Класс для представления корзины покупок."""
    
    items: Dict[int, int] = field(default_factory=dict)  # product_id -> quantity
    
    def add_item(self, product_id: int, quantity: int = 1) -> None:
        """Добавляет товар в корзину."""
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")
        
        if product_id in self.items:
            self.items[product_id] += quantity
        else:
            self.items[product_id] = quantity
    
    def remove_item(self, product_id: int, quantity: int = 1) -> None:
        """Удаляет товар из корзины или уменьшает его количество."""
        if product_id not in self.items:
            raise ValueError("Товар не найден в корзине")
        
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")
        
        if self.items[product_id] <= quantity:
            del self.items[product_id]
        else:
            self.items[product_id] -= quantity
    
    def clear(self) -> None:
        """Очищает корзину."""
        self.items.clear()
    
    def calculate_total(self, products: Dict[int, Product]) -> float:
        """Вычисляет общую стоимость корзины."""
        total = 0.0
        for product_id, quantity in self.items.items():
            if product_id in products:
                total += products[product_id].price * quantity
        return total
    
    def get_items_count(self) -> int:
        """Возвращает общее количество товаров в корзине."""
        return sum(self.items.values())
    
    def to_dict(self) -> dict:
        """Преобразует объект Cart в словарь."""
        return {'items': self.items.copy()}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Cart':
        """Создаёт объект Cart из словаря."""
        cart = cls()
        cart.items = data.get('items', {}).copy()
        return cart
    
    def __len__(self) -> int:
        """Возвращает количество позиций в корзине."""
        return len(self.items)
