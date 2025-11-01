"""Репозиторий для работы с товарами (Single Responsibility Principle)."""

from typing import Dict, Optional
from models import Product
from storage import IStorage


class ProductRepository:
    """Репозиторий для работы с товарами."""
    
    def __init__(self, storage: IStorage):
        """
        Инициализирует репозиторий товаров.
        
        Args:
            storage: Реализация интерфейса хранилища
        """
        self.storage = storage
    
    def get_all(self) -> Dict[int, Product]:
        """Возвращает все товары."""
        products_data = self.storage.load_products()
        return {
            pid: Product.from_dict(pdata)
            for pid, pdata in products_data.items()
        }
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Возвращает товар по ID."""
        products_data = self.storage.load_products()
        if product_id not in products_data:
            return None
        return Product.from_dict(products_data[product_id])
    
    def save(self, product: Product) -> Product:
        """Сохраняет товар."""
        products_data = self.storage.load_products()
        products_data[product.id] = product.to_dict()
        self.storage.save_products(products_data)
        return product
    
    def save_all(self, products: Dict[int, Product]) -> None:
        """Сохраняет все товары."""
        products_data = {pid: p.to_dict() for pid, p in products.items()}
        self.storage.save_products(products_data)
    
    def delete(self, product_id: int) -> bool:
        """Удаляет товар."""
        products_data = self.storage.load_products()
        if product_id not in products_data:
            return False
        del products_data[product_id]
        return self.storage.save_products(products_data)

