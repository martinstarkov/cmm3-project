from PIL import Image, ImageTk
from tkinter import messagebox
from typing import List
import matplotlib.pyplot as plt
import matplotlib.colors
import numpy.typing as npt
import numpy as np
import tkinter as tk
import os

"""
This file contains general utility functions used throughout the project.
None of these functions have dependency on other project files.
"""

# Variable which ensures consistent background color across widgets.
background_color = "white"


def read_data_file(file: any, *columns):
    """Function for reading and checking column data from a data file.
    Args:
        columns: List of column indexes to read into the returned list.
    Returns:
        A list of data in the specified columns, or a list of None if columns are not found. 
    """
    data = []
    for column in columns:
        try:
            # Read the given columns out of the file and append them to a list.
            data.append(np.genfromtxt(file, usecols=tuple(column), invalid_raise=True))
        except:
            print("Could not retrieve " + str(column) + " columns from file " + str(os.path.basename(file)))
            return [None for column in columns]
    return data


def relative_to_absolute(directory: any, path: str):
    """Converts relative file paths to absolute.
    Args:
        directory: Directory of the file.
        path:      Name of the file.
    Returns:
        A relative file path converted to an absolute file object.
    """
    return os.path.join(os.path.dirname(directory), path)


def create_heatmap(data: npt.ArrayLike, color_list: List[any], 
                   animated: bool, min: npt.ArrayLike, max: npt.ArrayLike, 
                   x_label: str, y_label: str):
    """Creates a heatmap figure used for plotting scalar fields.
    Args:
        data:       Scalar field to be plotted.
        color_list: List of integer and color intervals used for determining
                    the color gradient of the figure's color bar.
        animated:   Whether or not the heatmap can be animated.
        min:        [x, y] axis bounds
        max:        [x, y] axis bounds.
        x_label:    X axis label.
        y_label:    Y axis label.
    Returns:
        A figure, its axes, and the created heatmap.
    """
    # Close all previous plots to improve performance.
    plt.close('all')
    figure, axes = plt.figure(), plt.axes()
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)
    heatmap = axes.imshow(data, animated=animated,
                          extent=(min[0], max[0], min[1], max[1]))
    # Turn the lists inside the color_list into 
    # tuples as required by the from_list function.
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "", [tuple(pair) for pair in color_list])
    heatmap.set_cmap(cmap)
    figure.colorbar(matplotlib.cm.ScalarMappable(cmap=cmap))
    return figure, axes, heatmap


def configure_plot(title: str, x_label: str, y_label: str, scale: str):
    """Sets up a plot with the desired parameters."""
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.yscale(scale)
    plt.xscale(scale)
    plt.xlabel(x_label)
    plt.ylabel(y_label)


"""
The utility functions below are primarily there to reduce boilerplate 
code for interacting with and creating gridded Tkinter widgets (GUI).
"""


def create_root(geometry: str):
    """Creates a Tkinter window with a given geometry (size and offset).
    Args:
        geometry: Format is "[width]x[height]+[offset_x]+[offset_y]" 
                  where the [value] are replaced with the appropriate value.
                  Offsets from top right of monitor.
    Returns:
        Tkinter root window.
    """
    root = tk.Tk()
    root.geometry(geometry)
    root.configure(bg=background_color)
    # Make the root one big full sized grid.
    set_grid_sizes(root, [100], [100], uniform_row="root",
                   uniform_column="root")
    return root


