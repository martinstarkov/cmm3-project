import tkinter as tk
from tkinter.filedialog import askopenfile
import os
from PIL import Image, ImageTk
import json

    # def get_input(self):
    #     # Takes the input from the entry box and stores it as a class variable.
    #     if self.data_type == 'integer':
    #         data = self.box.get()
    #         return int(data)
    #     elif self.data_type == 'domain':
    #         values = []
    #         for input_box in self.boxes:
    #             value = float(input_box.get())
    #             values.append(value)
    #         return values
    #     else:
    #         data = self.box.get()
    #         return float(data)
    
    # def get_input(self):
    #     values = []
    #     if self.status:
    #         for input_box in self.input_boxes:
    #             if self.status and self.label != "Velocity Field":
    #                 (value) = float(input_box.get())
    #             elif self.status and self.label == "Velocity Field":
    #                 value = str(self.get_path())
    #             values.append(value)
    #         return True, values
    #     else:
    #         return False
    
    # def add_rectangle(self):
    #     self.window = tk.PanedWindow(self.root)
    #     self.window.grid(row=self.row, column=self.column + 2, sticky="nsew", padx= 10, pady= 20)
    #     left_pane = tk.Frame(self.window, width=50)
    #     right_pane = tk.PanedWindow(self.window, width=100)
    #     self.window.add(left_pane)
    #     self.window.add(right_pane)
    #     conc_label = tk.Label(left_pane, text="φ =")
    #     conc_label.grid(column=0, row=0)
    #     conc_input_box = tk.Entry(left_pane, width=5)
    #     conc_input_box.insert(0, self.default[0])
    #     conc_input_box.grid(column=1, row=0)
    #     xmin_input_box = tk.Entry(right_pane, width=5)
    #     xmin_input_box.insert(0, self.default[1])
    #     xmin_input_box.grid(column=0, row=0)
    #     x_label = tk.Label(right_pane, text="< x <")
    #     x_label.grid(column=1, row=0)
    #     xmax_input_box = tk.Entry(right_pane, width=5)
    #     xmax_input_box.insert(0, self.default[2])
    #     xmax_input_box.grid(column=2, row=0)
    #     ymin_input_box = tk.Entry(right_pane, width=5)
    #     ymin_input_box.insert(0, self.default[3])
    #     ymin_input_box.grid(column=0, row=1)
    #     y_label = tk.Label(right_pane, text="< y <")
    #     y_label.grid(column=1, row=1)
    #     ymax_input_box = tk.Entry(right_pane, width=5)
    #     ymax_input_box.insert(0, self.default[4])
    #     ymax_input_box.grid(column=2, row=1)
    #     self.input_boxes.extend([conc_input_box, xmin_input_box, xmax_input_box, ymin_input_box, ymax_input_box])
    #     self.elements = (self.window.winfo_children())

    # def add_circle(self):
    #     self.window = tk.PanedWindow(self.root)
    #     self.window.grid(row=self.row, column=self.column + 2, sticky="nsew", padx= 10, pady= 30)
    #     left_pane = tk.Frame(self.window, width=50)
    #     right_pane = tk.PanedWindow(self.window, width=100)
    #     self.window.add(left_pane)
    #     self.window.add(right_pane)
    #     conc_label = tk.Label(left_pane, text="φ", height = 1)
    #     conc_label.grid(column=0, row=0)
    #     conc_input_box = tk.Entry(left_pane, width=5)
    #     conc_input_box.insert(0, self.default[0])
    #     conc_input_box.grid(column=0, row=1)
    #     x_label = tk.Label(right_pane, text="x")
    #     x_label.grid(column=0, row=0)
    #     y_label = tk.Label(right_pane, text="y")
    #     y_label.grid(column=1, row=0)
    #     r_label = tk.Label(right_pane, text="r")
    #     r_label.grid(column=2, row=0)
    #     x_input_box = tk.Entry(right_pane, width=5)
    #     x_input_box.insert(0, self.default[1])
    #     x_input_box.grid(column=0, row=1)
    #     y_input_box = tk.Entry(right_pane, width=5)
    #     y_input_box.insert(0, self.default[2])
    #     y_input_box.grid(column=1, row=1)
    #     r_input_box = tk.Entry(right_pane, width=5)
    #     r_input_box.insert(0, self.default[3])
    #     r_input_box.grid(column=2, row=1)
    #     self.input_boxes.extend([conc_input_box, x_input_box, y_input_box, r_input_box])
    #     self.elements = (self.window.winfo_children())

    # def open_file(self):
    #     # handles the activity of the open file button. stores the path of the file as a variable and stores it as a class variable.
    #     self.file = askopenfile(mode='r', filetypes=[
    #                             ('velocity field', '*.dat')]).name
    #     if self.file is not None:
    #         self.file_path = str(pathlib.PurePath(str(self.file)))
    #         success_text = tk.Label(text=str(self.file_path))
    #         success_text.grid(
    #             columnspan=10, column=self.column + 3, row=self.row)
    
    # def get_path(self):
    #     return self.file_path

    # def add(self):
    #     self.window = tk.PanedWindow(self.root)
    #     self.window.grid(row=self.row, column=self.column + 2, sticky="nsew", columnspan=1, rowspan=1)
    #     self.browse = tk.Button(
    #                 self.window, text='Open File', command=lambda: self.open_file())
    #     self.browse.grid(
    #                 columnspan=1, column=self.column + 2, row=self.row)
    #     self.input_boxes.append(self)
    #     self.elements.append(self.browse)
        
    # def run(self):
    #     # Handles activity of the Run Button, stores user inputs in a data.json before running script.
    #     dict = self.input_dict
    #     for input in self.inputs:
    #         value = input.get_input()
    #         label = input.label
    #         dict[label][2] = value
    #     # Storing inputs in JSON File.
    #     with open(os.path.join(os.path.dirname(__file__), 'input_boxes.json')) as json_file:
    #         dictionary = json.load(json_file)
    #     dictionary[self.label] = dict
    #     with open(os.path.join(os.path.dirname(__file__), 'input_boxes.json'), 'w') as json_file:
    #         json.dump(dictionary, json_file, indent=4)
    #     for widgets in root.winfo_children():
    #         widgets.destroy()
    #     # TODO replace this with each tasks function.

