"""Сервис для работы с товарами."""

from typing import Dict, List
from models import Product


class ProductService:
    """Сервис для работы с товарами."""
    
    def __init__(self, products: Dict[int, Product]):
        """
        Инициализирует сервис товаров.
        
        Args:
            products: Словарь товаров (id -> Product)
        """
        self.products = products
    
    def get_all_products(self) -> List[Product]:
        """Возвращает все товары."""
        return list(self.products.values())
    
    def get_available_products(self) -> List[Product]:
        """Возвращает только товары в наличии."""
        return [p for p in self.products.values() if p.in_stock]
    
    def get_product(self, product_id: int) -> Product:
        """
        Возвращает товар по ID.
        
        Args:
            product_id: ID товара
            
        Returns:
            Товар или None если не найден
        """
        return self.products.get(product_id)
    
    def search_products(self, query: str) -> List[Product]:
        """
        Ищет товары по названию или описанию.
        
        Args:
            query: Поисковый запрос
            
        Returns:
            Список найденных товаров
        """
        query_lower = query.lower()
        results = []
        for product in self.products.values():
            if (query_lower in product.name.lower() or 
                query_lower in product.description.lower()):
                results.append(product)
        return results

