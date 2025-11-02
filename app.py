"""Flask приложение для интернет-магазина SHOP SHIPS."""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from data_manager import DataManager
from services import CartService, ProductService, OrderService
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'shop_ships_secret_key_change_in_production'

# Константа валюты
CURRENCY = 'USD'
CURRENCY_SYMBOL = '$'

# Инициализация менеджера данных
data_manager = DataManager()


def get_cart_service() -> CartService:
    """Получает сервис корзины для текущей сессии (DRY)."""
    cart = data_manager.load_cart()
    products = data_manager.get_all_products()
    return CartService(cart, products)


def admin_required(f):
    """Декоратор для проверки администратора (в будущем можно добавить реальную авторизацию)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Простая проверка (в продакшене нужна реальная авторизация)
        if not session.get('is_admin'):
            flash('Доступ запрещён. Требуется авторизация администратора.', 'danger')
            return redirect(url_for('public_index'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== Публичные маршруты ====================

@app.route('/')
def public_index():
    """Главная страница магазина."""
    product_service = ProductService(data_manager.get_all_products())
    products = product_service.get_available_products()
    cart_service = get_cart_service()
    cart_count = cart_service.get_items_count()
    
    return render_template('public/index.html', 
                         products=products, 
                         cart_count=cart_count,
                         currency_symbol=CURRENCY_SYMBOL)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Страница деталей товара."""
    product = data_manager.get_product(product_id)
    if not product:
        flash('Товар не найден.', 'danger')
        return redirect(url_for('public_index'))
    
    cart_service = get_cart_service()
    cart_count = cart_service.get_items_count()
    
    return render_template('public/product_detail.html', 
                         product=product, 
                         cart_count=cart_count,
                         currency_symbol=CURRENCY_SYMBOL)


@app.route('/search')
def search():
    """Поиск товаров."""
    query = request.args.get('q', '').strip()
    cart_service = get_cart_service()
    cart_count = cart_service.get_items_count()
    
    if not query:
        return redirect(url_for('public_index'))
    
    product_service = ProductService(data_manager.get_all_products())
    results = product_service.search_products(query)
    
    return render_template('public/search.html', 
                         query=query, 
                         results=results, 
                         cart_count=cart_count,
                         currency_symbol=CURRENCY_SYMBOL)


@app.route('/cart')
def cart():
    """Страница корзины."""
    cart_service = get_cart_service()
    items = cart_service.get_cart_items()
    total = cart_service.get_total()
    cart_count = cart_service.get_items_count()
    
    return render_template('public/cart.html', 
                         items=items, 
                         total=total, 
                         cart_count=cart_count,
                         currency_symbol=CURRENCY_SYMBOL)


@app.route('/cart/add', methods=['POST'])
def cart_add():
    """Добавление товара в корзину."""
    try:
        product_id = int(request.form.get('product_id'))
        quantity = int(request.form.get('quantity', 1))
    except (ValueError, TypeError):
        flash('Неверные данные.', 'danger')
        return redirect(url_for('public_index'))
    
    cart_service = get_cart_service()
    if cart_service.add_product(product_id, quantity):
        data_manager.save_cart(cart_service.cart)
        flash('Товар добавлен в корзину!', 'success')
    else:
        flash('Не удалось добавить товар. Возможно, товар недоступен.', 'danger')
    
    return redirect(request.referrer or url_for('public_index'))


@app.route('/cart/update', methods=['POST'])
def cart_update():
    """Обновление количества товара в корзине."""
    try:
        product_id = int(request.form.get('product_id'))
        quantity = int(request.form.get('quantity'))
        
        if quantity <= 0:
            return cart_remove()
    except (ValueError, TypeError):
        flash('Неверные данные.', 'danger')
        return redirect(url_for('cart'))
    
    cart_service = get_cart_service()
    
    # Получаем текущее количество
    current_qty = cart_service.cart.items.get(product_id, 0)
    difference = quantity - current_qty
    
    if difference > 0:
        cart_service.add_product(product_id, difference)
    elif difference < 0:
        cart_service.remove_product(product_id, -difference)
    
    data_manager.save_cart(cart_service.cart)
    flash('Корзина обновлена.', 'success')
    return redirect(url_for('cart'))


@app.route('/cart/remove', methods=['POST'])
def cart_remove():
    """Удаление товара из корзины."""
    try:
        product_id = int(request.form.get('product_id'))
    except (ValueError, TypeError):
        flash('Неверные данные.', 'danger')
        return redirect(url_for('cart'))
    
    cart_service = get_cart_service()
    if product_id in cart_service.cart.items:
        quantity = cart_service.cart.items[product_id]
        cart_service.remove_product(product_id, quantity)
        data_manager.save_cart(cart_service.cart)
        flash('Товар удалён из корзины.', 'success')
    
    return redirect(url_for('cart'))


