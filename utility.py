from PIL import Image, ImageTk
from tkinter import messagebox
from typing import List, Dict
import matplotlib.pyplot as plt
import matplotlib.colors
import numpy.typing as npt
import numpy as np
import tkinter as tk
import os

# TODO: Add short description at the top of this file.

# Utility function for reading and checking column data from a data file. 
def read_data_file(file, *columns):
    data = []
    for column in columns:
        try:
            # Read the given columns out of the file and append them to a list.
            data.append(np.genfromtxt(file, usecols=tuple(column), invalid_raise=True))
        except:
            print("Could not retrieve " + str(column) + " columns from file " + str(os.path.basename(file)))
            return None
    return data

# Converts a relative file path to an absolute file object.
def relative_to_absolute(directory, path):
    return os.path.join(os.path.dirname(directory), path)

# Returns a heatmap figure used for plotting concentrations.
def create_heatmap(data, color_dictionary: Dict[str, any], animated: bool, min: npt.ArrayLike, max: npt.ArrayLike, x_label: str, y_label: str):
    plt.close('all')
    figure, axes = plt.figure(), plt.axes()
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)
    heatmap = axes.imshow(data, animated=animated, extent=(min[0], max[0], min[1], max[1]))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [tuple(pair) for pair in color_dictionary])
    heatmap.set_cmap(cmap)
    figure.colorbar(matplotlib.cm.ScalarMappable(cmap=cmap))
    return figure, axes, heatmap

# Sets up a plot with the desired parameters.
def configure_plot(title: str, x_label: str, y_label: str, scale: str):
    plt.title(title); plt.legend(); plt.grid()
    plt.yscale(scale); plt.xscale(scale)
    plt.xlabel(x_label); plt.ylabel(y_label)

# Utility functions for easily creating gridded tkinter widgets.

# Creates a tkinter window with a given geometry (size and offset).
def create_root(geometry):
    root = tk.Tk()
    root.geometry(geometry)
    root.configure(bg="white")
    set_grid_sizes(root, [100], [100], uniform_row="root", uniform_column="root")
    return root

# Sets the relative sizes of the rows and columns of a tkinter container grid.
# The rows and columns lists define the weight placed on their respective index row or column.
# For example:
# rows=[20, 60, 20] would mean that 20% of the height of the container is the first row, 60% the second, and 20% the third.
# The values inside of these lists do not necessarily have to add up to 100 as they are relative weights.
def set_grid_sizes(container, rows: List[int] = [], columns: List[int] = [], uniform_row: str = "", uniform_column: str = ""):
    for row, size in enumerate(rows):
        container.grid_rowconfigure(row, weight=size, uniform=uniform_row)
    for column, size in enumerate(columns):
        container.grid_columnconfigure(column, weight=size, uniform=uniform_column)

# Creates a sub container inside a tkinter parent container.
def create_frame(parent_container, row: int, column: int, sticky: str = "NSEW"):
    frame = tk.Frame(parent_container, bg="white", bd=0)
    frame.grid(row=row, column=column, sticky=sticky)
    return frame

# Creates a tkinter label for written text.
def create_label(parent_container, text: str, row: int, column: int, sticky: str = "NSEW", padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0):
    label = tk.Label(parent_container, text=text, bg="white")
    label.grid(row=row, column=column, padx=0, pady=0, ipadx=0, ipady=0, sticky=sticky)
    return label

# Creates a tkinter entry object for retrieving user inputs.
def create_entry(parent_container, default_value, row: int, column: int, sticky: str = "NSEW", padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0, **kwargs):
    entry = tk.Entry(parent_container, bg="white", justify="center", **kwargs)
    entry.grid(row=row, column=column, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady, sticky=sticky)
    entry.insert(0, default_value)
    return entry

# Retrieves the raw value(s) of an entry.
# If entry is a tkinter widget, retrieve the value inside of it.
# If entry is boolean or string, return it as is.
# If entry is a list of entries, recursively go through the above steps for each element.
def get_entry( entry):
    if isinstance(entry, list):
        inner_entries = []
        for inner_entry in entry:
            # Cycle through the list recursively.
            inner_entries.append(get_entry(inner_entry))
        return inner_entries
    elif not isinstance(entry, bool) and not isinstance(entry, str):
        return entry.get()
    # Boolean and string entries are stored as-is and do not need to be retrieved.
    else:
        return entry

# Recrusively parses an entry and casts it to the correct type based on its respective defaults array.
def parse_entry(defaults, entry):
    if isinstance(entry, list):
        inner_entries = []
        for index, inner_entry in enumerate(entry):
            inner_entries.append(parse_entry(defaults[index], inner_entry))
        return inner_entries
    else:
        try:
            return type(defaults)(entry)
        except Exception as e:
            # Let the user know if the input they made has an invalid type.
            messagebox.showerror('error', e)
            # None is used for invalidating data for invalid entry types.
            return None
        
# Creates a tkinter button object.
def create_button(parent_container, text: str, row: int, column: int, command, sticky: str = "NSEW", padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0, **kwargs):
    button = tk.Button(parent_container, text=text, command=command, **kwargs)
    button.grid(row=row, column=column, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady, sticky=sticky)
    return button

# Creates a tkinter image object for the user interface logo.
def create_image(parent_container, path, row: int, column: int, sticky: str = "NSEW"):
    tkinter_image = ImageTk.PhotoImage(image=Image.open(path), master=parent_container)
    image = tk.Label(parent_container, bg="white", image=tkinter_image)
    image.image = tkinter_image
    image.grid(row=row, column=column, sticky=sticky)
    return image

# Clears all the tkinter widgets inside of a given container.
def clear_widgets(container):
    if container is not None:
        for widget in container.winfo_children():
            widget.destroy()
            

# Returns true if condition is met, otherwise prompts user with an error message and returns false.
def check(condition: bool, message: str):
    return True if condition else not bool(messagebox.showinfo("Field error", message))

# Returns true if the dictionary or list contains the given element.
# Checks through the object recursively.
def contains_value(dictionary_or_list, element: any):
    if isinstance(dictionary_or_list, list):
        if element in dictionary_or_list: return True
        for v in dictionary_or_list:
            if isinstance(v, list) or isinstance(v, dict):
                if contains_value(v, element):
                    return True
    elif isinstance(dictionary_or_list, dict):
        if element in dictionary_or_list.values(): return True
        for _, v in dictionary_or_list.items():
            if isinstance(v, list) or isinstance(v, dict):
                if contains_value(v, element):
                    return True
    return False