"""Пользовательский интерфейс для публичной части магазина."""

from typing import Optional
from models import Cart
from services import CartService, ProductService
from data_manager import DataManager


class PublicUI:
    """Пользовательский интерфейс для клиентов магазина."""
    
    def __init__(self, data_manager: DataManager):
        """
        Инициализирует публичный интерфейс.
        
        Args:
            data_manager: Менеджер данных
        """
        self.data_manager = data_manager
        self.cart = data_manager.load_cart()
        self.products = data_manager.get_all_products()
        
        self.cart_service = CartService(self.cart, self.products)
        self.product_service = ProductService(self.products)
    
    def show_menu(self) -> None:
        """Отображает главное меню."""
        while True:
            print("\n" + "="*50)
            print("🛒 ИНТЕРНЕТ-МАГАЗИН SHOP SHIPS")
            print("="*50)
            print("1. Просмотр каталога товаров")
            print("2. Поиск товаров")
            print("3. Корзина")
            print("4. Оформить заказ")
            print("0. Выход")
            print("="*50)
            
            choice = input("Выберите пункт меню: ").strip()
            
            if choice == "1":
                self.show_catalog()
            elif choice == "2":
                self.search_products()
            elif choice == "3":
                self.show_cart()
            elif choice == "4":
                self.create_order()
            elif choice == "0":
                self.save_and_exit()
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
    
    def show_catalog(self) -> None:
        """Отображает каталог товаров."""
        products = self.product_service.get_available_products()
        
        if not products:
            print("\n📦 Каталог пуст. Товары временно отсутствуют.")
            return
        
        print("\n" + "="*70)
        print("📦 КАТАЛОГ ТОВАРОВ")
        print("="*70)
        
        for product in products:
            print(f"\n{product}")
            print(f"   Описание: {product.description}")
        
        print("\n" + "="*70)
        
        while True:
            print("\nВыберите действие:")
            print("1. Добавить товар в корзину")
            print("2. Вернуться в главное меню")
            
            choice = input("Ваш выбор: ").strip()
            
            if choice == "1":
                self.add_to_cart_interactive()
            elif choice == "2":
                break
            else:
                print("❌ Неверный выбор.")
    
    def search_products(self) -> None:
        """Поиск товаров."""
        query = input("\n🔍 Введите поисковый запрос: ").strip()
        
        if not query:
            print("❌ Поисковый запрос не может быть пустым.")
            return
        
        results = self.product_service.search_products(query)
        
        if not results:
            print(f"\n❌ По запросу '{query}' ничего не найдено.")
            return
        
        print(f"\n🔍 Результаты поиска по запросу '{query}':")
        print("="*70)
        
        for product in results:
            print(f"\n{product}")
            print(f"   Описание: {product.description}")
        
        print("\n" + "="*70)
    
    def add_to_cart_interactive(self) -> None:
        """Интерактивное добавление товара в корзину."""
        try:
            product_id = int(input("\nВведите ID товара: ").strip())
        except ValueError:
            print("❌ Неверный ID товара.")
            return
        
        product = self.product_service.get_product(product_id)
        
        if not product:
            print("❌ Товар с таким ID не найден.")
            return
        
        if not product.in_stock:
            print("❌ Этот товар сейчас недоступен.")
            return
        
        try:
            quantity = int(input("Введите количество: ").strip())
            if quantity <= 0:
                print("❌ Количество должно быть больше нуля.")
                return
        except ValueError:
            print("❌ Неверное количество.")
            return
        
        if self.cart_service.add_product(product_id, quantity):
            print(f"✅ Товар '{product.name}' добавлен в корзину ({quantity} шт.)")
            self.data_manager.save_cart(self.cart)
        else:
            print("❌ Не удалось добавить товар в корзину.")
    
    def show_cart(self) -> None:
        """Отображает содержимое корзины."""
        items = self.cart_service.get_cart_items()
        
        if not items:
            print("\n🛒 Корзина пуста.")
            return
        
        print("\n" + "="*70)
        print("🛒 КОРЗИНА")
        print("="*70)
        
        total = 0.0
        for product_id, item_data in items.items():
            product = item_data['product']
            quantity = item_data['quantity']
            subtotal = product.price * quantity
            total += subtotal
            
            print(f"\n[{product.id}] {product.name}")
            print(f"   Цена: {product.price:.2f} ₽")
            print(f"   Количество: {quantity}")
            print(f"   Сумма: {subtotal:.2f} ₽")
        
        print("\n" + "-"*70)
        print(f"ИТОГО: {total:.2f} ₽")
        print("="*70)
        
        while True:
            print("\nВыберите действие:")
            print("1. Изменить количество товара")
            print("2. Удалить товар")
            print("3. Очистить корзину")
            print("4. Вернуться в главное меню")
            
            choice = input("Ваш выбор: ").strip()
            
            if choice == "1":
                self.update_cart_item()
            elif choice == "2":
                self.remove_from_cart()
            elif choice == "3":
                self.clear_cart()
            elif choice == "4":
                break
            else:
                print("❌ Неверный выбор.")
    
    def update_cart_item(self) -> None:
        """Изменяет количество товара в корзине."""
        try:
            product_id = int(input("\nВведите ID товара: ").strip())
        except ValueError:
            print("❌ Неверный ID товара.")
            return
        
        if product_id not in self.cart.items:
            print("❌ Товар не найден в корзине.")
            return
        
        try:
            new_quantity = int(input("Введите новое количество: ").strip())
            if new_quantity <= 0:
                print("❌ Количество должно быть больше нуля.")
                return
        except ValueError:
            print("❌ Неверное количество.")
            return
        
        current_quantity = self.cart.items[product_id]
        difference = new_quantity - current_quantity
        
        if difference > 0:
            self.cart_service.add_product(product_id, difference)
        elif difference < 0:
            self.cart_service.remove_product(product_id, -difference)
        
        self.data_manager.save_cart(self.cart)
        print("✅ Корзина обновлена.")
    
    def remove_from_cart(self) -> None:
        """Удаляет товар из корзины."""
        try:
            product_id = int(input("\nВведите ID товара для удаления: ").strip())
        except ValueError:
            print("❌ Неверный ID товара.")
            return
        
        if product_id not in self.cart.items:
            print("❌ Товар не найден в корзине.")
            return
        
        if self.cart_service.remove_product(product_id, self.cart.items[product_id]):
            print("✅ Товар удалён из корзины.")
            self.data_manager.save_cart(self.cart)
        else:
            print("❌ Не удалось удалить товар.")
    
    def clear_cart(self) -> None:
        """Очищает корзину."""
        confirm = input("\n⚠️ Вы уверены, что хотите очистить корзину? (да/нет): ").strip().lower()
        if confirm == "да":
            self.cart_service.clear_cart()
            self.data_manager.save_cart(self.cart)
            print("✅ Корзина очищена.")
        else:
            print("❌ Операция отменена.")
    
    def create_order(self) -> None:
        """Оформляет заказ."""
        if not self.cart.items:
            print("\n❌ Корзина пуста. Добавьте товары перед оформлением заказа.")
            return
        
        items = self.cart_service.get_cart_items()
        total = self.cart_service.get_total()
        
        print("\n" + "="*70)
        print("📋 ОФОРМЛЕНИЕ ЗАКАЗА")
        print("="*70)
        
        for product_id, item_data in items.items():
            product = item_data['product']
            quantity = item_data['quantity']
            print(f"{product.name} x{quantity} = {product.price * quantity:.2f} ₽")
        
        print("-"*70)
        print(f"ИТОГО: {total:.2f} ₽")
        print("="*70)
        
        confirm = input("\nПодтвердите оформление заказа (да/нет): ").strip().lower()
        
        if confirm == "да":
            order = self.data_manager.create_order(self.cart, self.products)
            self.cart_service.clear_cart()
            self.data_manager.save_cart(self.cart)
            print(f"\n✅ Заказ #{order.id} успешно оформлен!")
            print(f"📅 Дата: {order.created_at}")
            print(f"💰 Сумма: {order.total:.2f} ₽")
        else:
            print("❌ Оформление заказа отменено.")
    
    def save_and_exit(self) -> None:
        """Сохраняет корзину и выходит."""
        self.data_manager.save_cart(self.cart)
        print("\n👋 До свидания! Корзина сохранена.")

