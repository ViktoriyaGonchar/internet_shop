"""Базовые классы для сервисов (DRY принцип)."""

from typing import Dict
from models import Product


class BaseService:
    """Базовый класс для сервисов с общими методами."""
    
    def __init__(self, products: Dict[int, Product]):
        """
        Инициализирует базовый сервис.
        
        Args:
            products: Словарь товаров
        """
        self.products = products
    
    def _validate_product_exists(self, product_id: int) -> bool:
        """
        Валидирует существование товара.
        
        Args:
            product_id: ID товара
            
        Returns:
            True если товар существует
        """
        return product_id in self.products
    
    def _validate_product_available(self, product_id: int) -> bool:
        """
        Валидирует доступность товара.
        
        Args:
            product_id: ID товара
            
        Returns:
            True если товар доступен
        """
        if not self._validate_product_exists(product_id):
            return False
        return self.products[product_id].in_stock

