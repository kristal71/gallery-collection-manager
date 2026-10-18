import uuid
from abc import ABC, abstractmethod
from datetime import datetime
import time

class TimestampMixin:
    """Миксин: добавляет любому классу дату создания и дату обновления."""

    def __init__(self, created_at:str=None, updated_at:str=None, **kwargs):
        current_time = datetime.now().isoformat()

        self.created_at = created_at if created_at else current_time
        self.updated_at = updated_at if updated_at else current_time
        super().__init__(**kwargs)


    def touch(self):
        """Обновляет значение updated_at на текущее время."""

        self.updated_at = datetime.now().isoformat()


class ValidationMixin:
    """Миксин: валидация типов и диапазонов данных. """

    @staticmethod
    def validate_positive_int(value:int|str) -> int:
        """Преобразует значение в целое положительное число или возвращает ошибку."""

        try:
            if int(value) < 0:
                raise ValueError(f"{value} должно быть целым положительным числом")
            else:
                return int(value)
        except:
            raise TypeError(f"{value} должно быть целым положительным числом")

    @staticmethod
    def validate_non_empty_string(value:str) -> str:
        """Возвращает непустую строку или ошибку."""

        try:
            if len(value) == 0:
                raise ValueError(f"Значение: {value} должно быть непустой строкой")
            else:
                return value

        except:
            raise TypeError(f"Значение: {value} должно быть непустой строкой")


class BaseItem(ABC, TimestampMixin, ValidationMixin):
    """Абстрактный класс базового элемента"""

    def __init__(self, title:str, year:int, id:str=None, **kwargs):
        self.id = id if id else uuid.uuid4().hex
        self.title = self.validate_non_empty_string(title)
        self.year = self.validate_positive_int(year)
        super().__init__(**kwargs)

    @abstractmethod
    def get_risk_level(self, all_items: list = None) -> str:
        """Возвращает уровень риска ("normal", "high", "warning", "orphan" и т.д.) для цветовой подсветки строки.
           Принимает полный список элементов коллекции для контекстных проверок."""
        pass

    @abstractmethod
    def get_summary(self) -> dict:
        """Возвращает словарь всех отображаемых полей (включая рассчитываемые) для вывода в Treeview."""
        pass

    @abstractmethod
    def get_dynamic_fields(self) -> dict:
        """Возвращает словарь только специфических атрибутов сущности (для сериализации)."""
        pass

    @classmethod
    @abstractmethod
    def get_field_schema(self) -> dict:
        """Возвращает описание полей для построения DynamicForm
           (имя поля, тип ввода, список значений для Combobox, обязательность)."""
        pass


    def to_dict(self) -> dict:
        """Сохраняет только базовые и динамические атрибуты,
           а также служебный ключ "__type__" (имя класса) и временные метки (created_at, updated_at).
           Рассчитываемые поля в JSON не сохраняются."""

        data = {
            "__type__": self.__class__.__name__,
            "id": self.id,
            "title": self.title,
            "year": self.year,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        data.update(self.get_dynamic_fields())
        return data
