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

# Utility functions for easily creating gridded tkinter widgets.

def set_column_sizes(container, relative_sizes, uniform=""):
    for column, size in enumerate(relative_sizes):
        container.grid_columnconfigure(column, weight=size, uniform=uniform)
        
def set_row_sizes(container, relative_sizes, uniform=""):
    for row, size in enumerate(relative_sizes):
        container.grid_rowconfigure(row, weight=size, uniform=uniform)

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

# User interface object to be called at the beginning of the program creation.
class UserInterface(object):
    def __init__(self, json_filepath):
        self.json_filepath = json_filepath
        # Create Tkinter window of given size and grid configuration.
        self.root = tk.Tk()
        self.root.geometry("700x700+0+0")
        self.root.configure(bg="white")
        set_column_sizes(self.root, [100], uniform="root")
        set_row_sizes(self.root, [100], uniform="root")
        self.frame = create_frame(self.root, 0, 0)
        set_column_sizes(self.frame, [20, 60, 20], uniform="frame")
        set_row_sizes(self.frame, [20, 7, 66, 7], uniform="frame")
        self.container = None
        # Load JSON file into a data object and populate the window.
        with open(self.json_filepath) as json_file:
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
        self.clear_container()
        self.create_container()
        set_column_sizes(self.container, [100], uniform="container")
        set_row_sizes(self.container, [33, 33, 33], uniform="container")
        # Create individual buttons in the container.
        CustomConditions("Custom Conditions", self, 0)
        ValidationTasks("Validation Tasks", self, 1)
        EngineeringSpill("Engineering Spill", self, 2)

    # Creates the container cell.
    def create_container(self):
        self.container = create_frame(self.frame, 2, 1)
        
    # Clears the container cell.
    def clear_container(self):
        if self.container is not None:
            for widget in self.container.winfo_children():
                widget.destroy()
        self.label["text"] = self.label_text
        
    def create_plot(self, figure, reset_function, back_function):
        canvas = FigureCanvasTkAgg(figure, master=self.container)
        canvas.get_tk_widget().grid(row=0, column=0, padx=0, pady=0)
        
        create_button(self.container, "Reset Plot", 1, 0, reset_function, pady=(5, 0), ipady=15, fg="black", bg="pink")
        create_button(self.container, "Back", 2, 0, back_function, pady=(5, 0), ipady=15, fg="black", bg="pink")
        
        set_row_sizes(self.container, [80, 4, 4])
        set_column_sizes(self.container, [100])
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
        set_column_sizes(self.sub_container, [50, 50], uniform="sub_container")
        
    def create(self, text):
        self.key = text
        create_label(self.sub_container, text, 0, 0)


class NumericInputField(InputField):
    def create(self, text):
        super().create(text)
        # Creates a simple input parameter box with a default value.
        self.entries.append(create_entry(self.sub_container, self.field_info["default"], 0, 1, width=20))


class DomainInputField(InputField):
    def create(self, text):
        super().create(text)
        defaults = self.field_info["default"]
        domain_container = create_frame(self.sub_container, 0, 1)
        
        self.entries.append(create_entry(domain_container, defaults[0], 0, 0, sticky="EW", width=5))
        create_label(domain_container, "≤ x ≤", 0, 1)
        self.entries.append(create_entry(domain_container, defaults[1], 0, 2, sticky="EW", width=5))
        
        self.entries.append(create_entry(domain_container, defaults[2], 1, 0, sticky="EW", width=5))
        create_label(domain_container, "≤ y ≤", 1, 1)
        self.entries.append(create_entry(domain_container, defaults[3], 1, 2, sticky="EW", width=5))
        
        set_row_sizes(domain_container, [50, 50])
        set_column_sizes(domain_container, [40, 20, 40])
        
class CellInputField(InputField):
    def create(self, text):
        super().create(text)
        defaults = self.field_info["default"]
        cell_container = create_frame(self.sub_container, 0, 1)
        
        create_label(cell_container, u'Nₓ =', 0, 0)
        self.entries.append(create_entry(cell_container, defaults[0], 0, 1, sticky="EW", width=5))
        
        create_label(cell_container, u'Nᵧ =', 1, 0)
        self.entries.append(create_entry(cell_container, defaults[1], 1, 1, sticky="EW", width=5))
        
        set_row_sizes(cell_container, [50, 50])
        set_column_sizes(cell_container, [15, 85])

