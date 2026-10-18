import tkinter as tk
import tkinter.ttk as ttk


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('Main Window')
        self.root.geometry('800x400')

        columns = ('id', 'Name', 'Year', 'Artist', 'Technique/Materials', 'Area/Density', 'Estimated value', 'Type')
        self.table = ttk.Treeview(self.root, columns=columns, show='headings')

        self.table.heading('id', text='ID')
        self.table.column('id', width=40, minwidth=40, stretch=True, anchor='center')

        self.table.heading('Name', text='Name')
        self.table.column('Name', width=100, minwidth=80, stretch=True, anchor='center')

        self.table.heading('Year', text='Year')
        self.table.column('Year', width=60, minwidth=50, stretch=True, anchor='center')

        self.table.heading('Artist', text='Artist')
        self.table.column('Artist', width=100, minwidth=80, stretch=True, anchor='center')

        self.table.heading('Technique/Materials', text='Technique/Materials')
        self.table.column('Technique/Materials', width=150, minwidth=120, stretch=True, anchor='center')

        self.table.heading('Area/Density', text='Area/Density')
        self.table.column('Area/Density', width=90, minwidth=80, stretch=True, anchor='center')

        self.table.heading('Estimated value', text='Estimated value')
        self.table.column('Estimated value', width=110, minwidth=90, stretch=True, anchor='center')

        self.table.heading('Type', text='Type')
        self.table.column('Type', width=80, minwidth=70, stretch=True, anchor='center')

        tests = [
            (1, 'name', 'Year', 'Artist', 'Technique/Materials', 'Area/Density', 'Estimated value', 'Type'),
            (2, 'name', 'Year', 'Artist', 'Technique/Materials', 'Area/Density', 'Estimated value', 'Type')
        ]

        for test in tests:
            self.table.insert('', tk.END, values=test)

        self.table.pack(fill=tk.BOTH, expand=True, padx=0, pady=5)