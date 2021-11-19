import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
from matplotlib import animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sys import platform as sys_pf
import matplotlib.pyplot as plt
import numpy as np
import os
import json
import simulation

# TODO: Add requirements.txt file.
# TODO: Add short description at the top of this file.

# Tkinter embedded plot fix for macOS.
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")
    
X = 0
Y = 0

# Utility functions for easily creating gridded tkinter widgets.

def set_grid_sizes(container, rows=[], columns=[], uniform_row="", uniform_column=""):
    for row, size in enumerate(rows):
        container.grid_rowconfigure(row, weight=size, uniform=uniform_row)
    for column, size in enumerate(columns):
        container.grid_columnconfigure(column, weight=size, uniform=uniform_column)
        
def create_frame(parent_container, row, column, sticky="NSEW"):
    frame = tk.Frame(parent_container, bg="white", bd=0)
    frame.grid(row=row, column=column, sticky=sticky)
    return frame

def create_label(parent_container, text, row, column, sticky="NSEW", padx=0, pady=0, ipadx=0, ipady=0):
    label = tk.Label(parent_container, text=text, bg="white")
    label.grid(row=row, column=column, padx=0, pady=0, ipadx=0, ipady=0, sticky=sticky)
    return label

def create_entry(parent_container, default_value, row, column, sticky="NSEW", padx=0, pady=0, ipadx=0, ipady=0, **kwargs):
    entry = tk.Entry(parent_container, bg="white", justify="center", **kwargs)
    entry.grid(row=row, column=column, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady, sticky=sticky)
    entry.insert(0, default_value)
    return entry

def create_button(parent_container, text, row, column, command, sticky="NSEW", padx=0, pady=0, ipadx=0, ipady=0, **kwargs):
    button = tk.Button(parent_container, text=text, command=command, **kwargs)
    button.grid(row=row, column=column, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady, sticky=sticky)
    return button

def create_image(parent_container, path, row, column, sticky="NSEW"):
    tkinter_image = ImageTk.PhotoImage(image=Image.open(path), master=parent_container)
    image = tk.Label(parent_container, bg="white", image=tkinter_image)
    image.image = tkinter_image
    image.grid(row=row, column=column, sticky=sticky)
    return image

def clear_widgets(container):
    if container is not None:
        for widget in container.winfo_children():
            widget.destroy()

# User interface object to be called at the beginning of the program creation.
class UserInterface(object):
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        # Create Tkinter window of given size and grid configuration.
        self.root = tk.Tk()
        self.root.geometry("700x700+0+0")
        self.root.configure(bg="white")
        set_grid_sizes(self.root, [100], [100], uniform_row="root", uniform_column="root")
        self.frame = create_frame(self.root, 0, 0)
        set_grid_sizes(self.frame, [20, 7, 66, 7], [20, 60, 20], uniform_row="frame", uniform_column="frame")
        self.container = None
        # Load JSON file into a data object and populate the window.
        with open(self.json_file_path) as json_file:
            self.data = json.load(json_file)
            self.create_header()
            self.create_menu_buttons()
            self.root.mainloop()
        
    def create_header(self):
        # Create the GUI logo.
        create_image(self.frame, os.path.join(os.path.dirname(__file__), "gui/logo.png"), 0, 1)
        # Create the GUI label (modified by main menu buttons when they are pressed).
        self.label_text = "Please choose a mode of operation."
        self.label = create_label(self.frame, self.label_text, 1, 1)
    
    # Creates the main menu navigation buttons.
    def create_menu_buttons(self):
        clear_widgets(self.container)
        self.label["text"] = self.label_text
        self.create_container()
        set_grid_sizes(self.container, [33, 33, 33], [100], uniform_row="container", uniform_column="container")
        # Create individual buttons in the container.
        CustomConditions("Custom Conditions", self, 0)
        ValidationTasks("Validation Tasks", self, 1)
        EngineeringSpill("Engineering Spill", self, 2)

    # Creates the container cell.
    def create_container(self):
        self.container = create_frame(self.frame, 2, 1)
        
    def create_plot(self, figure, reset_function, back_function):
        canvas = FigureCanvasTkAgg(figure, master=self.container)
        canvas.get_tk_widget().grid(row=0, column=0, padx=0, pady=0)
        
        create_button(self.container, "Reset Plot", 1, 0, reset_function, pady=(5, 0), ipady=15, fg="black", bg="pink")
        create_button(self.container, "Back", 2, 0, back_function, pady=(5, 0), ipady=15, fg="black", bg="pink")
        
        set_grid_sizes(self.container, [80, 4, 4], [100])
        return canvas
      