# Abstract class for toggleable input containers.
class ToggleInput():
    def __init__(self, toggle_container):
        self.entries = []
        # Create a sub container in the toggle container.
        self.input_container = create_frame(toggle_container, 0, 1)
        set_row_sizes(self.input_container, [100])
    
    def remove(self):
        for widget in self.input_container.winfo_children():
            # Remove all widgets aside from the toggle button.
            toggle_button = widget.winfo_class() == 'Button' and widget.cget("text") == "toggle_button"
            if not toggle_button:
                widget.destroy()
        self.entries.clear()

class VelocityInput(ToggleInput):
    def __init__(self, toggle_container, update_function):
        super().__init__(toggle_container)
        self.update_function = update_function
        
    def create(self, field_info):
        defaults = field_info["default"]
        set_column_sizes(self.input_container, [100])
        file_container = create_frame(self.input_container, 0, 0)
        
        create_button(file_container, "Open File", 0, 0, self.open_file)
        
        default_file = defaults[1]
        self.path_label = create_label(file_container, "File: " + default_file, 1, 0)
        self.set_file(default_file, True)
        
        set_row_sizes(file_container, [50, 50])
        set_column_sizes(file_container, [100])
        
    def open_file(self):
        file = askopenfile(mode='r', filetypes=[('Velocity Field Data Files', '*.dat')])
        if file is not None:
            self.set_file(file.name)
            file.close()
    
    def set_file(self, file, relative=False):
        # Deal with relative file paths.
        if relative:
            file = os.path.join(os.path.dirname(__file__), file)
        # Update label with file name.
        self.path_label["text"] = "File: " + os.path.basename(file)
        self.entries = [file]
        self.update_function()
    
    
class CircleInput(ToggleInput):
    def create(self, field_info):
        defaults = field_info["default"]
        set_column_sizes(self.input_container, [50, 50])
        concentration_container = create_frame(self.input_container, 0, 0)
        circle_container = create_frame(self.input_container, 0, 1)
        
        create_label(concentration_container, "φ =", 1, 0)
        create_label(concentration_container, "", 0, 0)
        self.entries.append(create_entry(concentration_container, defaults[1], 1, 1, sticky="EW", padx=(0, 5), width=5))
        
        create_label(circle_container, "x", 0, 0)
        create_label(circle_container, "y", 0, 1)
        create_label(circle_container, "radius", 0, 2)
        self.entries.append(create_entry(circle_container, defaults[2], 1, 0, sticky="EW", width=5))
        self.entries.append(create_entry(circle_container, defaults[3], 1, 1, sticky="EW", width=5))
        self.entries.append(create_entry(circle_container, defaults[4], 1, 2, sticky="EW", width=5))
        
        set_row_sizes(concentration_container, [50, 50])
        set_row_sizes(circle_container, [50, 50])
        set_column_sizes(concentration_container, [40, 60])
        set_column_sizes(circle_container, [33, 33, 33])

class RectangleInput(ToggleInput):
    def create(self, field_info):
        defaults = field_info["default"]
        set_column_sizes(self.input_container, [50, 50])
        concentration_container = create_frame(self.input_container, 0, 0)
        extents_container = create_frame(self.input_container, 0, 1)
        
        create_label(concentration_container, "φ =", 0, 0)
        self.entries.append(create_entry(concentration_container, defaults[1], 0, 1, sticky="EW", padx=(0, 5), width=5))
        
        self.entries.append(create_entry(extents_container, defaults[2], 0, 0, sticky="EW", width=5))
        create_label(extents_container, "≤ x ≤", 0, 1)
        self.entries.append(create_entry(extents_container, defaults[3], 0, 2, sticky="EW", width=5))
        
        self.entries.append(create_entry(extents_container, defaults[4], 1, 0, sticky="EW", width=5))
        create_label(extents_container, "≤ y ≤", 1, 1)
        self.entries.append(create_entry(extents_container, defaults[5], 1, 2, sticky="EW", width=5))
        
        set_row_sizes(concentration_container, [100])
        set_row_sizes(extents_container, [50, 50])
        set_column_sizes(concentration_container, [40, 60])
        set_column_sizes(extents_container, [33, 33, 33])
        
