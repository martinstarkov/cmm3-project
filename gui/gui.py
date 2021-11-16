import tkinter as tk
from tkinter.filedialog import askopenfile
import os
from PIL import Image, ImageTk
import json
import pathlib

global root
root = tk.Tk()

# Global variables for toggle switch
switch_is_on = True
on = ImageTk.PhotoImage(file=os.path.join(os.path.dirname(__file__), "on.png"))
off = ImageTk.PhotoImage(file=os.path.join(
    os.path.dirname(__file__), "off.png"))



class InputBox():
    """This takes every variable type and creates a label and a text box for it. //
    It also has methods to capture and store the data before running the simulation"""

    def __init__(self, column, row, label, data_type, default, column_span=1):
        self.column = column
        self.row = row
        self.label = label
        self.data_type = data_type
        self.default = default
        self.column_span = column_span

    def place(self):
        # Places the button/toggle in the GUI window.
        input_label = tk.Label(root, text=self.label)
        input_label.grid(column=self.column, row=self.row)
        self.input_box = tk.Entry(root)
        self.input_box.insert(0, self.default)
        self.input_box.grid(column=self.column + 1, row=self.row)

    def get_input(self):
        # Takes the input from the entry box and stores it as a class variable.
        if self.data_type == 'integer':
            data = self.input_box.get()
            return int(data)
        else:
            data = self.input_box.get()
            return float(data)

class Toggle():
    def __init__(self, column, row, label, default,  status=True):
        self.column = column
        self.row = row 
        self.label = label
        self.default = default
        self.status = status
    
    def add(self):
        pass

    def remove(self):
        pass
    
    def place(self):
        # Places the button/toggle in the GUI window.
        input_label = tk.Label(root, text=self.label)
        input_label.grid(column=self.column, row=self.row)
        self.button = tk.Button(root, image=on, bd=0, command=self.toggle)
        self.button.grid(columnspan=1, column=self.column + 1, row=self.row)
        self.add()

    def toggle(self):
        self.status = not self.status
        if self.status:
            self.button.config(image=on)
            self.add()
        else:
            self.button.config(image=off)
            self.remove()
    
    def get_input(self):
        if self.status:
            return True
        else:
            return False
    
class RectangleToggle(Toggle):
    # child class constructor
    def __init__(self, column, row, label, default,  status=True):
        # call parent class constructor
        Toggle.__init__(self, column, row, label, default,  status=True)

    def add(self):
        pass

    def remove(self):
        pass

class CircleToggle(Toggle):
    def __init__(self, column, row, label, default,  status=True):
        # call parent class constructor
        Toggle.__init__(self, column, row, label, default,  status=True)

    def add(self):
        pass

    def remove(self):
        pass

class VelocityFieldToggle(Toggle):
    def __init__(self, column, row, label, default,  status=True):
        # call parent class constructor
        Toggle.__init__(self, column, row, label, default,  status=True)
        self.file = None
        self.file_path = None
    
    def open_file(self):
        # handles the activity of the open file button. stores the path of the file as a variable and stores it as a class variable.
        self.file = askopenfile(mode='r', filetypes=[
                                ('velocity field', '*.dat')]).name
        if self.file is not None:
            self.file_path = str(pathlib.PurePath(str(self.file)))
            success_text = tk.Label(text=str(self.file_path))
            success_text.grid(
                columnspan=10, column=self.column + 3, row=self.row)

    def add(self):
        self.browse = tk.Button(
                    root, text='Open File', command=lambda: self.open_file())
        self.browse.grid(
                    columnspan=1, column=self.column + 2, row=self.row)
    
    def remove(self):
        self.browse.destroy()