# User interface object to be called at the beginning of the program creation.
class UserInterface(object):
    def __init__(self, json_filepath):
        # Create Tkinter window of given size and grid configuration.
        self.root = tk.Tk()
        self.root.geometry("700x700+0+0")
        self.root.configure(bg="white")
        self.root.grid_columnconfigure(0, weight=100, uniform="root")
        self.root.grid_rowconfigure(0, weight=100, uniform="root")
        self.frame = tk.Frame(self.root, bg="white")
        self.frame.grid(row=0, column=0, sticky="NSEW")
        # Divide window into 3x4 grid with a relative (out of 100) size for each cell.
        column_sizes = [20, 60, 20]
        row_sizes = [20, 7, 66, 7]
        # Configure the relative widths and heights of the grid columns and rows respectively.
        for column, relative_width in enumerate(column_sizes):
            self.frame.grid_columnconfigure(column, weight=relative_width, uniform="frame")
        for row, relative_height in enumerate(row_sizes):
            self.frame.grid_rowconfigure(row, weight=relative_height, uniform="frame")
        self.container = None
        # Load JSON file into a data object and populate the window.
        with open(json_filepath) as json_file:
            self.data = json.load(json_file)
            self.create_header()
            self.create_menu_buttons()
            self.root.mainloop()
        
    def create_header(self):
        # Create the GUI logo.
        image = Image.open(os.path.join(os.path.dirname(__file__), "logo.png"))
        tkinter_image = ImageTk.PhotoImage(image, master=self.frame)
        logo = tk.Label(bg="white", image=tkinter_image, master=self.frame)
        logo.image = tkinter_image
        logo.grid(row=0, column=1, sticky="NSEW")
        # Create the GUI label (modified by main menu buttons when they are pressed).
        self.label_text = "Please choose a mode of operation."
        self.label = tk.Label(text=self.label_text, bg="white", master=self.frame)
        self.label.grid(row=1, column=1, sticky="NSEW")
    
    # Creates the main menu navigation buttons.
    def create_menu_buttons(self):
        self.clear_container()
        self.create_container()
        # Create a 1x3 container for the menu buttons.
        # Space buttons evenly in the grid.
        self.container.grid_columnconfigure(0, weight=100, uniform="container")
        for row in range(3):
            self.container.grid_rowconfigure(row, weight=100, uniform="container")
        # Create individual buttons in the container.
        CustomSpecifications("Custom Specifications", self, 0)
        ValidationTasks("Validation Tasks", self, 1)
        EngineeringSpill("Real-time Engineering Spill", self, 2)

    # Creates the container cell.
    def create_container(self):
        self.container = tk.Frame(bg="white", master=self.frame)
        self.container.grid(row=2, column=1, sticky="NSEW")
        
    # Clears the container cell.
    def clear_container(self):
        if self.container is not None:
            for widget in self.container.winfo_children():
                widget.destroy()
        self.label["text"] = self.label_text
    
    # TODO: Runs the simulation with parameters read from the json.
    # Probably should cycle through the InputField self.entries arrays and
    # for each of the run some sort of parameter parse and write to the JSON.
    def run(self):
        pass
      
