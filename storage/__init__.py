"""Модуль для работы с хранением данных."""

from .base_storage import IStorage
from .json_storage import JSONStorage

__all__ = ['IStorage', 'JSONStorage']
