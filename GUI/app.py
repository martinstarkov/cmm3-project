import tkinter as tk
import os
from PIL import Image, ImageTk
import json

class InputBox():
    """This takes every variable type and creates a label and a text box for it. //
    It also has methods to capture and store the data before running the simulation"""
    def __init__(self, column, row, label, column_span = 1):
        super(inputBox, self).__init__()
        self.column = column
        self.row = row
        self.label = label
        self.column_span = column_span

    def create_input_box(self):
        input_label = tk.Label(root, text = self.label)
        input_label.grid(column = self.column, row = self.row)
        self.input_box = tk.Entry(root)
        self.input_box.grid(column = self.column + 1, row = self.row)

    def get_input(self):
        data = self.input_box.get()
        return data
        
def init_text_boxes(list):
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
        box = InputBox(column_num, row_num, header)
        list.append(box)
        box.create_input_box()

def store_data():
    inputs = {
        "max_time": int(input_boxes[0].get_input()),
        "time_step": float(input_boxes[1].get_input()),
        "num_particles": int(input_boxes[2].get_input()),
        "diffusivity": float(input_boxes[3].get_input()),
        "velocity_field": bool(input_boxes[4].get_input()),
        "simulation_type": input_boxes[5].get_input(),
    }
    json_object = json.dumps(inputs)
    with open("data.json", "a") as outfile:
        outfile.write(json_object)
    

def run_script():
	script = os.system('python active_brownian.py')

def clear_previous_inputs():
    open('data.json', 'w').close()

root = tk.Tk()

canvas = tk.Canvas(root, height=500, width=800)
canvas.grid(columnspan=10, rowspan=10)

#logo
logo = Image.open('logo.png')
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(image = logo)
logo_label.image = logo
logo_label.grid(columnspan=2, column=1, row=0)

#instructions
instructions = tk.Label(root, text="Variable and Flexible Diffusion and Advection Simulation Tool. Change the Variables and Settings before running.")
instructions.grid(columnspan=10, column=0, row=1)

input_headers = ["Max Time (s)", "Time Step/ dT (s)", "Number of Particles (Integer)", "Diffusivity (Float)", "Velocity Field (True/False)", "Simulation Type (1D/ 2D/ Live)" ]

#buttons
run_script = tk.Button(root, text="Run Simulation", padx=10, pady=10, fg="black", bg="pink", command=run_script)
run_script.grid(columnspan=4, column=0, row=6, sticky = tk.W+tk.E)
clear = tk.Button(root, text="Clear Previous Inputs", padx=10, pady=10, fg="black", bg="pink", command=clear_previous_inputs)
clear.grid(columnspan=4, column=0, row=7, sticky = tk.W+tk.E)
clear = tk.Button(root, text="Store New Inputs", padx=10, pady=10, fg="black", bg="pink", command=store_data)
clear.grid(columnspan=4, column=0, row=8, sticky = tk.W+tk.E)


if __name__ == '__main__':
    input_boxes = []
    init_text_boxes(input_boxes)
    root.mainloop()
