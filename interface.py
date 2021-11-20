import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfile
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sys import platform as system_platform
import numpy as np
import os
import json
import simulation
import utility

# TODO: Add short description at the top of this file.

# Tkinter embedded plot fix for macOS.
if system_platform == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

X = 0
Y = 1

# Parent user interface class which creates a graphical 
# window and branches the program out to specific tasks.
class UserInterface(object):
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        # Create Tkinter window of given size and grid configuration.
        self.root = utility.create_root("700x700+0+0")
        self.frame = utility.create_frame(self.root, 0, 0)
        utility.set_grid_sizes(self.frame, [20, 7, 66, 7], [20, 60, 20], uniform_row="frame", uniform_column="frame")
        self.container = None
        # Load JSON file into a data object and populate the window.
        with open(self.json_file_path) as json_file:
            self.data = json.load(json_file)
            self.create_header()
            self.create_menu_buttons()
            self.root.mainloop()
        
    def create_header(self):
        # Create the GUI logo.
        utility.create_image(self.frame, os.path.join(os.path.dirname(__file__), "gui/logo.png"), 0, 1)
        # Create the GUI label (modified by main menu buttons when they are pressed).
        self.label_text = "Please choose a mode of operation."
        self.label = utility.create_label(self.frame, self.label_text, 1, 1)
    
    # Creates the main menu navigation buttons.
    def create_menu_buttons(self):
        utility.clear_widgets(self.container)
        self.label["text"] = self.label_text
        self.create_container()
        utility.set_grid_sizes(self.container, [33, 33, 33], [100], uniform_row="container", uniform_column="container")
        # Create individual buttons in the container.
        CustomConditions("Custom Conditions", self, 0)
        ValidationTasks("Validation Tasks", self, 1)
        EngineeringSpill("Engineering Spill", self, 2)

    # Creates the container cell.
    def create_container(self):
        self.container = utility.create_frame(self.frame, 2, 1)
        
    def create_plot(self, figure, reset_function, back_function):
        canvas = FigureCanvasTkAgg(figure, master=self.container)
        canvas.get_tk_widget().grid(row=0, column=0, padx=0, pady=0)
        
        utility.create_button(self.container, "Reset Plot", 1, 0, reset_function, pady=(5, 0), ipady=15, fg="black", bg="pink")
        utility.create_button(self.container, "Back", 2, 0, back_function, pady=(5, 0), ipady=15, fg="black", bg="pink")
        
        utility.set_grid_sizes(self.container, [80, 4, 4], [100])
        return canvas
      
# Abstract class which represents an input row.
class InputField(object):
    # Field info contains the input field info from the JSON file.
    def __init__(self, ui: UserInterface, field_info, row: int):
        self.field_info = field_info
        self.defaults = self.field_info["default"]
        # Used for storing the entry fields of the given input field.
        self.entries = []
        # Create a sub container for the input field and label.
        self.sub_container = utility.create_frame(ui.container, row, 0)
        utility.set_grid_sizes(self.sub_container, columns=[50, 50], uniform_row="sub_container", uniform_column="sub_container")
        
    def create(self, text):
        self.key = text
        utility.create_label(self.sub_container, text, 0, 0)


class NumericInputField(InputField):
    def create(self, text: str):
        super().create(text)
        # Creates a simple input parameter box with a default value.
        self.entries = utility.create_entry(self.sub_container, self.field_info["default"], 0, 1, width=20)


class DomainInputField(InputField):
    def create(self, text: str):
        super().create(text)
        domain_container = utility.create_frame(self.sub_container, 0, 1)
        
        utility.create_label(domain_container, "≤ x ≤", 0, 1)
        utility.create_label(domain_container, "≤ y ≤", 1, 1)
        self.entries.append([utility.create_entry(domain_container, self.defaults[0][X], 0, 0, sticky="EW", width=5),
                             utility.create_entry(domain_container, self.defaults[0][Y], 1, 0, sticky="EW", width=5)])
        self.entries.append([utility.create_entry(domain_container, self.defaults[1][X], 0, 2, sticky="EW", width=5),
                             utility.create_entry(domain_container, self.defaults[1][Y], 1, 2, sticky="EW", width=5)])
        
        utility.set_grid_sizes(domain_container, [50, 50], [40, 20, 40])
        
