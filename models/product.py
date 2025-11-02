"""Модель товара."""

from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class Product:
    """Класс для представления товара в магазине."""
    
    id: int
    name: str
    description: str
    price: float
    in_stock: bool = True
    image: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Преобразует объект Product в словарь."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """Создаёт объект Product из словаря."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            price=data['price'],
            in_stock=data.get('in_stock', True),
            image=data.get('image', None)
        )
    
    def __str__(self) -> str:
        """Строковое представление товара."""
        status = "✓ В наличии" if self.in_stock else "✗ Нет в наличии"
        return f"[{self.id}] {self.name} - {self.price:.2f} ₽ | {status}"