# Abstract class which represents main menu buttons.
class MainMenuButton(object):
    def __init__(self, name, ui, row):
        self.name = name
        self.ui = ui
        self.button = tk.Button(text=name, fg="black", bg="pink", command=self.press, master=self.ui.container)
        self.button.grid(row=row, column=0, pady=10, ipady=40, sticky="EW")
    def press(self):
        # Whenever a main menu button is pressed, the container is cleared and
        # the label below the logo is set to the name of the main menu button.
        self.ui.clear_container()
        self.ui.label["text"] = self.name
    
# Abstract class which represents an input row.
class InputField(object):
    # Field info contains the input field info from the JSON file.
    def __init__(self, ui, field_info, row):
        # Used for storing the entry fields of the given input field.
        # TODO: Cycle through these later to write to the JSON.
        self.entries = []
        # Create a sub container for the input field and label.
        self.sub_container = tk.Frame(bg="white", master=ui.container)
        self.sub_container.grid(row=row, column=0, sticky="NSEW")
        self.sub_container.grid_columnconfigure(0, weight=50, uniform="sub_container")
        self.sub_container.grid_columnconfigure(1, weight=50, uniform="sub_container")
        self.field_info = field_info
        
    def create(self, text):
        self.label = tk.Label(text=text, bg="white", master=self.sub_container)
        self.label.grid(row=0, column=0, pady=10, sticky="NSEW")


class NumericInputField(InputField):
    def create(self, text):
        super().create(text)
        # Creates a simple input parameter box with a default value.
        input = tk.Entry(bg="white", master=self.sub_container, justify="center")
        input.insert(0, self.field_info["default"])
        input.grid(row=0, column=1, pady=10, sticky="NSEW")
        self.entries.append(input)


class DomainInputField(InputField):
    def create(self, text):
        super().create(text)
        self.domain_container = tk.Frame(bg="white", master=self.sub_container)
        self.domain_container.grid(row=0, column=1, sticky="NSEW")
        # Array of relative weights for the column widths.
        widths = [15, 20, 15]
        # Labels between entry fields.
        labels = ["< x <", "< y <"]
        for row, label in enumerate(labels):
            self.domain_container.grid_rowconfigure(row, weight=50)
            for column, relative_width in enumerate(widths):
                self.domain_container.grid_columnconfigure(column, weight=relative_width, uniform="axis_container")
                # Odd columns are entries.
                if column % 2 == 0:
                    input = tk.Entry(bg="white", master=self.domain_container, justify="center")
                    input.insert(0, self.field_info["default"][len(self.entries)])
                    self.entries.append(input)
                # Even column is a label.
                else:
                    input = tk.Label(text=label, bg="white", padx=10, master=self.domain_container)
                # Only add bottom padding to the second row.
                input.grid(row=row, column=column, pady=10, sticky="EW")       

# Abstract class for toggleable input containers.
class ToggleInput():
    def __init__(self, toggle_container):
        self.entries = []
        # Create a sub container in the toggle container.
        self.input_container = tk.Frame(bg="white", bd=0, master=toggle_container)
        self.input_container.grid(row=0, column=1, sticky="NSEW")
        pass
    
    def remove(self):
        for widget in self.input_container.winfo_children():
            # Remove all widgets aside from the toggle button.
            if widget.cget("text") != "toggle_button":
                widget.destroy()
        # TODO: Clear self.entries array here.


class VelocityInput(ToggleInput):
    # TODO: Make this work.
    def create(self, field_info):
        pass
    
    
class CircleInput(ToggleInput):
    # TODO: Make this work.
    def create(self, field_info):
        pass