class CellInputField(InputField):
    def create(self, text: str):
        super().create(text)
        cell_container = utility.create_frame(self.sub_container, 0, 1)
        
        utility.create_label(cell_container, u'Nₓ =', 0, 0)
        utility.create_label(cell_container, u'Nᵧ =', 1, 0)
        self.entries.append(utility.create_entry(cell_container, self.defaults[X], 0, 1, sticky="EW", width=5))
        self.entries.append(utility.create_entry(cell_container, self.defaults[Y], 1, 1, sticky="EW", width=5))
        
        utility.set_grid_sizes(cell_container, [50, 50], [15, 85])

class ToggleInputField(InputField):
    def create(self, text: str):
        super().create(text)
        container = utility.create_frame(self.sub_container, 0, 1)
        utility.set_grid_sizes(container, [100], [20, 80], uniform_column="toggle_container")
        self.toggle_container = utility.create_frame(container, 0, 0)
        utility.set_grid_sizes(self.toggle_container, [100], [100])
        self.input_container = utility.create_frame(container, 0, 1)
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
        utility.clear_widgets(self.input_container)
        self.entries = [self.state.get()]

class VelocityInputField(ToggleInputField):
    def appear(self):
        utility.set_grid_sizes(self.input_container, columns=[100])
        file_container = utility.create_frame(self.input_container, 0, 0)
        
        utility.create_button(file_container, "Open File", 0, 0, self.open_file)

        self.path_label = utility.create_label(file_container, "File: " + self.defaults[1], 1, 0)
        self.entries.append(os.path.join(os.path.dirname(__file__), self.defaults[1]))
        
        utility.set_grid_sizes(file_container, [50, 50], [100])
        
    def open_file(self):
        file = askopenfile(mode='r', filetypes=[('Velocity Field Data Files', '*.dat')])
        if file is not None:
            self.path_label["text"] = "File: " + os.path.basename(file.name)
            self.entries[1] = file.name
            file.close()
    
class CircleInputField(ToggleInputField):
    def appear(self):
        utility.set_grid_sizes(self.input_container, columns=[50, 50])
        concentration_container = utility.create_frame(self.input_container, 0, 0)
        circle_container = utility.create_frame(self.input_container, 0, 1)
        
        utility.create_label(concentration_container, "φ =", 1, 0)
        utility.create_label(concentration_container, "", 0, 0)
        utility.create_label(circle_container, "x", 0, 0)
        utility.create_label(circle_container, "y", 0, 1)
        utility.create_label(circle_container, "radius", 0, 2)
        
        self.entries.append(utility.create_entry(concentration_container, self.defaults[1], 1, 1, sticky="EW", padx=(0, 5), width=5))
        self.entries.append([utility.create_entry(circle_container, self.defaults[2][X], 1, 0, sticky="EW", width=5),
                             utility.create_entry(circle_container, self.defaults[2][Y], 1, 1, sticky="EW", width=5)])
        self.entries.append(utility.create_entry(circle_container, self.defaults[3], 1, 2, sticky="EW", width=5))
        
        utility.set_grid_sizes(concentration_container, [50, 50], [40, 60])
        utility.set_grid_sizes(circle_container, [50, 50], [33, 33, 33])

class RectangleInputField(ToggleInputField):
    def appear(self):
        utility.set_grid_sizes(self.input_container, columns=[50, 50])
        concentration_container = utility.create_frame(self.input_container, 0, 0)
        extents_container = utility.create_frame(self.input_container, 0, 1)
        
        utility.create_label(concentration_container, "φ =", 0, 0)
        utility.create_label(extents_container, "≤ x ≤", 0, 1)
        utility.create_label(extents_container, "≤ y ≤", 1, 1)
        
        self.entries.append(utility.create_entry(concentration_container, self.defaults[1], 0, 1, sticky="EW", padx=(0, 5), width=5))
        self.entries.append([utility.create_entry(extents_container, self.defaults[2][X], 0, 0, sticky="EW", width=5),
                             utility.create_entry(extents_container, self.defaults[2][Y], 1, 0, sticky="EW", width=5)])
        self.entries.append([utility.create_entry(extents_container, self.defaults[3][X], 0, 2, sticky="EW", width=5),
                             utility.create_entry(extents_container, self.defaults[3][Y], 1, 2, sticky="EW", width=5)])
        
        utility.set_grid_sizes(concentration_container, [100], [40, 60])
        utility.set_grid_sizes(extents_container, [50, 50], [33, 33, 33])
           
