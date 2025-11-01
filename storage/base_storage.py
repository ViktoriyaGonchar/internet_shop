"""Базовые интерфейсы для хранилища (Dependency Inversion Principle)."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class IStorage(ABC):
    """Интерфейс для хранилища данных (Interface Segregation Principle)."""
    
    @abstractmethod
    def load_products(self) -> Dict[int, Dict[str, Any]]:
        """Загружает товары из хранилища."""
        pass
    
    @abstractmethod
    def save_products(self, products: Dict[int, Dict[str, Any]]) -> bool:
        """Сохраняет товары в хранилище."""
        pass
    
    @abstractmethod
    def load_orders(self) -> List[Dict[str, Any]]:
        """Загружает заказы из хранилища."""
        pass
    
    @abstractmethod
    def save_orders(self, orders: List[Dict[str, Any]]) -> bool:
        """Сохраняет заказы в хранилище."""
        pass
    
    @abstractmethod
    def load_cart(self) -> Dict[str, Any]:
        """Загружает корзину из хранилища."""
        pass
    
    @abstractmethod
    def save_cart(self, cart_data: Dict[str, Any]) -> bool:
        """Сохраняет корзину в хранилище."""
        pass

