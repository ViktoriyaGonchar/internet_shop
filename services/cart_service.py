"""Сервис для работы с корзиной покупок."""

from typing import Dict
from models import Cart, Product


class CartService:
    """Сервис для работы с корзиной покупок."""
    
    def __init__(self, cart: Cart, products: Dict[int, Product]):
        """
        Инициализирует сервис корзины.
        
        Args:
            cart: Экземпляр корзины
            products: Словарь доступных товаров (id -> Product)
        """
        self.cart = cart
        self.products = products
    
    def add_product(self, product_id: int, quantity: int = 1) -> bool:
        """
        Добавляет товар в корзину.
        
        Args:
            product_id: ID товара
            quantity: Количество
            
        Returns:
            True если товар добавлен, False если товар не найден или нет в наличии
        """
        if product_id not in self.products:
            return False
        
        product = self.products[product_id]
        if not product.in_stock:
            return False
        
        try:
            self.cart.add_item(product_id, quantity)
            return True
        except ValueError:
            return False
    
    def remove_product(self, product_id: int, quantity: int = 1) -> bool:
        """
        Удаляет товар из корзины или уменьшает его количество.
        
        Args:
            product_id: ID товара
            quantity: Количество для удаления
            
        Returns:
            True если операция успешна, False в противном случае
        """
        try:
            self.cart.remove_item(product_id, quantity)
            return True
        except ValueError:
            return False
    
    def clear_cart(self) -> None:
        """Очищает корзину."""
        self.cart.clear()
    
    def get_total(self) -> float:
        """Возвращает общую стоимость корзины."""
        return self.cart.calculate_total(self.products)
    
    def get_items_count(self) -> int:
        """Возвращает общее количество товаров в корзине."""
        return self.cart.get_items_count()
    
    def get_cart_items(self) -> Dict[int, Dict]:
        """
        Возвращает список товаров в корзине с деталями.
        
        Returns:
            Словарь {product_id: {'product': Product, 'quantity': int}}
        """
        items = {}
        for product_id, quantity in self.cart.items.items():
            if product_id in self.products:
                items[product_id] = {
                    'product': self.products[product_id],
                    'quantity': quantity
                }
        return items