# Abstract class which represents main menu buttons.
class MainMenuButton(object):
    def __init__(self, name: str, ui: UserInterface, row: int):
        self.name = name
        self.ui = ui
        self.button = utility.create_button(self.ui.container, name, row, 0, self.press, sticky="EW", pady=10, ipady=40, fg="black", bg="pink")
    def press(self):
        # Whenever a main menu button is pressed, the container is cleared and
        # the label below the logo is set to the name of the main menu button.
        utility.clear_widgets(self.ui.container)
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
        utility.set_grid_sizes(self.ui.container, rows=np.full(row_count, relative_height))
        
        for row, (key, field_info) in enumerate(input_dictionary.items()):
            self.create_input_object(key, field_info, row)
        
        utility.create_button(self.ui.container, "Run Simulation", row_count - 1, 0, self.run, pady=(5, 0), ipady=10, fg="black", bg="pink")
        utility.create_button(self.ui.container, "Back", row_count, 0, self.ui.create_menu_buttons, pady=(5, 0), ipady=10, fg="black", bg="pink")
        
    def create_input_object(self, text: str, field_info, row: int):
        input = type_dictionary[field_info["type"]](self.ui, field_info, row)
        input.create(text)
        self.inputs.append(input)
        
    # Retrieves the raw value(s) of an entry.
    # If entry is a tkinter widget, retrieve the value inside of it.
    # If entry is boolean or string, return it as is.
    # If entry is a list of entries, recursively go through the above steps for each element.
    def get_entry(self, entry):
        if isinstance(entry, list):
            inner_entries = []
            for inner_entry in entry:
                # Cycle through the list recursively.
                inner_entries.append(self.get_entry(inner_entry))
            return inner_entries
        elif not isinstance(entry, bool) and not isinstance(entry, str):
            return entry.get()
        else:
            return entry

    # Parses an entry and casts it to the correct type based on its respective defaults array.
    def parse_entry(self, defaults, entry):
        if isinstance(entry, list):
            inner_entries = []
            for index, inner_entry in enumerate(entry):
                inner_entries.append(self.parse_entry(defaults[index], inner_entry))
            return inner_entries
        else:
            try:
                return type(defaults)(entry)
            except Exception as e: # Let the user know if the entry they made cannot be cast.
                messagebox.showerror('error', e)
                return None # None used for invalidating data.
                
    def run(self):
        self.outputs = {}
        for input in self.inputs:
            keys = input.field_info["key"]
            defaults = input.field_info["default"]
            if isinstance(keys, list):
                for index, entry in enumerate(input.entries):
                    self.outputs[keys[index]] = self.parse_entry(defaults[index], self.get_entry(entry))
            else:
                self.outputs[keys] = self.parse_entry(defaults, self.get_entry(input.entries))
        # Any value of None (invalid) in the self.outputs dictionary will prevent the button from continuing.
        if not None in self.outputs.values() and self.validation():
            self.setup()
        
    def setup(self):
        utility.clear_widgets(self.ui.container)
        self.ui.label["text"] = self.name
        
        # Color gradient which goes red to blue (0.0 to 1.0).
        color_gradient = dict(red   = [(0.0, 0.0, 1.0), (1.0, 0.0, 0.0)],
                              green = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)],
                              blue  = [(0.0, 0.0, 0.0), (1.0, 1.0, 0.0)])

        sim = simulation.Simulation(color_gradient, **self.outputs)
        
        if self.outputs.get("use_circle"):
            sim.add_circle(self.outputs["circle_center"], self.outputs["circle_radius"], self.outputs["circle_value"])
        
        if self.outputs.get("use_rectangle"):
            sim.add_rectangle(self.outputs["rectangle_min"], self.outputs["rectangle_max"], self.outputs["rectangle_value"])

        if self.outputs["animated"]:
            sim.setup_animated_plot()
            self.ui.label["text"] = self.name + " (animating until t = " +  str(self.outputs["time_max"]) + "s)"
        else:
            sim.setup_static_plot()
            
        self.ui.create_plot(sim.figure, self.setup, self.press).draw()
    
    # Returns true if condition is met, otherwise prompts user with an error message and returns false.
    def check(self, condition: bool, message: str):
        return True if condition else not bool(messagebox.showinfo("Field error", message))
        
    # Validates entry field inputs and notifies the user if any or all of them do not fit requiremed criteria.
    # Criteria such as certain values being positive, velocity data being readable, etc. 
    def validation(self):
        # All conditions must be met in order for validity to hold.
        valid = self.check(self.outputs["time_max"] > 0, "Max time must be greater than 0") & \
                self.check(self.outputs["dt"] > 0, "Time step must be greater than 0") & \
                self.check(self.outputs["dt"] < self.outputs["time_max"], "Time step cannot exceed maximum time") & \
                self.check(self.outputs["diffusivity"] > 0, "Diffusivity must be greater than or equal to 0") & \
                self.check(self.outputs["particle_count"] > 0, "Particle count must be greater than 0") & \
                self.check(self.outputs["max"][X] > self.outputs["min"][X], "X_max must be greater than X_min") & \
                self.check(self.outputs["max"][Y] > self.outputs["min"][Y], "Y_max must be greater than Y_min") & \
                self.check(self.outputs["cell_size"][X] > 0, "Cell width must be greater than 0") & \
                self.check(self.outputs["cell_size"][Y] > 0, "Cell height must be greater than 0")
        
        if self.outputs["use_velocity"]:
            # Check that the velocity field file can be read and has 4 columns.
            coordinates, vectors = simulation.read_data_file(self.outputs["velocity_field_path"], [0, 1], [2, 3])
            valid &= self.check(coordinates is not None and vectors is not None, "Velocity field data file does not contain the required data columns") 
        
        if self.outputs["use_circle"]:
            valid &= self.check(self.outputs["circle_value"] == 0 or self.outputs["circle_value"] == 1, "Circle concentration must start as 0 or 1 (red or blue)")
        
        if self.outputs["use_rectangle"]:
            valid &= self.check(self.outputs["rectangle_value"] == 0 or self.outputs["rectangle_value"] == 1, "Rectangle concentration must start as 0 or 1 (red or blue)")
        
        return valid