def set_grid_sizes(container: any, rows: List[int] = [], columns: List[int] = [], 
                   uniform_row: str = "", uniform_column: str = ""):
    """Sets the relative sizes of the rows and columns of a Tkinter container grid.
    
    The rows and columns lists define the weight placed 
    on their respective index row or column.
    Example:
        rows=[20, 60, 20] would mean that '20%' of the height of the
        container is the first row, '60%' the second, and '20%' the third.
        The values inside of these lists do not necessarily 
        need to add up to 100 as they are just relative weights.
    Args:
        container:      Tkinter container for which to modify the grid.
        rows:           Relative row heights to use.         Defaults to [] (meaning ignored).
        columns:        Relative column width to use.        Defaults to [] (meaning ignored).
        uniform_row:    Key for rows of uniform height to use.   Defaults to "" (meaning ignored).
        uniform_column: Key for columns of uniform width to use. Defaults to "" (meaning ignored).
    """
    for row, size in enumerate(rows):
        container.grid_rowconfigure(row, weight=size, uniform=uniform_row)
    for column, size in enumerate(columns):
        container.grid_columnconfigure(column, weight=size, uniform=uniform_column)


def create_frame(parent_container: any, row: int, column: int, sticky: str = "NSEW"):
    """Creates a Tkinter sub container inside a parent container.
    Args:
        parent_container: Container in which to create the frame.
        row:              Row in the parent container to use for the frame.
        column:           Column in the parent container to use for the frame.
        sticky:           Stretching properties of the frame. Defaults to "NSEW".
    Returns:
        Tkinter frame widget.
    """
    frame = tk.Frame(parent_container, bg=background_color, bd=0)
    frame.grid(row=row, column=column, sticky=sticky)
    return frame


def create_label(parent_container: any, text: str, 
                 row: int, column: int, sticky: str = "NSEW", 
                 padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0):
    """Creates a Tkinter label for written text.
    Args:
        parent_container: Container in which to create the label.
        text:             Label text content.
        row:              Row in the parent container to use for the label.
        column:           Column in the parent container to use for the label.
        sticky:           Stretching properties of the label. Defaults to "NSEW".
        padx:             External x direction padding of the label. Defaults to 0.
        pady:             External y direction padding of the label. Defaults to 0.
        ipadx:            Internal x direction padding of the label. Defaults to 0.
        ipady:            Internal y direction padding of the label. Defaults to 0.
    Returns:
        Tkinter label widget.
    """
    label = tk.Label(parent_container, text=text, bg=background_color)
    label.grid(row=row, column=column, padx=0, pady=0, ipadx=0, ipady=0, sticky=sticky)
    return label


def create_entry(parent_container: any, default_value: any, 
                 row: int, column: int,
                 sticky: str = "NSEW", padx: int = 0, pady: int = 0, 
                 ipadx: int = 0, ipady: int = 0, **kwargs):
    """Creates a Tkinter entry box for retrieving user inputs.
    Args:
        parent_container: Container in which to create the entry.
        default_value:    Default value to place in the entry.
        row:              Row in the parent container to use for the entry.
        column:           Column in the parent container to use for the entry.
        sticky:           Stretching properties of the entry. Defaults to "NSEW".
        padx:             External x direction padding of the entry. Defaults to 0.
        pady:             External y direction padding of the entry. Defaults to 0.
        ipadx:            Internal x direction padding of the entry. Defaults to 0.
        ipady:            Internal y direction padding of the entry. Defaults to 0.
        **kwargs:         Any other keyword arguments to be passed to the entry.
    Returns:
        Tkinter entry widget.
    """
    entry = tk.Entry(parent_container, bg=background_color, justify="center", **kwargs)
    entry.grid(row=row, column=column, padx=padx, pady=pady,
               ipadx=ipadx, ipady=ipady, sticky=sticky)
    entry.insert(0, default_value)
    return entry


def get_entry(entry: any):
    """
    Retrieves the raw value(s) of an entry.
    If entry is a Tkinter widget, retrieve the value inside of it.
    If entry is boolean or string, return it as is.
    If entry is a list of entries, recursively go through the above steps for each element.
    """
    if isinstance(entry, list):
        inner_entries = []
        for inner_entry in entry:
            # Cycle through the list recursively.
            inner_entries.append(get_entry(inner_entry))
        return inner_entries
    elif not isinstance(entry, bool) and not isinstance(entry, str):
        # Retrieve the value in the Tkinter widget.
        return entry.get()
    else:
        # Boolean and string entries are stored as-is 
        # and do not need to be retrieved.
        return entry


