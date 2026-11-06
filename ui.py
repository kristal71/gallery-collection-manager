import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog
from factory import ItemFactory
from storage import JsonStorage

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
        self.create_toolbar()
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
            self.table.heading(col, text=column_titles[col], command=lambda c=col: self.sort_by(c))
            self.table.column(col, width=100, anchor="center")

        for tag, color in {"high": "#ffb3b3", "normal": "#ffffff"}.items():
            self.table.tag_configure(tag, background=color)

        self.table.pack(side="left", fill="both", expand=True)

    def create_toolbar(self) -> None:
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

        self.filter_field = tk.StringVar(value="title")
        ttk.Combobox(
            frame, textvariable=self.filter_field,
            values = list(column_titles), state="readonly", width=20,
        ).pack(side="left", padx=5)

        ttk.Label(frame, text="Значение:").pack(side="left")
        self.filter_value = tk.StringVar()
        ttk.Entry(frame, textvariable=self.filter_value, width=20).pack(side="left", padx=5)

        ttk.Button(frame, text="Искать", command=self.apply_filter).pack(side="left")
        ttk.Button(frame, text="Сброс", command=self.reset_filter).pack(side="left", padx=5)


    def add_item(self) -> None:
        DynamicForm(self.root, self._save_new_item)

    def _save_new_item(self, data) -> None:
        """Обрабатывает и сохраняет новый элемент"""

        self.items.append(ItemFactory.create_item(data))
        self.storage.save_items(self.items)
        self.apply_filter()

    def edit_item(self) -> None:
        """Открывает окно редактирование выбранного элемента"""

        item = self.selected_item()
        if item is None:
            messagebox.showinfo("Для редактирования выберите строку.")
            return
        DynamicForm(self.root, self._save_edited_item, item)


    def _save_edited_item(self, data:dict) -> None:
        """Обрабатывает и сохраняет выбранный элемент"""

        item_id = data.get("id")
        item = next((x for x in self.items if x.id == item_id), None)
        data["created_at"] = item.created_at
        checked = ItemFactory.create_item(data)
        item.title = checked.title
        item.year = checked.year

        item.__dict__.update(checked.get_dynamic_fields())
        item.touch()
        self.storage.save_items(self.items)
        self.apply_filter()


    def selected_item(self):
        """Возвращает объект выбранной строки"""
        selected = self.table.selection()
        if not selected:
            return None

        selected_id = selected[0]
        for item in self.items:
            if str(item.id) == selected_id:
                return item
        return None


    def delete_item(self) -> None:
        """Удаление выбранного объекта"""

        item = self.selected_item()
        if not item:
            messagebox.showinfo("Выберите строку дял удаления")
            return
        if messagebox.askyesno(f"Удалить {item.title}?"):
            self.items.remove(item)
            self.storage.save_items(self.items)
            self.apply_filter()


    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path:
            return
        self.storage = JsonStorage(path)
        self.items = self.storage.load_items()
        self.visible_items = list(self.items)
        self.refresh()


    def apply_filter(self) -> None:
        """Фильтрует элементы в таблице по выбранному полю и введённому значению"""

        field = self.filter_field.get()
        value = self.filter_value.get().strip().lower()
        if value:
            self.visible_items= [item for item in self.items
                                 if value in str(get_value(item.get_summary(), field)).lower()]
        else:
            self.visible_items = list(self.items)
        self.refresh()

    def reset_filter(self) -> None:
        """Сбрасывает фильтр."""

        self.filter_value.set("")
        self.visible_items = list(self.items)
        self.refresh()

    def refresh(self) -> None:
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


    def sort_by(self, column) -> None:
        """Динамическая сортировка элементов при нажатии на заголовок столбца"""

        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        def sort_key(item) -> tuple:
            """Ключ для сортировки. Разделяет поля на сравнимые группы по типу данных"""
            value = get_value(item.get_summary(), column)
            if isinstance(value, (int, float)):
                return 0, value
            return 1, str(value).lower()

        self.visible_items.sort(key=sort_key, reverse=self.sort_reverse)
        self.refresh()


class DynamicForm(tk.Toplevel):
    def __init__(self, master, on_save, item=None):
        super().__init__(master)
        self.on_save = on_save
        self.item = item
        self.widgets ={}
        self.title("Редактирование" if item else "Добавление")
        self.grab_set()

        registry = ItemFactory.get_registry_type()
        if item is None:
            frame = ttk.Frame(self, padding=5)
            frame.pack(fill="x")
            self.type_var = tk.StringVar(value=list(registry)[0])

            combob = ttk.Combobox(frame, textvariable=self.type_var, values=list(registry), state="readonly")
            combob.pack()
            combob.bind("<<ComboboxSelected>>", lambda e: self.build_fields())
        else:
            self.type_var = tk.StringVar(value=item.__class__.__name__)

        self.fields_frame = ttk.Frame(self, padding=5)
        self.fields_frame.pack(fill="both", expand=True)
        self.build_fields()

        buttons = ttk.Frame(self, padding=5)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Сохранить", command=self.submit).pack(side="right")
        ttk.Button(buttons, text="Отмена", command=self.destroy).pack(side="right", padx=5)

    def build_fields(self) -> None:
        """Динамически перестраивает поля формы в зависимости от выбранного типа объекта."""

        for w in self.fields_frame.winfo_children():
            w.destroy()
        self.widgets.clear()

        cls = ItemFactory.get_registry_type()[self.type_var.get()]
        schema = cls.get_field_schema()
        values = {}
        if self.item:
            values = {"title": self.item.title, "year": self.item.year, **self.item.get_dynamic_fields()}

        for row, (name, meta) in enumerate(schema.items()):
            ttk.Label(self.fields_frame, text=meta["label"]).grid(row=row, column=0, sticky="w")

            var = tk.StringVar(value=str(values.get(name, "")))
            if meta["type"] == "choice":
                widget = ttk.Combobox(self.fields_frame, textvariable=var, values=meta["choices"], state="readonly")
            else:
                widget = ttk.Entry(self.fields_frame, textvariable=var)

            widget.grid(row=row, column=1, sticky="ew")
            self.widgets[name] = var

        self.fields_frame.columnconfigure(1,weight=1)

    def submit(self) -> None:
        """Собирает данные из формы и сохраняет объект."""

        data = {name: var.get() for name, var in self.widgets.items()}
        data["__type__"] = ( self.item.__class__.__name__ if self.item else self.type_var.get())

        if self.item:
            data["id"] = self.item.id
        try:
            self.on_save(data)
        except(ValueError, TypeError) as e:
            messagebox.showerror("Ошибка")
            return
        self.destroy()