class RectangleInput(ToggleInput):
    # TODO: Make this work as intended.
    def create(self, field_info):
        # Array of relative weights for the column widths.
        widths = [15, 20, 15]
        # Labels between entry fields.
        labels = ["< x <", "< y <"]
        for row, label in enumerate(labels):
            self.input_container.grid_rowconfigure(row, weight=50)
            for column, relative_width in enumerate(widths):
                self.input_container.grid_columnconfigure(column, weight=relative_width, uniform="rectangle_container")
                # Odd columns are entries.
                if column % 2 == 0:
                    input = tk.Entry(bg="white", master=self.input_container, justify="center")
                    # TODO: Figure out the entries array, right now the issue is that create is called multiple times,
                    # unlike in the DomainInputField create function, which means most likely the self.remove function
                    # should also clear the entries array.
                    #input.insert(0, field_info["default"][len(self.entries)])
                    #self.entries.append(input)
                # Even column is a label.
                else:
                    input = tk.Label(text=label, bg="white", padx=10, master=self.input_container)
                # Only add bottom padding to the second row.
                input.grid(row=row, column=column, pady=10, sticky="EW") 


class ToggleInputField(InputField):
    def create(self, text):
        super().create(text)
        # Create images for on and off state of toggle button.
        self.off = ImageTk.PhotoImage(file=os.path.join(os.path.dirname(__file__), self.field_info["image"][0]))
        self.on = ImageTk.PhotoImage(file=os.path.join(os.path.dirname(__file__), self.field_info["image"][1]))
        # Default state of the button
        self.state = self.field_info["default"][1]
        self.toggle_container = tk.Frame(bg="white", master=self.sub_container)
        self.toggle_container.grid(row=0, column=1, sticky="NSEW")
        self.toggle_container.grid_rowconfigure(0, weight=100)
        self.toggle_container.grid_columnconfigure(0, weight=20, uniform="toggle_container")
        self.toggle_container.grid_columnconfigure(1, weight=80, uniform="toggle_container")
        self.button = tk.Button(text="toggle_button", bg="white", activebackground="white", bd=0, \
                                image=self.get_image(), command=self.toggle, master=self.toggle_container)
        self.button.grid(row=0, column=0, pady=10, ipady=10, sticky="NSEW")
        # Type of the toggle button
        type = self.field_info["default"][0]
        # Default input is animation toggle (just a button, hence no class type).
        self.input = None
        if type == "field":
            self.input = VelocityInput(self.toggle_container)
        elif type == "circle":
            self.input = CircleInput(self.toggle_container)
        elif type == "rectangle":
            self.input = RectangleInput(self.toggle_container)
            
        # Update entries array for input retrieval.
        if self.input is not None:
            # Since self.entries is an array, the easiest way to transfer the entry
            # fields up the parent chain is by setting the array to the internal one.
            self.entries = self.input.entries
        else:
            # TODO: Make sure that when parsing the self.entries array, check for
            # tk.Button type vs tk.Entry for the animation toggle button input.
            self.entries.append(self.button)
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
        

class CustomSpecifications(MainMenuButton):
    def press(self):
        super().press()
        # Read the input dictionary from the JSON.
        input_dictionary = self.ui.data[self.name]
        # Count the number of input fields and add 2 rows for the run and back buttons.
        row_count = len(input_dictionary.keys()) + 2
        # Relative height of an invidual input row.
        relative_height = int(100 / row_count)
        for row, (key, field_info) in enumerate(input_dictionary.items()):
            self.ui.container.grid_rowconfigure(row, weight=relative_height)
            self.create_input_object(key, field_info, row)
        # Set alignment for last two buttons.
        self.ui.container.grid_rowconfigure(row_count, weight=relative_height)
        self.ui.container.grid_rowconfigure(row_count - 1, weight=relative_height)
        run_button = tk.Button(text="Run Simulation", fg="black", bg="pink", \
                                command=self.ui.run, master=self.ui.container)
        run_button.grid(row=row_count - 1, column=0, pady=(5, 0), ipady=10, sticky="NSEW")
        back_button = tk.Button(text="Back to Homepage", fg="black", bg="pink", \
                                command=self.ui.create_menu_buttons, master=self.ui.container)
        back_button.grid(row=row_count, column=0, pady=(5, 0), ipady=10, sticky="NSEW")

    def create_input_object(self, text, field_info, row):
        type = field_info["type"]
        if type == "integer" or type == "float":
            input = NumericInputField(self.ui, field_info, row)
        elif type == "toggle":
            input = ToggleInputField(self.ui, field_info, row)
        elif type == "domain":
            input = DomainInputField(self.ui, field_info, row)
        input.create(text)
    
# TODO: Make this work.
class ValidationTasks(MainMenuButton):
    def press(self):
        super().press()

# TODO: Make this work.
class EngineeringSpill(MainMenuButton):
    def press(self):
        super().press()


UserInterface(os.path.join(os.path.dirname(__file__), "input_boxes.json"))