def parse_entry(defaults: any, entry: any):
    """
    Recrusively parses an entry and casts it to the 
    correct type based on its respective default value.
    Args:
        defaults: Default value corresponding to the entry.
                  Used for determining the type of the entry.
        entry:    Entry to parse the outputs of.
    Returns:
        The value in the entry converted to the correct type,
        None if it cannot be converted.
    """
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
            # None is used for invalidating data for invalid entry types,
            # preventing buttons from moving on until the input is fixed.
            return None


def create_button(parent_container: any, text: str, row: int, column: int, 
                  command: any, sticky: str = "NSEW", padx: int = 0, pady: int = 0, 
                  ipadx: int = 0, ipady: int = 0, **kwargs):
    """
    Args:
        parent_container: Container in which to create the button.
        text:             Cext content inside of the button.
        row:              Row in the parent container to use for the button.
        column:           Column in the parent container to use for the button.
        command:          Function to be run by the button once it is pressed.
        sticky:           Stretching properties of the button. Defaults to "NSEW".
        padx:             External x direction padding of the button. Defaults to 0.
        pady:             External y direction padding of the button. Defaults to 0.
        ipadx:            Internal x direction padding of the button. Defaults to 0.
        ipady:            Internal y direction padding of the button. Defaults to 0.
        **kwargs:         Any other keyword arguments to be passed to the button.
    Returns:
        Tkinter button widget.
    """
    button = tk.Button(parent_container, text=text, command=command, **kwargs)
    button.grid(row=row, column=column, padx=padx, pady=pady,
                ipadx=ipadx, ipady=ipady, sticky=sticky)
    return button


def create_image(parent_container: any, path: any, 
                 row: int, column: int, sticky: str = "NSEW"):
    """
    Args:
        parent_container: Container in which to create the image.
        path:             Path to the image file.
        row:              Row in the parent container to use for the image.
        column:           Column in the parent container to use for the image.
        sticky:           Stretching properties of the image. Defaults to "NSEW".

    Returns:
        Tkinter image object.
    """
    tkinter_image = ImageTk.PhotoImage(
        image=Image.open(path), master=parent_container)
    image = tk.Label(parent_container, bg=background_color, image=tkinter_image)
    image.image = tkinter_image
    image.grid(row=row, column=column, sticky=sticky)
    return image


def clear_widgets(container: any):
    """Clears all the Tkinter widgets inside of a given container.
    Args:
        container: Container to clear widgets from.
    """
    if container is not None:
        for widget in container.winfo_children():
            widget.destroy()
            

def check(condition: bool, message: str):
    """Condition validation function for user entry checks.
    Args:
        condition: Condition to check.
        message:   Message to display if condition is not met.
    Returns:
        True if condition is met, false otherwise 
        (and prompts the user with an error message).
    """
    return True if condition else not bool(messagebox.showinfo("Field error", message))


def contains_value(dictionary_or_list: any, element: any):
    """Recrusively checks if an iterable object contains an element.
    Args:
        dictionary_or_list: Dictionary or List object to check through.
        element:            Any variable to check for.
    Returns:
        True if the dictionary or list contains the given element, false otherwise.
    """
    # This is a fairly self-explanatory recursive search algorithm.
    if isinstance(dictionary_or_list, list):
        if element in dictionary_or_list: return True
        for v in dictionary_or_list:
            if isinstance(v, list) or isinstance(v, dict):
                if contains_value(v, element): return True
    # The reason it is repeated twice is because lists
    # and dictionaries differ in how they are iterated.
    elif isinstance(dictionary_or_list, dict):
        if element in dictionary_or_list.values(): return True
        for _, v in dictionary_or_list.items():
            if isinstance(v, list) or isinstance(v, dict):
                if contains_value(v, element): return True
    return False