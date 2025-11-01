"""Модуль для управления данными интернет-магазина.

Инкапсулирует всю логику работы с данными (товары, заказы).
В текущей реализации использует словари и JSON-файлы.
В будущем этот модуль можно легко заменить на реальный API-клиент или ORM-модель.
"""

from typing import Dict, List, Optional
from models import Product, Order, Cart
from storage import JSONStorage


class DataManager:
    """Класс для управления всеми данными интернет-магазина."""
    
    def __init__(self, storage: Optional[JSONStorage] = None):
        """
        Инициализирует менеджер данных.
        
        Args:
            storage: Экземпляр хранилища. Если None, создаётся новый JSONStorage
        """
        self.storage = storage or JSONStorage()
        self._products: Dict[int, Product] = {}
        self._orders: List[Order] = []
        self._next_product_id = 1
        self._next_order_id = 1
        
        # Загружаем данные при инициализации
        self.load_all_data()
    
    def load_all_data(self) -> None:
        """Загружает все данные из хранилища."""
        # Загружаем товары
        products_data = self.storage.load_products()
        self._products = {
            pid: Product.from_dict(pdata) 
            for pid, pdata in products_data.items()
        }
        
        # Определяем следующий ID для товаров
        if self._products:
            self._next_product_id = max(self._products.keys()) + 1
        
        # Загружаем заказы
        orders_data = self.storage.load_orders()
        self._orders = [Order.from_dict(odata) for odata in orders_data]
        
        # Определяем следующий ID для заказов
        if self._orders:
            self._next_order_id = max(o.id for o in self._orders) + 1
    
    def save_all_data(self) -> None:
        """Сохраняет все данные в хранилище."""
        # Сохраняем товары
        products_data = {pid: p.to_dict() for pid, p in self._products.items()}
        self.storage.save_products(products_data)
        
        # Сохраняем заказы
        orders_data = [o.to_dict() for o in self._orders]
        self.storage.save_orders(orders_data)
    
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
        self.save_all_data()
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
        
        self.save_all_data()
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
            del self._products[product_id]
            self.save_all_data()
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
        self.save_all_data()
        return order
    
    # Работа с корзиной (сессия)
    def load_cart(self) -> Cart:
        """Загружает корзину из хранилища."""
        cart_data = self.storage.load_cart()
        return Cart.from_dict(cart_data)
    
    def save_cart(self, cart: Cart) -> None:
        """Сохраняет корзину в хранилище."""
        cart_data = cart.to_dict()
        self.storage.save_cart(cart_data)

