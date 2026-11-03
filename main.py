import tkinter as tk
import tkinter.ttk
from ui import MainWindow
from storage import JsonStorage

def main():
    root = tk.Tk()

    MainWindow(root, JsonStorage())

    root.mainloop()


if __name__ == "__main__":
    main()