@app.route('/cart/clear', methods=['POST'])
def cart_clear():
    """Очистка корзины."""
    cart_service = get_cart_service()
    cart_service.clear_cart()
    data_manager.save_cart(cart_service.cart)
    flash('Корзина очищена.', 'success')
    return redirect(url_for('cart'))


@app.route('/checkout')
def checkout():
    """Страница оформления заказа (checkout)."""
    cart_service = get_cart_service()
    
    if not cart_service.cart.items:
        flash('Корзина пуста.', 'warning')
        return redirect(url_for('cart'))
    
    items = cart_service.get_cart_items()
    total = cart_service.get_total()
    cart_count = cart_service.get_items_count()
    
    return render_template('public/checkout.html',
                         items=items,
                         total=total,
                         cart_count=cart_count,
                         currency_symbol=CURRENCY_SYMBOL)


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    """Страница оплаты."""
    if request.method == 'POST':
        # Обработка платежа
        payment_method = request.form.get('payment_method')
        card_number = request.form.get('card_number', '').strip()
        expiry_date = request.form.get('expiry_date', '').strip()
        cvv = request.form.get('cvv', '').strip()
        cardholder_name = request.form.get('cardholder_name', '').strip()
        
        # Простая валидация (в реальном приложении нужна более серьёзная проверка)
        if payment_method == 'card':
            if not all([card_number, expiry_date, cvv, cardholder_name]):
                flash('Заполните все поля для оплаты картой.', 'danger')
                return redirect(url_for('payment'))
        
        # Создаём заказ
        cart_service = get_cart_service()
        order = data_manager.create_order(
            cart_service.cart, 
            data_manager.get_all_products()
        )
        
        cart_service.clear_cart()
        data_manager.save_cart(cart_service.cart)
        
        flash(f'Заказ #{order.id} успешно оформлен и оплачен!', 'success')
        return redirect(url_for('order_success', order_id=order.id))
    
    # GET запрос - показываем форму оплаты
    cart_service = get_cart_service()
    
    if not cart_service.cart.items:
        flash('Корзина пуста.', 'warning')
        return redirect(url_for('cart'))
    
    items = cart_service.get_cart_items()
    total = cart_service.get_total()
    cart_count = cart_service.get_items_count()
    
    return render_template('public/payment.html',
                         items=items,
                         total=total,
                         cart_count=cart_count,
                         currency_symbol=CURRENCY_SYMBOL)


@app.route('/order/success/<int:order_id>')
def order_success(order_id):
    """Страница успешного оформления заказа."""
    order = data_manager.get_order(order_id)
    if not order:
        flash('Заказ не найден.', 'danger')
        return redirect(url_for('public_index'))
    
    cart_service = get_cart_service()
    cart_count = cart_service.get_items_count()
    
    # Получаем детали заказа
    products = data_manager.get_all_products()
    order_items = {}
    for product_id, quantity in order.cart.items.items():
        if product_id in products:
            order_items[product_id] = {
                'product': products[product_id],
                'quantity': quantity
            }
    
    return render_template('public/order_success.html', 
                         order=order, 
                         items=order_items, 
                         cart_count=cart_count,
                         currency_symbol=CURRENCY_SYMBOL)


@app.route('/contacts')
def contacts():
    """Страница контактов."""
    cart_service = get_cart_service()
    cart_count = cart_service.get_items_count()
    
    return render_template('public/contacts.html',
                         cart_count=cart_count)


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Страница обратной связи."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        if not all([name, email, message]):
            flash('Заполните все обязательные поля.', 'danger')
            return redirect(url_for('feedback'))
        
        # В реальном приложении здесь бы была отправка email
        # Пока просто сохраняем в сессии или логируем
        flash('Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.', 'success')
        return redirect(url_for('feedback'))
    
    cart_service = get_cart_service()
    cart_count = cart_service.get_items_count()
    
    return render_template('public/feedback.html',
                         cart_count=cart_count)


