import json
import os.path

from factory import ItemFactory
from models import BaseItem

class JsonStorage:
    """Класс JsonStorage для загрузки и сохранения объектов в JSON-файл."""

    def __init__(self, file_path:str = os.path.join("data", "gallery.json")):
        self.file_path = file_path
        self.file_existed = os.path.exists(self.file_path)

    def load_items(self) -> list[BaseItem]:
        """Загрузка файлов из JSON-файла"""
        if not os.path.exists(self.file_path):
            self.file_existed = False
            return []

        self.file_existed = True
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                raw_data = json.load(file)
                items = [ItemFactory.create_item(item_dict) for item_dict in raw_data]
                return items
        except:
            return []

    def save_items(self, items:list[BaseItem]) -> None:
        """Записываем итоговый массив словарей в файл"""
        dir_path = os.path.dirname(self.file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        serialized_data = [item.to_dict() for item in items]

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(serialized_data, file, ensure_ascii=False, indent=4)

        self.file_existed = True
