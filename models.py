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
    def validate_positive_float(value:float|str) -> float:
        """Преобразует значение в не целое положительное число или возвращает ошибку."""
        try:
            if float(value) < 0:
                raise ValueError(f"{value} должно быть целым положительным числом")
            else:
                return float(value)
        except:
            raise TypeError(f"{value} должно быть целым положительным числом")

    @staticmethod
    def validate_non_empty_string(value:str) -> str:
        """Возвращает непустую строку или ошибку."""

        if not isinstance(value, str):
            raise TypeError(f"Значение '{value}' должно быть строкой")

        if len(value.strip()) == 0:
            raise ValueError(f"Значение '{value}' не может быть пустой строкой")

        return value

    @staticmethod
    def validate_choice(value:str, permissible_values:list) -> str:
        if value in permissible_values:
            return value
        else:
            raise ValueError(f"Недопустимое значение {value}. Допустимые значения:{permissible_values}")


class BaseItem(TimestampMixin, ValidationMixin, ABC):
    """Абстрактный класс базового элемента"""

    def __init__(self, title:str, year:int, id:str=None, **kwargs):
        self.id = id if id else uuid.uuid4().hex
        self.title = self.validate_non_empty_string(title)
        self.year = self.validate_positive_int(year)
        super().__init__(**kwargs)

    @property
    def age(self) -> int:
        """Возвращает возраст"""
        return datetime.now().year - self.year

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


class Painting(BaseItem):
    """Класс картин"""

    permissible_technique = ["Масло", "Акварель", "Пастель"]
    def __init__(self,  title:str, year:int, artist:str, technique:str, width_cm:float, height_cm:float, estimated_value:float, **kwargs):
        super().__init__(title=title, year=year, **kwargs)
        self.artist = self.validate_non_empty_string(artist)
        self.technique = self.validate_choice(technique, self.permissible_technique)
        self.width_cm = self.validate_positive_float(width_cm)
        self.height_cm = self.validate_positive_float(height_cm)
        self.estimated_value = self.validate_positive_float(estimated_value)

    @property
    def area(self) -> float:
        return self.width_cm * self.height_cm

    def get_risk_level(self, all_items: list = None) -> str:
        if self.technique == "Акварель" and self.age > 80:
            return "high"
        return "normal"

    def get_summary(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "year": self.year,
            "artist": self.artist,
            "technique": self.technique,
            "area": self.area,
            "estimated_value": self.estimated_value,
            "type": "Картина"
        }

    def get_dynamic_fields(self) -> dict:
        return{
            "artist": self.artist,
            "technique": self.technique,
            "width_cm": self.width_cm,
            "height_cm": self.height_cm,
            "estimated_value": self.estimated_value
        }

    @classmethod
    def get_field_schema(cls) -> dict:
        return{
            "title": {"label": "Название", "type": "str", "required": True},
            "year": {"label": "Год создания", "type": "int", "required": True},
            "artist": {"label": "Художник", "type": "str", "required": True},
            "technique": {"label": "Техника", "type": "choice", "choices": cls.permissible_technique},
            "width_cm": {"label": "Ширина(см)", "type": "float", "required": True},
            "height_cm": {"label": "Высота(см)", "type": "float", "required": True},
            "estimated_value": {"label": "Оценочная стоимость", "type": "float", "required": True}
        }


class Sculpture(BaseItem):
    """Класс скульптур"""

    permissible_technique = ["Бронза", "Мрамор", "Дерево"]

    def __init__(self, title: str, year: int, artist: str, material: str, weight_kg: float, volume_m3: float, **kwargs):
        super().__init__(title=title, year=year, **kwargs)
        self.artist = self.validate_non_empty_string(artist)
        self.material = self.validate_choice(material, self.permissible_technique)
        self.weight_kg = self.validate_positive_float(weight_kg)
        self.volume_m3 = self.validate_positive_float(volume_m3)


    @property
    def density(self):
        return self.weight_kg / self.volume_m3 if self.volume_m3 > 0 else None

    def get_risk_level(self, all_items: list = None) -> str:
        if (self.age > 80):
            return "high"
        return "normal"

    def get_summary(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "year": self.year,
            "artist": self.artist,
            "material": self.material,
            "density": f"{self.density} кг/м³",
            "estimated_value": "-",
            "type": "Sculpture"
        }

    def get_dynamic_fields(self) -> dict:
        return {
            "artist": self.artist,
            "material": self.material,
            "weight_kg": self.weight_kg,
            "volume_m3": self.volume_m3
        }

    @classmethod
    def get_field_schema(cls) -> dict:
        return {
            "title": {"label": "Название", "type": "str", "required": True},
            "year": {"label": "Год создания", "type": "int", "required": True},
            "artist": {"label": "Скульптор", "type": "str", "required": True},
            "material": {"label": "Материал", "type": "choice", "choices": cls.permissible_technique},
            "weight_kg": {"label": "Вес (кг)", "type": "float", "required": True},
            "volume_m3": {"label": "Объем (м³)", "type": "float", "required": True}
        }