class ToggleInputField(InputField):
    def create(self, text):
        super().create(text)
        # Create images for on and off state of toggle button.
        self.off = ImageTk.PhotoImage(file=os.path.join(os.path.dirname(__file__), self.field_info["button_image"][0]))
        self.on = ImageTk.PhotoImage(file=os.path.join(os.path.dirname(__file__), self.field_info["button_image"][1]))
        # Default state of the button
        self.state = self.field_info["default"][0]
        toggle_container = create_frame(self.sub_container, 0, 1)
        set_row_sizes(toggle_container, [100])
        set_column_sizes(toggle_container, [20, 80], uniform="toggle_container")
        self.button = create_button(toggle_container, "toggle_button", 0, 0, self.toggle, image=self.get_image(), bg="white", activebackground="white", bd=0)
        
        # Type of the toggle button
        type = self.field_info["type"]
        # Default input is animation toggle (just a button, hence no class type).
        self.input = None
        if type == "field":
            self.input = VelocityInput(toggle_container, self.update_entries)
        elif type == "circle":
            self.input = CircleInput(toggle_container)
        elif type == "rectangle":
            self.input = RectangleInput(toggle_container)
            
        self.update_visibility()
            
    # Returns the image of the button for the given state.
    def get_image(self):
        return self.on if self.state else self.off
    
    # Toggles the internal state of the button.
    def toggle(self):
        self.state = not self.state
        self.update_visibility()
        self.button.config(image=self.get_image())
    
    # Updates the visibility of the toggle input container contents. 
    def update_visibility(self):
        if self.input is not None:
            if self.state:
                self.input.create(self.field_info)
            else:
                self.input.remove()
        self.update_entries()
            
    def update_entries(self):
        if self.input is not None and self.state:
            self.entries = [self.state] + self.input.entries
        else:
            self.entries = [self.state]
     
# Abstract class which represents main menu buttons.
class MainMenuButton(object):
    def __init__(self, name, ui, row):
        self.name = name
        self.ui = ui
        self.button = create_button(self.ui.container, name, row, 0, self.press, sticky="EW", pady=10, ipady=40, fg="black", bg="pink")
    def press(self):
        # Whenever a main menu button is pressed, the container is cleared and
        # the label below the logo is set to the name of the main menu button.
        self.ui.clear_container()
        self.ui.label["text"] = self.name
          
class CustomConditions(MainMenuButton):
    def press(self):
        super().press()
        self.inputs = []
        # Read the input dictionary from the JSON.
        input_dictionary = self.ui.data[self.name]
        
        # Count the number of input fields and add 2 rows for the run and back buttons.
        row_count = len(input_dictionary.keys()) + 2
        relative_height = int(100 / row_count)
        set_row_sizes(self.ui.container, np.full(row_count, relative_height))
        
        for row, (key, field_info) in enumerate(input_dictionary.items()):
            self.create_input_object(key, field_info, row)
        
        create_button(self.ui.container, "Run Simulation", row_count - 1, 0, self.run, pady=(5, 0), ipady=10, fg="black", bg="pink")
        create_button(self.ui.container, "Back", row_count, 0, self.ui.create_menu_buttons, pady=(5, 0), ipady=10, fg="black", bg="pink")
        
    def create_input_object(self, text, field_info, row):
        type = field_info["type"]
        if type == "numeric":
            input = NumericInputField(self.ui, field_info, row)
        elif type == "cell":
            input = CellInputField(self.ui, field_info, row)
        elif type == "domain":
            input = DomainInputField(self.ui, field_info, row)
        elif type == "boolean" or type == "field" or type == "circle" or type == "rectangle":
            input = ToggleInputField(self.ui, field_info, row)
        input.create(text)
        self.inputs.append(input)
        
    def run(self):
        # TODO: Convert ouputs to dictionary where key is retrieved from json and value is output.
        # This will drastically simplify the code and make it much clearer.
        self.outputs = []
        type_validation = True
        for input in self.inputs:
            entry_outputs = []
            types = []
            for key in input.field_info["default"]:
                types.append(type(key))
            for index, entry in enumerate(input.entries):
                if isinstance(entry, bool) or isinstance(entry, str):
                    entry_outputs.append(types[index](entry))
                elif entry.winfo_class() == 'Entry':
                    try:
                        entry_outputs.append(types[index](entry.get()))
                    except Exception as e:
                        type_validation = False
                        messagebox.showerror('error', e)
                        
            self.outputs.append(entry_outputs)
        if type_validation and self.validation():
            self.setup()
        
    def setup(self):
        self.ui.clear_container()
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