import tkinter as tk
import os
from PIL import Image, ImageTk
import json
import task_a
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from gui_inputs import *

global root
root = tk.Tk()
switch_is_on = True
on = ImageTk.PhotoImage(file = os.path.join(os.path.dirname(__file__), "on.png"))
off = ImageTk.PhotoImage(file = os.path.join(os.path.dirname(__file__), "off.png"))

class InputBox():
    """This takes every variable type and creates a label and a text box for it. //
    It also has methods to capture and store the data before running the simulation"""
    def __init__(self, column, row, label, toggle = False, column_span = 1):
        self.column = column
        self.row = row
        self.label = label
        self.toggle = toggle
        self.column_span = column_span
    
    def switch(self):
        global switch_is_on
        
        if switch_is_on:
            self.toggle.config(image = off)
            switch_is_on = False
        else:
            self.toggle.config(image = on)
            switch_is_on = True

    def place(self):
        input_label = tk.Label(root, text = self.label)
        input_label.grid(column = self.column, row = self.row)
        if self.toggle == True:
            self.toggle = tk.Button(root, image = on, bd = 0, command = self.switch)
            self.toggle.grid(columnspan=2, column=self.column + 1, row = self.row)
        else:
            self.input_box = tk.Entry(root)
            self.input_box.grid(column = self.column + 1, row = self.row)

    def get_input(self):
        data = self.input_box.get()
        return data

class Task():
    """Manages buttons and functions managing the buttons"""
    def __init__(self, task, row, column_span = 10):
        self.task = task
        self.row = row
        self.label = "Task " + (self.task)
        self.column_span = column_span

    def go_to_task(self):
        #Sets up new page for the task specific inputs and elements
        for widgets in root.winfo_children():
            widgets.destroy()
        canvas = tk.Canvas(root, height=500, width=800)
        canvas.grid(columnspan=10, rowspan=10)
        place_logo()
        header = tk.Label(text=self.label)
        header.grid(columnspan=10, column=0, row=1)
        instructions = tk.Label(text="Define your variables before running the script.")
        instructions.grid(columnspan=10, column=0, row=2)
        self.inputs = place_input_boxes(self.label)
        btn_run = tk.Button(root, text="Run Simulation", padx=10, pady=10, fg="black", bg="pink", command=self.run)
        btn_run.grid(columnspan=10, column=0, row=9, sticky = tk.W+tk.E)
        btn_back = tk.Button(root, text="Back to Homepage", padx=10, pady=10, fg="black", bg="pink", command=back)
        btn_back.grid(columnspan=10, column=0, row=10, sticky = tk.W+tk.E)
    
    def run(self):
        #Reads inputs then runs script
        for widgets in root.winfo_children():
            widgets.destroy()
        for input in self.inputs:
            input.get_input()
            #TODO write to file function
        task_a.animated_particle_diffusion(root, back, task_a.steps, task_a.h, task_a.x_min, task_a.x_max, task_a.y_min, task_a.y_max, task_a.fluid_coordinates, task_a.spatial_field, task_a.field_vectors, task_a.fluid_concentrations, task_a.color_dictionary)
    
    def place_button(self):
        #Places the button on the homepage
        btn = tk.Button(root, text=str(self.label), padx=10, pady=10, fg="black", bg="pink", command=self.go_to_task)
        btn.grid(columnspan=10, column=0, row=self.row, sticky = tk.W+tk.E)


def init_buttons(list):
    # Takes a list and element type (Input Box or Button) and generates the element using the respective class
    row_num = 2
    for task in tasks:
        element = Task(task, row_num)
        list.append(element)
        element.place_button()
        row_num += 1


def place_input_boxes(task_label):
    # Reads file and gets all the inputs, then checks for toggle or input box. Places input boxes/toggles
    row_num = 3
    list = []
    for key in Task_Dict[task_label]:
        if Task_Dict[task_label][key][0] == "toggle":
            element = InputBox(4, row_num, key, toggle=True)
        else:
            element = InputBox(4, row_num, key)
        list.append(element)
        element.place()
        row_num += 1


def init_text_boxes(list):
    # Takes a list and element type (Input Box or Button) and generates the element using the respective class
    row_num = 3
    for header in input_headers:
        if (input_headers.index(header) == 0):
            column_num = 0
            row_num = 3
        elif ((input_headers.index(header)+1) % 2 == 0):
            column_num = 2
            row_num = row_num
        else:
            column_num = 0
            row_num += 1
        element = InputBox(column_num, row_num, header)
        list.append(element)
        element.place()
    

def clear_previous_inputs():
    open(os.path.join(os.path.dirname(__file__), 'data.json'), 'w').close()

def back():
    pass
    # TODO: update this
    for widgets in root.winfo_children():
      widgets.destroy()
    main(root)


def task(task_letter):
    #TODO Edit this to allow for multiple tasks
    for widgets in root.winfo_children():
      widgets.destroy()
    init_text_boxes(input_headers, InputBox)
    print("Running task " + str(task_letter))
    #task_a.animated_particle_diffusion(root, back, task_a.steps, task_a.h, task_a.x_min, task_a.x_max, task_a.y_min, task_a.y_max, task_a.fluid_coordinates, task_a.spatial_field, task_a.field_vectors, task_a.fluid_concentrations, task_a.color_dictionary)


def place_logo():
    # places logo and instructions for the gui
    logo = Image.open(os.path.join(os.path.dirname(__file__), 'logo.png'))
    logo = ImageTk.PhotoImage(logo, master = root)
    logo_label = tk.Label(image = logo, master=root)
    logo_label.image = logo
    logo_label.grid(columnspan=10, column=0, row=0)


input_headers = ["Max Time (s)", "Time Step/ dT (s)", "Number of Particles (Integer)", "Diffusivity (Float)", "Velocity Field (True/False)", "Simulation Type (1D/ 2D/ Live)" ]
tasks = ["A", "B", "C", "D", "E"]


def main(root):
    canvas = tk.Canvas(root, height=500, width=900)
    canvas.grid(columnspan=10, rowspan=10)
    place_logo()
    instructions = tk.Label(text="Choose the task you wish to run.")
    instructions.grid(columnspan=10, column=0, row=1)
    buttons = []
    init_buttons(buttons)
    root.mainloop()

if __name__ == "__main__":
    main(root)