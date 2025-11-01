"""Репозиторий для работы с корзиной (Single Responsibility Principle)."""

from models import Cart
from storage import IStorage


class CartRepository:
    """Репозиторий для работы с корзиной."""
    
    def __init__(self, storage: IStorage):
        """
        Инициализирует репозиторий корзины.
        
        Args:
            storage: Реализация интерфейса хранилища
        """
        self.storage = storage
    
    def load(self) -> Cart:
        """Загружает корзину из хранилища."""
        cart_data = self.storage.load_cart()
        return Cart.from_dict(cart_data)
    
    def save(self, cart: Cart) -> None:
        """Сохраняет корзину в хранилище."""
        cart_data = cart.to_dict()
        self.storage.save_cart(cart_data)

