import tkinter as tk
import tkinter.ttk as ttk


columns = ("id", "title", "year", "artist",
           "technique_material", "area_density",
           "estimated_value", "type")

column_titles = {
    "id": "ID", "title": "Название", "year": "Год",
    "artist": "Художник",
    "technique_material": "Техника/Материал",
    "area_density": "Площадь/Плотность",
    "estimated_value": "Стоимость", "type": "Тип",
}

stretch_columns = {"title", "technique_material", "artist"}

def get_value(summary, field) -> int|str:
    """Возвращает значение поля"""

    synonyms = {"technique_material": ("technique", "material"), "area_density": ("area", "density")}
    if field in synonyms:
        for name in synonyms[field]:
            if name in summary:
                return summary[name]
        return "-"
    return summary.get(field, "-")

def summary_to_row(item) -> tuple[int|str, ...]:
    """преобразует объект в кортеж данных, готовый для вставки в таблицу"""

    summary = item.get_summary()
    return tuple(get_value(summary, col) for col in columns)


class MainWindow:
    def __init__(self, root, storage):
        self.root = root
        self.storage = storage
        self.root.title('Main Window')
        self.root.geometry('1400x500')

        self.items= self.storage.load_items()
        self.visible_items = list(self.items)
        self.sort_column = None
        self.sort_reverse = False

        self.create_statusbar()
        self.create_table()
        self.build_toolbar()
        self.refresh()


    def create_statusbar(self) -> None:
        """Создаёт строку состояния внизу главного окна"""

        frame = ttk.Frame(self.root)
        frame.pack(side = "bottom", fill = "x")
        self.count_label = ttk.Label(frame, text='Отображено объектов: 0', padding=3)
        self.count_label.pack(side = "left")
        self.file_label = ttk.Label(frame, text='Файл: -', padding=3)
        self.file_label.pack(side  = "right")

    def create_table(self) -> None:
        """Создаёт таблицу Treeviw с пустыми колонками"""

        self.table = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.table.heading(col, text=column_titles[col])
            self.table.column(col, width=100, anchor="center")

        for tag, color in {"high": "#ffb3b3", "normal": "#ffffff"}.items():
            self.table.tag_configure(tag, background=color)

        self.table.pack(side="left", fill="both", expand=True)

    def build_toolbar(self) -> None:
        """Создаёт панель управления с основными кнопками"""

        toolbar = ttk.Frame(self.root, padding=5)
        toolbar.pack(side="top", fill="x")

        for title, command in(
            ("Добавить", self.add_item),
            ("Редактировать", self.edit_item),
            ("Удалить", self.delete_item),
            ("Открыть файл", self.choose_file),
        ):
            ttk.Button(toolbar, text=title,command=command).pack(side="left", padx=3)

        frame = ttk.Frame(self.root, padding=3)
        frame.pack(side="top", fill="x")
        ttk.Label(frame, text="Поле: ").pack(side="left")

        self.filter_field = tk.StringVar(value="Название")
        ttk.Combobox(
            frame, textvariable=self.filter_field,
            values = list(column_titles), state="readonly", width=20,
        ).pack(side="left", padx=5)

        ttk.Label(frame, text="Значение:").pack(side="left")
        self.filter_value = tk.StringVar()
        ttk.Entry(frame, textvariable=self.filter_value, width=20).pack(side="left", padx=5)

        ttk.Button(frame, text="Искать", command=self.apply_filter).pack(side="left")
        ttk.Button(frame, text="Сброс", command=self.reset_filter).pack(side="left", padx=5)


    def add_item(self):
        pass

    def edit_item(self):
        pass

    def delete_item(self):
        pass

    def choose_file(self):
        pass

    def apply_filter(self):
        pass

    def reset_filter(self):
        pass

    def refresh(self):
        """Обновление главного окна программы при любом изменении данных."""

        self.table.delete(*self.table.get_children())
        for item in self.visible_items:
            self.table.insert("", "end", iid=str(item.id),
                              values=summary_to_row(item), tags=(item.get_risk_level(self.items),))
        total, show = len(self.items), len(self.visible_items)
        self.count_label.config(text=f"Отображено объектов: {show} из {total}")

        if self.storage.file_existed:
            self.file_label.config(text=f"Файл: {self.storage.file_path}")
        else:
            self.file_label.config(text="Файл не найден. Новый файл будет создан при сохранении")