# Abstract class which represents an input row.
class InputField(object):
    # Field info contains the input field info from the JSON file.
    def __init__(self, ui, field_info, row):
        self.field_info = field_info
        # Used for storing the entry fields of the given input field.
        self.entries = []
        # Create a sub container for the input field and label.
        self.sub_container = create_frame(ui.container, row, 0)
        set_grid_sizes(self.sub_container, columns=[50, 50], uniform_row="sub_container", uniform_column="sub_container")
        
    def create(self, text):
        self.key = text
        create_label(self.sub_container, text, 0, 0)


class NumericInputField(InputField):
    def create(self, text):
        super().create(text)
        # Creates a simple input parameter box with a default value.
        self.entries = create_entry(self.sub_container, self.field_info["default"], 0, 1, width=20)


class DomainInputField(InputField):
    def create(self, text):
        super().create(text)
        defaults = self.field_info["default"]
        domain_container = create_frame(self.sub_container, 0, 1)
        
        create_label(domain_container, "≤ x ≤", 0, 1)
        create_label(domain_container, "≤ y ≤", 1, 1)
        self.entries.append([create_entry(domain_container, defaults[0][X], 0, 0, sticky="EW", width=5),
                             create_entry(domain_container, defaults[0][Y], 1, 0, sticky="EW", width=5)])
        self.entries.append([create_entry(domain_container, defaults[1][X], 0, 2, sticky="EW", width=5),
                             create_entry(domain_container, defaults[1][Y], 1, 2, sticky="EW", width=5)])
        
        set_grid_sizes(domain_container, [50, 50], [40, 20, 40])
        
class CellInputField(InputField):
    def create(self, text):
        super().create(text)
        defaults = self.field_info["default"]
        cell_container = create_frame(self.sub_container, 0, 1)
        
        create_label(cell_container, u'Nₓ =', 0, 0)
        create_label(cell_container, u'Nᵧ =', 1, 0)
        self.entries.append([create_entry(cell_container, defaults[X], 0, 1, sticky="EW", width=5),
                             create_entry(cell_container, defaults[Y], 1, 1, sticky="EW", width=5)])
        
        set_grid_sizes(cell_container, [50, 50], [15, 85])

class ToggleInputField(InputField):
    def create(self, text):
        super().create(text)
        self.defaults = self.field_info["default"]
        container = create_frame(self.sub_container, 0, 1)
        set_grid_sizes(container, [100], [20, 80], uniform_column="toggle_container")
        self.toggle_container = create_frame(container, 0, 0)
        set_grid_sizes(self.toggle_container, [100], [100])
        self.input_container = create_frame(container, 0, 1)
        self.state = tk.BooleanVar(value=self.defaults[0])
        toggle_button = tk.Checkbutton(self.toggle_container, bg="white", activebackground="white", \
                                       variable=self.state, onvalue=True, offvalue=False, command=self.update)
        toggle_button.grid(row=0, column=0, sticky="NSEW")
        if not self.state.get(): # By default, checkbutton starts checked.
            toggle_button.deselect()
        self.entries = [self.state.get()]
        self.update()

    # Updates the state of the widget containers and entry state.
    def update(self):
        if self.state.get():
            self.appear()
        else:
            self.disappear()
        self.entries[0] = self.state.get()
    
    # Nothing for boolean toggles, can be overriden in child classes.
    def appear(self):
        pass
        
    # Removes all the non toggle button widgets.
    def disappear(self):
        clear_widgets(self.input_container)
        self.entries = [self.state.get()]

