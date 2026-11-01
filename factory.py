from models import BaseItem, Painting, Sculpture

class ItemFactory:
    """Класс для создания объектов на основе типа и словаря данных."""

    _registry: dict[str, type[BaseItem]] = {
        "Painting": Painting,
        "Sculpture": Sculpture
    }

    @classmethod
    def get_registry_type(cls):
        """Возвращает список всевозможных типов объектов"""
        return cls._registry

    @classmethod
    def create_item(cls, data:dict) -> BaseItem:
        """Принимает словарь данных, извлекает тип и возвращает нужный объект"""

        item_data = data.copy()
        type_name = item_data.pop("__type__", None)
        if not type_name: raise ValueError("В данных отсутствует '__type__'.")

        final_class = cls._registry.get(type_name)
        if not final_class: raise ValueError(f"Неизвестный тип сущности: '{type_name}'.")

        item_id = item_data.pop("id", None)

        return final_class(id=item_id, **item_data)