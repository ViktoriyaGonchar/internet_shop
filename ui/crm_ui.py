"""Пользовательский интерфейс для CRM (админ-панель)."""

from typing import Optional
from models import Product
from services import ProductService, OrderService
from data_manager import DataManager


class CRMUI:
    """Пользовательский интерфейс для администраторов (CRM)."""
    
    def __init__(self, data_manager: DataManager):
        """
        Инициализирует CRM интерфейс.
        
        Args:
            data_manager: Менеджер данных
        """
        self.data_manager = data_manager
        self.products = data_manager.get_all_products()
        self.orders = data_manager.get_all_orders()
        
        self.product_service = ProductService(self.products)
        self.order_service = OrderService(self.orders)
    
    def show_menu(self) -> None:
        """Отображает главное меню CRM."""
        while True:
            print("\n" + "="*50)
            print("⚙️ CRM - УПРАВЛЕНИЕ МАГАЗИНОМ")
            print("="*50)
            print("1. Управление товарами")
            print("2. Просмотр заказов")
            print("3. Статистика")
            print("0. Выход")
            print("="*50)
            
            choice = input("Выберите пункт меню: ").strip()
            
            if choice == "1":
                self.manage_products()
            elif choice == "2":
                self.show_orders()
            elif choice == "3":
                self.show_statistics()
            elif choice == "0":
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
    
    def manage_products(self) -> None:
        """Меню управления товарами."""
        while True:
            print("\n" + "="*50)
            print("📦 УПРАВЛЕНИЕ ТОВАРАМИ")
            print("="*50)
            print("1. Список всех товаров")
            print("2. Добавить товар")
            print("3. Редактировать товар")
            print("4. Удалить товар")
            print("0. Назад")
            print("="*50)
            
            choice = input("Выберите пункт меню: ").strip()
            
            if choice == "1":
                self.list_products()
            elif choice == "2":
                self.add_product()
            elif choice == "3":
                self.edit_product()
            elif choice == "4":
                self.delete_product()
            elif choice == "0":
                break
            else:
                print("❌ Неверный выбор.")
    
    def list_products(self) -> None:
        """Отображает список всех товаров."""
        products = self.product_service.get_all_products()
        
        if not products:
            print("\n📦 Товары отсутствуют.")
            return
        
        print("\n" + "="*70)
        print("📦 СПИСОК ТОВАРОВ")
        print("="*70)
        
        for product in products:
            print(f"\n{product}")
            print(f"   Описание: {product.description}")
        
        print("\n" + "="*70)
        input("\nНажмите Enter для продолжения...")
    
    def add_product(self) -> None:
        """Добавляет новый товар."""
        print("\n📦 ДОБАВЛЕНИЕ НОВОГО ТОВАРА")
        print("-"*50)
        
        name = input("Название: ").strip()
        if not name:
            print("❌ Название не может быть пустым.")
            return
        
        description = input("Описание: ").strip()
        
        try:
            price = float(input("Цена: ").strip())
            if price < 0:
                print("❌ Цена не может быть отрицательной.")
                return
        except ValueError:
            print("❌ Неверный формат цены.")
            return
        
        in_stock_input = input("В наличии? (да/нет): ").strip().lower()
        in_stock = in_stock_input == "да"
        
        product = Product(
            id=0,  # ID будет присвоен автоматически
            name=name,
            description=description,
            price=price,
            in_stock=in_stock
        )
        
        product = self.data_manager.add_product(product)
        self.products[product.id] = product  # Обновляем локальный кэш
        
        print(f"\n✅ Товар '{product.name}' успешно добавлен (ID: {product.id})")
    
    def edit_product(self) -> None:
        """Редактирует существующий товар."""
        try:
            product_id = int(input("\nВведите ID товара для редактирования: ").strip())
        except ValueError:
            print("❌ Неверный ID товара.")
            return
        
        product = self.product_service.get_product(product_id)
        if not product:
            print("❌ Товар с таким ID не найден.")
            return
        
        print(f"\n📝 РЕДАКТИРОВАНИЕ ТОВАРА: {product.name}")
        print("-"*50)
        print(f"Текущие данные:")
        print(f"  Название: {product.name}")
        print(f"  Описание: {product.description}")
        print(f"  Цена: {product.price:.2f} ₽")
        print(f"  В наличии: {'Да' if product.in_stock else 'Нет'}")
        print("-"*50)
        
        print("\nВведите новые данные (оставьте пустым для сохранения текущего значения):")
        
        name = input(f"Название [{product.name}]: ").strip()
        description = input(f"Описание [{product.description}]: ").strip()
        price_input = input(f"Цена [{product.price:.2f}]: ").strip()
        in_stock_input = input(f"В наличии? (да/нет) [{'да' if product.in_stock else 'нет'}]: ").strip().lower()
        
        update_data = {}
        
        if name:
            update_data['name'] = name
        if description:
            update_data['description'] = description
        if price_input:
            try:
                price = float(price_input)
                if price < 0:
                    print("❌ Цена не может быть отрицательной.")
                    return
                update_data['price'] = price
            except ValueError:
                print("❌ Неверный формат цены.")
                return
        if in_stock_input in ['да', 'нет']:
            update_data['in_stock'] = in_stock_input == "да"
        
        if not update_data:
            print("❌ Не указано ни одного поля для изменения.")
            return
        
        updated_product = self.data_manager.update_product(product_id, **update_data)
        if updated_product:
            self.products[product_id] = updated_product  # Обновляем локальный кэш
            print(f"\n✅ Товар '{updated_product.name}' успешно обновлён.")
        else:
            print("❌ Не удалось обновить товар.")
    
    def delete_product(self) -> None:
        """Удаляет товар."""
        try:
            product_id = int(input("\nВведите ID товара для удаления: ").strip())
        except ValueError:
            print("❌ Неверный ID товара.")
            return
        
        product = self.product_service.get_product(product_id)
        if not product:
            print("❌ Товар с таким ID не найден.")
            return
        
        print(f"\n⚠️ Вы собираетесь удалить товар: {product.name}")
        confirm = input("Подтвердите удаление (да/нет): ").strip().lower()
        
        if confirm == "да":
            if self.data_manager.delete_product(product_id):
                del self.products[product_id]  # Обновляем локальный кэш
                print("✅ Товар успешно удалён.")
            else:
                print("❌ Не удалось удалить товар.")
        else:
            print("❌ Удаление отменено.")
    
    def show_orders(self) -> None:
        """Отображает список заказов."""
        orders = self.order_service.get_all_orders()
        
        if not orders:
            print("\n📋 Заказы отсутствуют.")
            return
        
        print("\n" + "="*70)
        print("📋 СПИСОК ЗАКАЗОВ")
        print("="*70)
        
        for order in reversed(orders):  # Новые заказы первыми
            print(f"\n{order}")
        
        print("\n" + "="*70)
        
        while True:
            print("\nВыберите действие:")
            print("1. Просмотреть детали заказа")
            print("2. Вернуться в главное меню")
            
            choice = input("Ваш выбор: ").strip()
            
            if choice == "1":
                self.show_order_details()
            elif choice == "2":
                break
            else:
                print("❌ Неверный выбор.")
    
    def show_order_details(self) -> None:
        """Отображает детали конкретного заказа."""
        try:
            order_id = int(input("\nВведите ID заказа: ").strip())
        except ValueError:
            print("❌ Неверный ID заказа.")
            return
        
        order = self.order_service.get_order(order_id)
        if not order:
            print("❌ Заказ с таким ID не найден.")
            return
        
        from datetime import datetime
        date = datetime.fromisoformat(order.created_at).strftime('%Y-%m-%d %H:%M:%S')
        
        print("\n" + "="*70)
        print(f"📋 ДЕТАЛИ ЗАКАЗА #{order.id}")
        print("="*70)
        print(f"Дата создания: {date}")
        print(f"Общая сумма: {order.total:.2f} ₽")
        print("\nТовары:")
        print("-"*70)
        
        for product_id, quantity in order.cart.items.items():
            product = self.products.get(product_id)
            if product:
                subtotal = product.price * quantity
                print(f"  [{product.id}] {product.name}")
                print(f"      Цена: {product.price:.2f} ₽")
                print(f"      Количество: {quantity}")
                print(f"      Сумма: {subtotal:.2f} ₽")
            else:
                print(f"  [ID: {product_id}] (товар удалён) x{quantity}")
        
        print("="*70)
        input("\nНажмите Enter для продолжения...")
    
    def show_statistics(self) -> None:
        """Отображает статистику магазина."""
        orders_count = self.order_service.get_orders_count()
        total_revenue = self.order_service.get_total_revenue()
        products_count = len(self.products)
        available_products = len([p for p in self.products.values() if p.in_stock])
        
        print("\n" + "="*70)
        print("📊 СТАТИСТИКА МАГАЗИНА")
        print("="*70)
        print(f"Всего товаров: {products_count}")
        print(f"Товаров в наличии: {available_products}")
        print(f"Всего заказов: {orders_count}")
        print(f"Общая выручка: {total_revenue:.2f} ₽")
        
        if orders_count > 0:
            avg_order = total_revenue / orders_count
            print(f"Средний чек: {avg_order:.2f} ₽")
        
        print("="*70)
        input("\nНажмите Enter для продолжения...")

