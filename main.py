import tkinter as tk
import tkinter.ttk
from ui import MainWindow

def main():
    root = tk.Tk()

    app = MainWindow(root)

    root.mainloop()


if __name__ == "__main__":
    main()
