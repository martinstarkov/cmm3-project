import tkinter as tk
from typing import List
from PIL import Image, ImageTk

# TODO: Add short description at the top of this file.
# Utility functions for easily creating gridded tkinter widgets.

def create_root(geometry):
    root = tk.Tk()
    root.geometry(geometry)
    root.configure(bg="white")
    set_grid_sizes(root, [100], [100], uniform_row="root", uniform_column="root")
    return root

def set_grid_sizes(container, rows: List[int] = [], columns: List[int] = [], uniform_row: str = "", uniform_column: str = ""):
    for row, size in enumerate(rows):
        container.grid_rowconfigure(row, weight=size, uniform=uniform_row)
    for column, size in enumerate(columns):
        container.grid_columnconfigure(column, weight=size, uniform=uniform_column)

def create_frame(parent_container, row: int, column: int, sticky: str = "NSEW"):
    frame = tk.Frame(parent_container, bg="white", bd=0)
    frame.grid(row=row, column=column, sticky=sticky)
    return frame

def create_label(parent_container, text: str, row: int, column: int, sticky: str = "NSEW", padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0):
    label = tk.Label(parent_container, text=text, bg="white")
    label.grid(row=row, column=column, padx=0, pady=0, ipadx=0, ipady=0, sticky=sticky)
    return label

def create_entry(parent_container, default_value, row: int, column: int, sticky: str = "NSEW", padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0, **kwargs):
    entry = tk.Entry(parent_container, bg="white", justify="center", **kwargs)
    entry.grid(row=row, column=column, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady, sticky=sticky)
    entry.insert(0, default_value)
    return entry

def create_button(parent_container, text: str, row: int, column: int, command, sticky: str = "NSEW", padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0, **kwargs):
    button = tk.Button(parent_container, text=text, command=command, **kwargs)
    button.grid(row=row, column=column, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady, sticky=sticky)
    return button

def create_image(parent_container, path, row: int, column: int, sticky: str = "NSEW"):
    tkinter_image = ImageTk.PhotoImage(image=Image.open(path), master=parent_container)
    image = tk.Label(parent_container, bg="white", image=tkinter_image)
    image.image = tkinter_image
    image.grid(row=row, column=column, sticky=sticky)
    return image

def clear_widgets(container):
    if container is not None:
        for widget in container.winfo_children():
            widget.destroy()