class VelocityInputField(ToggleInputField):
    def appear(self):
        set_grid_sizes(self.input_container, columns=[100])
        file_container = create_frame(self.input_container, 0, 0)
        
        create_button(file_container, "Open File", 0, 0, self.open_file)

        self.path_label = create_label(file_container, "File: " + self.defaults[1], 1, 0)
        self.entries.append(os.path.join(os.path.dirname(__file__), self.defaults[1]))
        
        set_grid_sizes(file_container, [50, 50], [100])
        
    def open_file(self):
        file = askopenfile(mode='r', filetypes=[('Velocity Field Data Files', '*.dat')])
        if file is not None:
            self.path_label["text"] = "File: " + os.path.basename(file.name)
            self.entries[1] = file.name
            file.close()
    
class CircleInputField(ToggleInputField):
    def appear(self):
        set_grid_sizes(self.input_container, columns=[50, 50])
        concentration_container = create_frame(self.input_container, 0, 0)
        circle_container = create_frame(self.input_container, 0, 1)
        
        create_label(concentration_container, "φ =", 1, 0)
        create_label(concentration_container, "", 0, 0)
        create_label(circle_container, "x", 0, 0)
        create_label(circle_container, "y", 0, 1)
        create_label(circle_container, "radius", 0, 2)
        
        self.entries.append(create_entry(concentration_container, self.defaults[1], 1, 1, sticky="EW", padx=(0, 5), width=5))
        self.entries.append([create_entry(circle_container, self.defaults[2][X], 1, 0, sticky="EW", width=5),
                             create_entry(circle_container, self.defaults[2][Y], 1, 1, sticky="EW", width=5)])
        self.entries.append(create_entry(circle_container, self.defaults[3], 1, 2, sticky="EW", width=5))
        
        set_grid_sizes(concentration_container, [50, 50], [40, 60])
        set_grid_sizes(circle_container, [50, 50], [33, 33, 33])

class RectangleInputField(ToggleInputField):
    def appear(self):
        set_grid_sizes(self.input_container, columns=[50, 50])
        concentration_container = create_frame(self.input_container, 0, 0)
        extents_container = create_frame(self.input_container, 0, 1)
        
        create_label(concentration_container, "φ =", 0, 0)
        create_label(extents_container, "≤ x ≤", 0, 1)
        create_label(extents_container, "≤ y ≤", 1, 1)
        
        self.entries.append(create_entry(concentration_container, self.defaults[1], 0, 1, sticky="EW", padx=(0, 5), width=5))
        self.entries.append([create_entry(extents_container, self.defaults[2][X], 0, 0, sticky="EW", width=5),
                             create_entry(extents_container, self.defaults[2][Y], 0, 2, sticky="EW", width=5)])
        self.entries.append([create_entry(extents_container, self.defaults[3][X], 1, 0, sticky="EW", width=5),
                             create_entry(extents_container, self.defaults[3][Y], 1, 2, sticky="EW", width=5)])
        
        set_grid_sizes(concentration_container, [100], [40, 60])
        set_grid_sizes(extents_container, [50, 50], [33, 33, 33])
           
# Abstract class which represents main menu buttons.
class MainMenuButton(object):
    def __init__(self, name, ui, row):
        self.name = name
        self.ui = ui
        self.button = create_button(self.ui.container, name, row, 0, self.press, sticky="EW", pady=10, ipady=40, fg="black", bg="pink")
    def press(self):
        # Whenever a main menu button is pressed, the container is cleared and
        # the label below the logo is set to the name of the main menu button.
        clear_widgets(self.ui.container)
        self.ui.label["text"] = self.name

type_dictionary = {
    "numeric": NumericInputField,
    "cell": CellInputField,
    "domain": DomainInputField,
    "boolean": ToggleInputField,
    "field": VelocityInputField,
    "circle": CircleInputField,
    "rectangle": RectangleInputField,
}
    