# ==================== CRM маршруты ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Авторизация администратора (упрощённая версия)."""
    if request.method == 'POST':
        password = request.form.get('password', '')
        # Простая проверка (в продакшене нужна реальная авторизация)
        if password == 'admin':
            session['is_admin'] = True
            flash('Вы успешно вошли в систему.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Неверный пароль.', 'danger')
    
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    """Выход из системы администратора."""
    session.pop('is_admin', None)
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    """Главная страница CRM."""
    product_service = ProductService(data_manager.get_all_products())
    order_service = OrderService(data_manager.get_all_orders())
    
    stats = {
        'total_products': len(product_service.get_all_products()),
        'available_products': len(product_service.get_available_products()),
        'total_orders': order_service.get_orders_count(),
        'total_revenue': order_service.get_total_revenue(),
        'avg_order': order_service.get_total_revenue() / order_service.get_orders_count() 
                    if order_service.get_orders_count() > 0 else 0
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         currency_symbol=CURRENCY_SYMBOL)


@app.route('/admin/products')
@admin_required
def admin_products():
    """Управление товарами."""
    product_service = ProductService(data_manager.get_all_products())
    products = product_service.get_all_products()
    
    return render_template('admin/products.html', 
                         products=products,
                         currency_symbol=CURRENCY_SYMBOL)


@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_product_add():
    """Добавление товара."""
    if request.method == 'POST':
        from models import Product
        
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        try:
            price = float(request.form.get('price', 0))
            if price < 0:
                flash('Цена не может быть отрицательной.', 'danger')
                return render_template('admin/product_form.html', mode='add')
        except (ValueError, TypeError):
            flash('Неверный формат цены.', 'danger')
            return render_template('admin/product_form.html', mode='add')
        
        in_stock = request.form.get('in_stock') == 'on'
        image = request.form.get('image', '').strip() or None
        
        if not name:
            flash('Название товара обязательно.', 'danger')
            return render_template('admin/product_form.html', mode='add')
        
        product = Product(id=0, name=name, description=description, price=price, in_stock=in_stock, image=image)
        product = data_manager.add_product(product)
        flash(f'Товар "{product.name}" успешно добавлен!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', mode='add')


@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_product_edit(product_id):
    """Редактирование товара."""
    product = data_manager.get_product(product_id)
    if not product:
        flash('Товар не найден.', 'danger')
        return redirect(url_for('admin_products'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        try:
            price = float(request.form.get('price', 0))
            if price < 0:
                flash('Цена не может быть отрицательной.', 'danger')
                return render_template('admin/product_form.html', mode='edit', product=product)
        except (ValueError, TypeError):
            flash('Неверный формат цены.', 'danger')
            return render_template('admin/product_form.html', mode='edit', product=product)
        
        in_stock = request.form.get('in_stock') == 'on'
        image = request.form.get('image', '').strip() or None
        
        if not name:
            flash('Название товара обязательно.', 'danger')
            return render_template('admin/product_form.html', mode='edit', product=product)
        
        updated = data_manager.update_product(
            product_id, 
            name=name, 
            description=description, 
            price=price, 
            in_stock=in_stock,
            image=image
        )
        
        if updated:
            flash('Товар успешно обновлён!', 'success')
            return redirect(url_for('admin_products'))
        else:
            flash('Ошибка при обновлении товара.', 'danger')
    
    return render_template('admin/product_form.html', mode='edit', product=product)


@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def admin_product_delete(product_id):
    """Удаление товара."""
    product = data_manager.get_product(product_id)
    if not product:
        flash('Товар не найден.', 'danger')
        return redirect(url_for('admin_products'))
    
    if data_manager.delete_product(product_id):
        flash(f'Товар "{product.name}" успешно удалён!', 'success')
    else:
        flash('Ошибка при удалении товара.', 'danger')
    
    return redirect(url_for('admin_products'))


@app.route('/admin/orders')
@admin_required
def admin_orders():
    """Список заказов."""
    order_service = OrderService(data_manager.get_all_orders())
    orders = order_service.get_all_orders()
    
    return render_template('admin/orders.html', 
                         orders=reversed(orders),
                         currency_symbol=CURRENCY_SYMBOL)


@app.route('/admin/orders/<int:order_id>')
@admin_required
def admin_order_detail(order_id):
    """Детали заказа."""
    order = data_manager.get_order(order_id)
    if not order:
        flash('Заказ не найден.', 'danger')
        return redirect(url_for('admin_orders'))
    
    products = data_manager.get_all_products()
    order_items = {}
    for product_id, quantity in order.cart.items.items():
        if product_id in products:
            order_items[product_id] = {
                'product': products[product_id],
                'quantity': quantity
            }
    
    return render_template('admin/order_detail.html', 
                         order=order, 
                         items=order_items,
                         currency_symbol=CURRENCY_SYMBOL)


# ==================== Обработка ошибок ====================

@app.errorhandler(404)
def not_found(error):
    """Обработка 404 ошибки."""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработка 500 ошибки."""
    return render_template('errors/500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