class Task():
    """Manages each tasks landing page and inputs."""

    def __init__(self, label, row, column_span=10):
        self.label = label
        self.row = row
        self.column_span = column_span

    def go_to_task(self):
        # Clears elements on the page and replaces them with task appropriate elements.
        for widgets in root.winfo_children():
            widgets.destroy()
        canvas = tk.Canvas(root, height=500, width=800)
        canvas.grid(columnspan=10, rowspan=10)
        place_logo()
        header = tk.Label(text=self.label)
        header.grid(columnspan=10, column=0, row=1)
        instructions = tk.Label(
            text="Define your variables before running the script.")
        instructions.grid(columnspan=10, column=0, row=2)

        # Create Input Boxes
        self.inputs, self.input_dict = place_input_boxes(self.label)

        btn_run = tk.Button(root, text="Run Simulation", padx=10,
                            pady=10, fg="black", bg="pink", command=self.run)
        btn_run.grid(columnspan=10, column=0, row=self.inputs[-1].row + 2, sticky=tk.W+tk.E)
        btn_back = tk.Button(root, text="Back to Homepage",
                             padx=10, pady=10, fg="black", bg="pink", command=back)
        btn_back.grid(columnspan=10, column=0, row=self.inputs[-1].row + 3, sticky=tk.W+tk.E)

    def run(self):
        # Handles activity of the Run Button, stores user inputs in a data.json before running script.
        dict = self.input_dict
        for input in self.inputs:
            value = input.get_input()
            label = input.label
            dict[label][2] = value
        for input_box in self.inputs:
            if (input_box.label == 'Velocity Field'):
                dict['File Path'][2] = input_box.file_path
        # Storing inputs in JSON File.
        with open(os.path.join(os.path.dirname(__file__), 'input_boxes.json')) as json_file:
            dictionary = json.load(json_file)
        dictionary[self.label] = dict
        with open(os.path.join(os.path.dirname(__file__), 'input_boxes.json'), 'w') as json_file:
            json.dump(dictionary, json_file, indent=4)
        for widgets in root.winfo_children():
            widgets.destroy()
        # TODO replace this with each tasks function.

    def place_button(self):
        # Places the task button on the main landing page
        btn = tk.Button(root, text=str(self.label), padx=10,
                        pady=10, fg="black", bg="pink", command=self.go_to_task)
        btn.grid(columnspan=10, column=0, row=self.row, sticky=tk.W+tk.E)


def main_menu_buttons(list):
    # Reads the input boxes json file and populates the main menu.
    with open(os.path.join(os.path.dirname(__file__), 'input_boxes.json')) as json_file:
            tasks = json.load(json_file)
    #to avoid interference with logo
    row_num = 2
    for task in tasks:
        element = Task(task, row_num)
        list.append(element)
        element.place_button()
        row_num += 1


def place_input_boxes(task_label):
    # Reads input boxes file, then checks for toggle or input box. Places input boxes/toggles.
    row_num = 3
    input_boxes = []
    with open(os.path.join(os.path.dirname(__file__), 'input_boxes.json')) as json_file:
        dictionary = json.load(json_file)
    task_dict = dictionary[task_label] #finding the specific dictionary for the task.
    # Creating InputBox class instances
    for key in task_dict:
        if task_dict[key][0] == "toggle":
            if task_dict[key][3] == "velocity_field":
                element = VelocityFieldToggle(4, row_num, key, task_dict[key][1])
            elif task_dict[key][3] == "circle":
                element = CircleToggle(4, row_num, key, task_dict[key][1])
            elif task_dict[key][3] == "rectangle":
                element = RectangleToggle(4, row_num, key, task_dict[key][1])
            # element = InputBox(4, row_num, key, task_dict[key][0], task_dict[key][1], toggle=True)
        elif key == "File Path":
            pass
        else:
            element = InputBox(4, row_num, key, task_dict[key][0], task_dict[key][1])
        input_boxes.append(element)
        element.place()
        row_num += 1
    return input_boxes, task_dict


def back():
    # Handles the activity of the back button
    for widgets in root.winfo_children():
        widgets.destroy()
    main(root)


def place_logo():
    # places logo and instructions for the gui
    logo = Image.open(os.path.join(os.path.dirname(__file__), 'logo.png'))
    logo = ImageTk.PhotoImage(logo, master=root)
    logo_label = tk.Label(image=logo, master=root)
    logo_label.image = logo
    logo_label.grid(columnspan=10, column=0, row=0)


def main(root):
    # Generates the landing page.
    canvas = tk.Canvas(root, height=500, width=900)
    canvas.grid(columnspan=10, rowspan=30)
    place_logo()
    instructions = tk.Label(text="Choose the task you wish to run.")
    instructions.grid(columnspan=10, column=0, row=1)
    buttons = []
    main_menu_buttons(buttons)
    root.mainloop()


if __name__ == "__main__":
    main(root)