class CustomConditions(MainMenuButton):
    def press(self):
        super().press()
        self.inputs = []
        # Read the input dictionary from the JSON.
        input_dictionary = self.ui.data[self.name]
        
        # Count the number of input fields and add 2 rows for the run and back buttons.
        row_count = len(input_dictionary.keys()) + 2
        relative_height = int(100 / row_count)
        set_grid_sizes(self.ui.container, rows=np.full(row_count, relative_height))
        
        for row, (key, field_info) in enumerate(input_dictionary.items()):
            self.create_input_object(key, field_info, row)
        
        create_button(self.ui.container, "Run Simulation", row_count - 1, 0, self.run, pady=(5, 0), ipady=10, fg="black", bg="pink")
        create_button(self.ui.container, "Back", row_count, 0, self.ui.create_menu_buttons, pady=(5, 0), ipady=10, fg="black", bg="pink")
        
    def create_input_object(self, text, field_info, row):
        input = type_dictionary[field_info["type"]](self.ui, field_info, row)
        input.create(text)
        self.inputs.append(input)
        
    def get_entry_value(self, entry):
        if not isinstance(entry, bool) and not isinstance(entry, str):
            entry = entry.get()
        return entry
    
    def set_value(self, key, value):
        try:
            self.outputs[key] = value
            return True
        except Exception as e:
            type_validation = False
            messagebox.showerror('error', e)
        return False
    
    def loop_entries(self, keys, defaults, entries):
        for index, entry in enumerate(entries):
            if isinstance(entry, list):
                get_entries = lambda x: self.get_entry_value(x)
                inner_entries = np.vectorize(get_entries)(np.array(entry))
                for inner_entry in inner_entries:
                    self.set_value(keys[index], type(defaults[index])(self.get_entry_value(entry)))
            else:
                self.set_value(keys[index], type(defaults[index])(self.get_entry_value(entry)))
        
    def run(self):
        #TODO: Convert ouputs to dictionary where key is retrieved from json and value is output.
        #This will drastically simplify the code and make it much clearer.
        self.outputs = {}
        type_validation = True
        for input in self.inputs:
            defaults = input.field_info["default"]
            keys = input.field_info["key"]
            if isinstance(input.entries, list):
                assert len(input.entries) > 0, "Entries length must be greater than 0"
                if isinstance(input.entries[0], bool): # Toggle entry.
                    toggle = bool(input.entries[0])
                    self.outputs[keys[0]] = toggle
                    if toggle and len(input.entries) > 1:
                        print("Toggle: " + str(input.entries[1:]))
                else: # Other non-toggle entry.
                    pass
                    print("Non-toggle: " + str(input.entries))
            else:
                type_validation &= self.set_value(keys, type(defaults)(self.get_entry_value(input.entries)))
        print(self.outputs)
        # if type_validation and self.validation():
        #    self.setup()
        
    def setup(self):
        clear_widgets(self.ui.container)
        time_max = self.outputs[0][0]
        self.ui.label["text"] = self.name
        animated = self.outputs[6][0]
        # Color gradient which goes red to blue (0.0 to 1.0).
        color_gradient = dict(red   = [(0.0, 0.0, 1.0), (1.0, 0.0, 0.0)],
                              green = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)],
                              blue  = [(0.0, 0.0, 0.0), (1.0, 1.0, 0.0)])
        # time, step, diffusivity, particle_count, domain, cell_size, animated, velocity_info, circle_info, rectangle_info, color_gradient
        sim = simulation.setup(time_max, self.outputs[1][0], self.outputs[2][0], self.outputs[3][0], self.outputs[4], \
                               self.outputs[5], animated, self.outputs[7], self.outputs[8], self.outputs[9], color_gradient)
        if animated:
            sim.setup_animated_plot()
            anim = animation.FuncAnimation(sim.figure, func=sim.animate, init_func=sim.init_animation, frames=sim.steps, interval=1, repeat=False)
            self.ui.label["text"] = self.name + " (animating until t = " +  str(time_max) + "s)"
        else:
            sim.setup_static_plot()
            
        self.ui.create_plot(sim.figure, self.setup, self.press).draw()
    
    # Returns true if condition is met, otherwise prompts user with an error message and returns false.
    def check(self, condition, message):
        return True if condition else not bool(messagebox.showinfo("Field error", message))
        
    # Validates entry field inputs and notifies the user if any or all of them do not fit requiremed criteria.
    # Criteria such as certain values being positive, velocity data being readable, etc. 
    def validation(self):
        # All conditions must be met in order for validity to hold.
        valid = self.check(self.outputs[0][0] > 0, "Max time must be greater than 0") & \
                self.check(self.outputs[1][0] > 0, "Time step must be greater than 0") & \
                self.check(self.outputs[1][0] < self.outputs[0][0], "Time step cannot exceed maximum time") & \
                self.check(self.outputs[2][0] > 0, "Diffusivity must be greater than or equal to 0") & \
                self.check(self.outputs[3][0] > 0, "Particle count must be greater than 0") & \
                self.check(self.outputs[4][1] > self.outputs[4][0], "X_max must be greater than X_min") & \
                self.check(self.outputs[4][3] > self.outputs[4][2], "Y_max must be greater than Y_min") & \
                self.check(self.outputs[5][0] > 0, "Cell width must be greater than 0") & \
                self.check(self.outputs[5][1] > 0, "Cell height must be greater than 0")
        if self.outputs[7][0]: # Velocity field is being used.
            # velocity path can be read and has 4 columns
            vc, vf = simulation.read_data_file(self.outputs[7][1], [0, 1], [2, 3])
            valid &= self.check(vc is not None and vf is not None, "Velocity field data file does not contain the required data columns") 
        if self.outputs[8][0]: # Circle field is being used.
            valid &= self.check(self.outputs[8][1] == 0 or self.outputs[8][1] == 1, "Circle concentration must start as 0 or 1 (red or blue)")
        if self.outputs[9][0]: # Rectangle field is being used.
            valid &= self.check(self.outputs[9][1] == 0 or self.outputs[9][1] == 1, "Rectangle concentration must start as 0 or 1 (red or blue)")
        return valid

