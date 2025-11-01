"""Модуль для работы с JSON-файлами для хранения данных."""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from .base_storage import IStorage


class JSONStorage(IStorage):
    """Класс для работы с JSON-файлами для хранения данных."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Инициализирует хранилище.
        
        Args:
            data_dir: Директория для хранения JSON-файлов
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Файлы для хранения данных
        self.products_file = self.data_dir / "products.json"
        self.orders_file = self.data_dir / "orders.json"
        self.cart_file = self.data_dir / "cart.json"
    
    def _read_json(self, file_path: Path, default: Any = None) -> Any:
        """
        Читает данные из JSON-файла.
        
        Args:
            file_path: Путь к файлу
            default: Значение по умолчанию, если файл не существует
            
        Returns:
            Данные из файла или значение по умолчанию
        """
        if not file_path.exists():
            return default if default is not None else {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка при чтении файла {file_path}: {e}")
            return default if default is not None else {}
    
    def _write_json(self, file_path: Path, data: Any) -> bool:
        """
        Записывает данные в JSON-файл.
        
        Args:
            file_path: Путь к файлу
            data: Данные для записи
            
        Returns:
            True если запись успешна, False в противном случае
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"Ошибка при записи файла {file_path}: {e}")
            return False
    
    def load_products(self) -> Dict[int, Dict[str, Any]]:
        """Загружает товары из файла."""
        data = self._read_json(self.products_file, default={})
        return {int(k): v for k, v in data.items()}
    
    def save_products(self, products: Dict[int, Dict[str, Any]]) -> bool:
        """Сохраняет товары в файл."""
        return self._write_json(self.products_file, products)
    
    def load_orders(self) -> List[Dict[str, Any]]:
        """Загружает заказы из файла."""
        data = self._read_json(self.orders_file, default=[])
        return data if isinstance(data, list) else []
    
    def save_orders(self, orders: List[Dict[str, Any]]) -> bool:
        """Сохраняет заказы в файл."""
        return self._write_json(self.orders_file, orders)
    
    def load_cart(self) -> Dict[str, Any]:
        """Загружает корзину из файла."""
        return self._read_json(self.cart_file, default={"items": {}})
    
    def save_cart(self, cart_data: Dict[str, Any]) -> bool:
        """Сохраняет корзину в файл."""
        return self._write_json(self.cart_file, cart_data)