# TODO: Make this work.
class ValidationTasks(MainMenuButton):
    def press(self):
        super().press()

class EngineeringSpill(MainMenuButton):
    def press(self):
        super().press()
        
        outputs = {
            "time_max": 5,
            "dt": 0.01,
            "diffusivity": 0.1,
            "particle_count": 15000,
            "min": [-1.0, -1.0],
            "max": [1.0, 1.0],
            "cell_size": [75, 75],
            "use_velocity": True,
            "velocity_field_path": os.path.join(os.path.dirname(__file__), "velocityCMM3.dat"),
        }
        
        self.ui.label["text"] = self.name + " (animating until t = " +  str(outputs["time_max"]) + "s)"
        
        # Color gradient which goes blue to green to green (0.0 to 0.3 to 1.0).
        color_gradient = dict(blue  = [(0.0, 0.0, 1.0), (0.3, 0.0, 1.0), (0.3, 0.0, 0.0),  (1.0, 0.0, 0.0)],
                              green = [(0.0, 0.0, 0.0), (0.3, 0.7, 1.0), (1.0, 1.0, 1.0)],
                              red   = [(0.0, 0.0, 0.0), (0.3, 0.0, 1.0), (0.3, 0.0, 0.0),  (1.0, 0.0, 0.0)])
        
        sim = simulation.Simulation(color_gradient, **outputs)

        sim.add_circle(center=[0.4, 0.4], radius=0.1, value=1)
        
        sim.setup_animated_plot()
        
        self.ui.create_plot(sim.figure, self.press, self.ui.create_menu_buttons).draw()
        

UserInterface(os.path.join(os.path.dirname(__file__), "gui/input_boxes.json"))