# TODO: Make this work.
class ValidationTasks(MainMenuButton):
    def press(self):
        super().press()

class EngineeringSpill(MainMenuButton):
    def press(self):
        super().press()
        time_max = 5
        self.ui.label["text"] = self.name + " (animating until t = " +  str(time_max) + "s)"
        # Color gradient which goes blue to green to green (0.0 to 0.3 to 1.0).
        color_gradient = dict(blue   = [(0.0, 0.0, 1.0), (0.3, 0.0, 1.0), (0.3, 0.0, 0.0),  (1.0, 0.0, 0.0)],
                              green = [(0.0, 0.0, 0.0), (0.3, 0.7, 1.0), (1.0, 1.0, 1.0)],
                              red  = [(0.0, 0.0, 0.0), (0.3, 0.0, 1.0), (0.3, 0.0, 0.0),  (1.0, 0.0, 0.0)])
        # time, step, diffusivity, particle_count, domain, cell_size, animated, velocity_info, circle_info, rectangle_info, color_gradient
        sim = simulation.setup(time_max, 0.01, 0.1, 15000, [-1, 1, -1, 1], [75, 75], [True], \
                               [True, os.path.join(os.path.dirname(__file__), "velocityCMM3.dat")], \
                               [True, 1, 0.4, 0.4, 0.1], [False], color_gradient)
        sim.setup_animated_plot()
        anim = animation.FuncAnimation(sim.figure, func=sim.animate, init_func=sim.init_animation, frames=sim.steps, interval=1, repeat=False)
            
        self.ui.create_plot(sim.figure, self.press, self.ui.create_menu_buttons).draw()
        

UserInterface(os.path.join(os.path.dirname(__file__), "gui/input_boxes.json"))