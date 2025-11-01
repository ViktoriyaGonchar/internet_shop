"""Модуль для управления данными интернет-магазина.

Инкапсулирует всю логику работы с данными (товары, заказы).
Использует репозитории для разделения ответственности (SOLID).
"""

from typing import Dict, List, Optional
from models import Product, Order, Cart
from storage import IStorage, JSONStorage
from repositories import ProductRepository, OrderRepository, CartRepository


class DataManager:
    """Класс для управления всеми данными интернет-магазина."""
    
    def __init__(self, storage: Optional[IStorage] = None):
        """
        Инициализирует менеджер данных.
        
        Args:
            storage: Экземпляр хранилища. Если None, создаётся новый JSONStorage
        """
        self.storage = storage or JSONStorage()
        
        # Инициализируем репозитории (Dependency Injection)
        self.product_repo = ProductRepository(self.storage)
        self.order_repo = OrderRepository(self.storage)
        self.cart_repo = CartRepository(self.storage)
        
        self._products: Dict[int, Product] = {}
        self._orders: List[Order] = []
        self._next_product_id = 1
        self._next_order_id = 1
        
        # Загружаем данные при инициализации
        self.load_all_data()
    
    def load_all_data(self) -> None:
        """Загружает все данные из хранилища."""
        self._products = self.product_repo.get_all()
        
        # Определяем следующий ID для товаров
        if self._products:
            self._next_product_id = max(self._products.keys()) + 1
        
        self._orders = self.order_repo.get_all()
        
        # Определяем следующий ID для заказов
        if self._orders:
            self._next_order_id = max(o.id for o in self._orders) + 1
    
    def save_all_data(self) -> None:
        """Сохраняет все данные в хранилище."""
        self.product_repo.save_all(self._products)
        self.order_repo.save_all(self._orders)
    
    # Работа с товарами
    def get_all_products(self) -> Dict[int, Product]:
        """Возвращает все товары."""
        return self._products.copy()
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Возвращает товар по ID."""
        return self._products.get(product_id)
    
    def add_product(self, product: Product) -> Product:
        """
        Добавляет новый товар.
        
        Args:
            product: Товар для добавления (ID будет перезаписан)
            
        Returns:
            Товар с присвоенным ID
        """
        product.id = self._next_product_id
        self._next_product_id += 1
        self._products[product.id] = product
        self.product_repo.save(product)
        return product
    
    def update_product(self, product_id: int, **kwargs) -> Optional[Product]:
        """
        Обновляет товар.
        
        Args:
            product_id: ID товара
            **kwargs: Поля для обновления (name, description, price, in_stock)
            
        Returns:
            Обновлённый товар или None, если товар не найден
        """
        if product_id not in self._products:
            return None
        
        product = self._products[product_id]
        if 'name' in kwargs:
            product.name = kwargs['name']
        if 'description' in kwargs:
            product.description = kwargs['description']
        if 'price' in kwargs:
            product.price = kwargs['price']
        if 'in_stock' in kwargs:
            product.in_stock = kwargs['in_stock']
        
        self.product_repo.save(product)
        return product
    
    def delete_product(self, product_id: int) -> bool:
        """
        Удаляет товар.
        
        Args:
            product_id: ID товара
            
        Returns:
            True если товар удалён, False если не найден
        """
        if product_id in self._products:
            if self.product_repo.delete(product_id):
                del self._products[product_id]
                return True
        return False
    
    # Работа с заказами
    def get_all_orders(self) -> List[Order]:
        """Возвращает все заказы."""
        return self._orders.copy()
    
    def get_order(self, order_id: int) -> Optional[Order]:
        """Возвращает заказ по ID."""
        for order in self._orders:
            if order.id == order_id:
                return order
        return None
    
    def create_order(self, cart: Cart, products: Dict[int, Product]) -> Order:
        """
        Создаёт новый заказ из корзины.
        
        Args:
            cart: Корзина с товарами
            products: Словарь товаров для расчёта суммы
            
        Returns:
            Созданный заказ
        """
        total = cart.calculate_total(products)
        order = Order(
            id=self._next_order_id,
            cart=Cart.from_dict(cart.to_dict()),  # Копируем корзину
            total=total
        )
        self._next_order_id += 1
        self._orders.append(order)
        self.order_repo.save(order)
        return order
    
    # Работа с корзиной (сессия)
    def load_cart(self) -> Cart:
        """Загружает корзину из хранилища."""
        return self.cart_repo.load()
    
    def save_cart(self, cart: Cart) -> None:
        """Сохраняет корзину в хранилище."""
        self.cart_repo.save(cart)
