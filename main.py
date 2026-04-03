"""
Number String Game — entry point.
Run with: python main.py
"""
import tkinter as tk
from src.ui import App


def main() -> None:
    root = tk.Tk()
    app  = App(root)
    app.run()


if __name__ == '__main__':
    main()
