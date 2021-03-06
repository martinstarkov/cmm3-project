from sys import platform as system_platform
from typing import Dict
from tkinter.filedialog import askopenfile
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import animation
import tkinter as tk
import numpy as np
import sys
import json
import simulation
import validation
import utility

"""
This file implements all the user interface related functionality 
and acts as an entry point to the application.
"""

# Tkinter embedded plot fix for macOS.
if system_platform == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

# Check for correct python version.
if sys.version_info[0:2] < (3, 7):
    raise Exception('GUI requires at least Python 3.7 to run')

"""
These variables alias indexes. This improves code
readability when accessing multi-dimensional arrays.
"""
X = 0
Y = 1
# Used for naming plot axes based on the above dimension alias.
dimension_labels = {
    0: "X",
    1: "Y"
}

"""
Parent user interface class which creates a graphical
window and branches the program out to specific tasks.
"""
class UserInterface(object):
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        # Create Tkinter window of given size and grid configuration.
        self.root = utility.create_root("700x700+0+0")
        self.root.title("Diffusion and Advection Simulator")
        # Create an inner frame container for the contents of the UI.
        self.frame = utility.create_frame(self.root, 0, 0)
        utility.set_grid_sizes(self.frame, [20, 7, 66, 7], [10, 80, 10],
                               uniform_row="frame", uniform_column="frame")
        self.container = None
        # Load JSON file into a data object and populate the window.
        with open(self.json_file_path) as json_file:
            self.data = json.load(json_file)
            self.create_header()
            self.create_menu_buttons()
            self.root.mainloop()


    def create_header(self):
        """Creates the GUI logo."""
        utility.create_image(self.frame, 
                             utility.relative_to_absolute(__file__, "logo.png"), 0, 1)
        # Create the GUI instruction text.
        # (modified by main menu buttons when they are pressed).
        self.label_text = "Please choose a mode of operation."
        self.label = utility.create_label(self.frame, self.label_text, 1, 1)


    def create_menu_buttons(self):
        """Creates the main menu navigation buttons."""
        utility.clear_widgets(self.container)
        self.label["text"] = self.label_text
        self.container = utility.create_frame(self.frame, 2, 1)
        utility.set_grid_sizes(self.container, [33, 33, 33], [100],
                               uniform_row="container", uniform_column="container")
        # Create individual buttons in the container.
        ChemicalSpill("Animated Chemical Spill", self, 0)
        ValidationTasks("Validation Tasks", self, 1)
        CustomConditions("Custom Conditions", self, 2)


    def embed_plot(self, figure: any, row_heights: any = [80, 4, 4]):
        """Embed the figure into the user interface window.
        Args:
            figure:      Figure to embed in the user interface.
            row_heights: Relative row heights of the ui container. Defaults to [80, 4, 4].
                         which is s based on having a reset plot and back button below the plot.
        """
        canvas = FigureCanvasTkAgg(figure, master=self.container)
        canvas.get_tk_widget().grid(row=0, column=0)
        utility.set_grid_sizes(self.container, row_heights, [100])
        return canvas


"""
Abstract class which represents an input entry field.
"""
class InputField(object):
    def __init__(self, ui: UserInterface, field_info: Dict[str, any], row: int):
        """
        Args:
            ui:         Reference to the user interface class instance.
            field_info: Contains the input field info from the JSON file.
            row:        Row on which to place the user input field.
        """
        self.field_info = field_info
        self.defaults = self.field_info["default"]
        # Used for storing the entry fields of the given input field.
        self.entries = []
        # Create a sub container for the input field and label.
        self.sub_container = utility.create_frame(ui.container, row, 0)
        utility.set_grid_sizes(self.sub_container, columns=[50, 50],
                               uniform_row="sub_container", uniform_column="sub_container")


    def create(self, text: str):
        """
        Determines what occurs when an input field is created on the screen.
        Child classes inherit this and implement their own specific input field formatting.
        Args:
            text: Name of the input entry field from the JSON file.
        """
        self.key = text
        utility.create_label(self.sub_container, text, 0, 0)

"""
All the classes below which inherit from InputField define a create method which expresses
how that type of input field is created. This allows for flexible creation of unique
user interface elements with very little effort.
"""

class NumericInputField(InputField):
    def create(self, text: str):
        # Creates a simple input parameter box with a default value.
        self.entries = utility.create_entry(self.sub_container, 
                                            self.field_info["default"], 
                                            0, 1, width=20)

class DomainInputField(InputField):
    def create(self, text: str):
        domain_container = utility.create_frame(self.sub_container, 0, 1)
        utility.create_label(domain_container, "??? x ???", 0, 1)
        utility.create_label(domain_container, "??? y ???", 1, 1)
        self.entries.append([
            utility.create_entry(domain_container, self.defaults[0][X],
                                 0, 0, sticky="EW", width=5),
            utility.create_entry(domain_container, self.defaults[0][Y],
                                 1, 0, sticky="EW", width=5)])
        self.entries.append([
            utility.create_entry(domain_container, self.defaults[1][X],
                                 0, 2, sticky="EW", width=5),
            utility.create_entry(domain_container, self.defaults[1][Y],
                                 1, 2, sticky="EW", width=5)])
        utility.set_grid_sizes(domain_container, [50, 50], [40, 20, 40])


class CellInputField(InputField):
    def create(self, text: str):
        cell_container = utility.create_frame(self.sub_container, 0, 1)
        utility.create_label(cell_container, u'N??? =', 0, 0)
        utility.create_label(cell_container, u'N??? =', 1, 0)
        self.entries.append(
            utility.create_entry(cell_container, self.defaults[X],
                                 0, 1, sticky="EW", width=5))
        self.entries.append(
            utility.create_entry(cell_container, self.defaults[Y],
                                 1, 1, sticky="EW", width=5))
        utility.set_grid_sizes(cell_container, [50, 50], [15, 85])


"""
Parent class for toggleable input entry fields.
Can also be used without inheritence (not abstract).
"""
class ToggleInputField(InputField):
    def create(self, text: str):
        super().create(text)
        # Create sub containers for the toggle button and
        # toggleable content and size them correctly.
        container = utility.create_frame(self.sub_container, 0, 1)
        utility.set_grid_sizes(container, [100], [20, 80],
                               uniform_column="toggle_container")
        self.toggle_container = utility.create_frame(container, 0, 0)
        utility.set_grid_sizes(self.toggle_container, [100], [100])
        self.input_container = utility.create_frame(container, 0, 1)

        # Create a toggle button.
        self.state = tk.BooleanVar(value=self.defaults[0])
        toggle_button = tk.Checkbutton(self.toggle_container, bg="white", 
                                       activebackground="white", 
                                       variable=self.state,
                                       onvalue=True, offvalue=False, 
                                       command=self.update)
        toggle_button.grid(row=0, column=0, sticky="NSEW")
        
        if not self.state.get():  # By default, checkbutton starts checked.
            toggle_button.deselect()
        self.entries = [self.state.get()]
        self.update()


    def update(self):
        """Updates the state of the widget containers and entry."""
        if self.state.get():
            self.appear()
        else:
            self.disappear()
        self.entries[0] = self.state.get()


    def appear(self):
        """
        Nothing appears for boolean toggles.
        Overriden with functionality in child classes.
        Defines what occurs when the toggle button becomes ticked (toggled on).
        """
        pass


    def disappear(self):
        """Removes all the non toggle button widgets."""
        utility.clear_widgets(self.input_container)
        self.entries = [self.state.get()]


class VelocityInputField(ToggleInputField):
    def appear(self):
        utility.set_grid_sizes(self.input_container, columns=[100])
        file_container = utility.create_frame(self.input_container, 0, 0)
        utility.create_button(file_container, "Open File",
                              0, 0, self.open_file)
        self.path_label = utility.create_label(
            file_container, "File: " + self.defaults[1], 1, 0)
        self.entries.append(
            utility.relative_to_absolute(__file__, self.defaults[1]))
        utility.set_grid_sizes(file_container, [50, 50], [100])


    def open_file(self):
        """
        Opens a directory browser to prompt the 
        user for a velocity field data file.
        """
        file = askopenfile(mode='r', 
                           filetypes=[('Velocity Field Data Files', '*.dat')])
        if file is not None:
            self.path_label["text"] = "File: " + file.name
            self.entries[1] = file.name
            file.close()


class CircleInputField(ToggleInputField):
    def appear(self):
        utility.set_grid_sizes(self.input_container, columns=[50, 50])
        phi_container = utility.create_frame(self.input_container, 0, 0)
        circle_container = utility.create_frame(self.input_container, 0, 1)
        utility.create_label(phi_container, "?? =", 1, 0)
        utility.create_label(phi_container, "", 0, 0)
        utility.create_label(circle_container, "x", 0, 0)
        utility.create_label(circle_container, "y", 0, 1)
        utility.create_label(circle_container, "radius", 0, 2)
        self.entries.append(
            utility.create_entry(phi_container, self.defaults[1], 
                                 1, 1, sticky="EW", padx=(0, 5), width=5))
        self.entries.append([
            utility.create_entry(circle_container, self.defaults[2][X],
                                 1, 0, sticky="EW", width=5),
            utility.create_entry(circle_container, self.defaults[2][Y],
                                 1, 1, sticky="EW", width=5)])
        self.entries.append(
            utility.create_entry(circle_container, self.defaults[3],
                                 1, 2, sticky="EW", width=5))
        utility.set_grid_sizes(phi_container, [50, 50], [40, 60])
        utility.set_grid_sizes(circle_container, [50, 50], [33, 33, 33])


class RectangleInputField(ToggleInputField):
    def appear(self):
        utility.set_grid_sizes(self.input_container, columns=[50, 50])
        phi_container = utility.create_frame(self.input_container, 0, 0)
        extents_container = utility.create_frame(self.input_container, 0, 1)
        utility.create_label(phi_container, "?? =", 0, 0)
        utility.create_label(extents_container, "??? x ???", 0, 1)
        utility.create_label(extents_container, "??? y ???", 1, 1)
        self.entries.append(
            utility.create_entry(phi_container, self.defaults[1],
                                 0, 1, sticky="EW", padx=(0, 5), width=5))
        self.entries.append([
            utility.create_entry(extents_container, self.defaults[2][X],
                                 0, 0, sticky="EW", width=5),
            utility.create_entry(extents_container, self.defaults[2][Y],
                                 1, 0, sticky="EW", width=5)])
        self.entries.append([
            utility.create_entry(extents_container, self.defaults[3][X],
                                 0, 2, sticky="EW", width=5),
            utility.create_entry(extents_container, self.defaults[3][Y],
                                 1, 2, sticky="EW", width=5)])
        utility.set_grid_sizes(phi_container, [100], [40, 60])
        utility.set_grid_sizes(extents_container, [50, 50], [33, 33, 33])


"""
Dictionary of input types and their associated classes.
Used for generating the user interface based on the JSON configuration file.
"""
input_dictionary = {
    "numeric": NumericInputField,
    "cell": CellInputField,
    "domain": DomainInputField,
    "boolean": ToggleInputField,
    "field": VelocityInputField,
    "circle": CircleInputField,
    "rectangle": RectangleInputField,
}


"""Abstract class which represents main menu buttons."""
class MainMenuButton(object):
    def __init__(self, name: str, ui: UserInterface, row: int):
        """
        Args:
            name: Name and key of the button.
            ui:   Reference to a user interface instance.
            row:  Row number to place the button at.
        """
        self.name = name
        self.ui = ui
        self.data = self.ui.data[self.name]
        self.button = utility.create_button(self.ui.container, name, row, 0,
                                            self.press,sticky="EW", 
                                            pady=10, ipady=40, fg="black", bg="pink")


    def press(self):
        """
        Defines what happens when a main menu button is pressed.
        This is overriden in child classes with specific behavior.
        """
        # Whenever a main menu button is pressed, the container is cleared and
        # the label below the logo is set to the name of the main menu button.
        utility.clear_widgets(self.ui.container)
        self.ui.label["text"] = self.name


"""Responsible for creating and managing the chemical spill plot"""
class ChemicalSpill(MainMenuButton):
    def press(self):
        super().press()
        parameters = self.data["parameters"]
        # Ensure that velocity path is absolute.
        parameters["velocity_field_path"] = utility.relative_to_absolute(
            __file__, parameters["velocity_field_path"])

        self.highlight_threshold = self.data["highlight_threshold"]

        self.sim = simulation.Simulation(parameters)

        figure, self.axes, self.heatmap = utility.create_heatmap(self.sim.concentrations, 
                                                                 self.data["color_map"], 
                                                                 self.sim.animated, 
                                                                 self.sim.min, self.sim.max, 
                                                                 "x", "y")

        # Create an array to store all the highlighted concentrations.
        self.highlighted = np.copy(self.sim.concentrations)

        # Update the top label with relevant information.
        self.ui.label["text"] = self.name + " (animating until t=" + \
                                str(self.sim.time_max) + "s," + \
                                "dt=" + str(self.sim.dt) + "s) \n" + \
                                "Permanently marking all locations where " + \
                                "concentration has ever been > " + \
                                str(self.highlight_threshold)

        utility.create_button(self.ui.container, "Reset Plot", 1, 0, 
                              self.press, pady=(5, 0), ipady=15, 
                              fg="black", bg="pink")
        utility.create_button(self.ui.container, "Back", 2, 0,
                              self.ui.create_menu_buttons, pady=(5, 0),
                              ipady=15, fg="black", bg="pink")

        self.canvas = self.ui.embed_plot(figure)
        # Enables the plot to be animated
        self.anim = animation.FuncAnimation(figure, func=self.animate_plot,
                                            frames=self.sim.steps, interval=1,
                                            repeat=False, blit=False)


    def animate_plot(self, step: int):
        """Animation function called once per step of the simulation.
        Args:
            step: Current step of the simulation.
        """
        self.axes.set_title("Time: " + str(round(step * self.sim.dt, 2)) + "s")
        # Recalculate concentrations every simulation step.
        self.sim.calculate_concentrations()
        # Check if a concentration is above the highlighted 
        # threshold in either array.
        above_threshold = np.logical_or(self.sim.concentrations > self.highlight_threshold,
                                        self.highlighted > self.highlight_threshold)
        # Update the highlighted array with the points 
        # where the threshold is exceeded (masking).
        self.highlighted = np.where(above_threshold, 1.0, self.sim.concentrations)
        self.heatmap.set_array(self.highlighted)
        # Enables plotting t = 0.
        if step > 0:
            self.sim.update()
        self.canvas.draw()


"""Responsible for creating and managing the validation task menu"""
class ValidationTasks(MainMenuButton):
    def press(self):
        super().press()
        parameters = self.data["parameters"]
        # Ensure that reference data file path is absolute.
        parameters["reference_file_path"] = utility.relative_to_absolute(
            __file__, parameters["reference_file_path"])

        self.validation = validation.Validation(parameters)

        # Create sub containers for the task buttons.
        utility.set_grid_sizes(self.ui.container,
                               rows=[20, 40, 20, 20, 10],
                               columns=[100])
        input_container = utility.create_frame(self.ui.container, 1, 0)
        utility.set_grid_sizes(input_container,
                               rows=[50, 50],
                               columns=[20, 20, 20, 15, 15, 15])
        utility.create_label(input_container,
                             "logarithmic particle divisions (int) =", 1, 0)
        utility.create_label(input_container,
                             "linear dt divisions (int) =", 2, 0)
        utility.create_label(input_container,
                             "??? particles (ints) ???", 1, 4)
        utility.create_label(input_container,
                             "??? dts (s) (floats) ???", 2, 4)

        # Store the RMSE optional entries for parsing the data later.
        self.inputs = []
        self.inputs.append(
            utility.create_entry(input_container, 
                                 self.data["rmse"]["particle_divisions"],
                                 1, 1, sticky="EW", padx=(0, 5), width=5))
        self.inputs.append(
            utility.create_entry(input_container, self.data["rmse"]["particle_min"],
                                 1, 3, sticky="EW", width=5))
        self.inputs.append(
            utility.create_entry(input_container, self.data["rmse"]["particle_max"],
                                 1, 5, sticky="EW", width=5))
        self.inputs.append(
            utility.create_entry(input_container, self.data["rmse"]["dt_divisions"],
                                 2, 1, sticky="EW", padx=(0, 5), width=5))
        self.inputs.append(
            utility.create_entry(input_container, self.data["rmse"]["dt_min"],
                                 2, 3, sticky="EW", width=5))
        self.inputs.append(
            utility.create_entry(input_container, self.data["rmse"]["dt_max"],
                                 2, 5, sticky="EW", width=5))

        utility.create_button(self.ui.container, "Plot Reference and Calculated Comparison",
                              0, 0, lambda: self.collect_outputs("reference_comparison"),
                              pady=(5, 10), ipady=14, sticky="EW", fg="black", bg="pink")
        utility.create_button(self.ui.container, "Plot Linear RMS Error vs Number of Particles", 
                              2, 0, lambda: self.collect_outputs("linear"),
                              pady=(5, 0), ipady=14, sticky="EW", fg="black", bg="pink")
        utility.create_button(self.ui.container, "Plot Logarithmic RMS Error vs Number of Particles",
                              3, 0, lambda: self.collect_outputs("log"),
                              ipady=14, sticky="EW", fg="black", bg="pink")
        utility.create_button(self.ui.container, "Back", 4, 0, self.ui.create_menu_buttons,
                              pady=(5, 0), ipady=10, sticky="EW", fg="black", bg="pink")


    def collect_outputs(self, type: str):
        """
        Called by plot buttons, collects and parses user entries
        into a dictionary. If all the required information is found, 
        continues on to plot the requested type of graph.
        Args:
            type: The type of plotting to perform (passed down the call chain).
        """
        if type == "reference_comparison":
            self.plot(type)
        else:
            # Parse the entry field values into the outputs array.
            self.outputs = {}
            keys = list(self.data["rmse"])
            default_values = list(self.data["rmse"].values())
            for index, entry in enumerate(self.inputs):
                self.outputs[keys[index]] = utility.parse_entry(
                    default_values[index], utility.get_entry(entry))
            # Any value of None (invalid) in the outputs dictionary
            # will prevent the button from continuing.
            if not utility.contains_value(self.outputs, None) and self.output_validation(self.outputs):
                self.plot(type)


    def plot(self, type: str):
        """Plots the selected type of rmse / comparison graph.
        Args:
            type: Type of graph to plot (can be "reference_comparison", "linear" or "log")
        """
        figure = None
        if type == "reference_comparison":
            # Obtain particle array for comparison from JSON file.
            particles = np.array(self.data["reference_comparison"]["particles"]).astype(int)
            dt = self.data["reference_comparison"]["dt"]
            # Check that some necessary conditions in case someone modifies the JSON mistakenly.
            assert np.all(particles > 0), \
                   "Particle array for reference comparison cannot have numbers less than 1"
            assert dt <= self.data["parameters"]["time_max"], \
                   "Cannot use greater dt than time max for reference comparison"
            # Create a reference comparison figure.
            figure = self.validation.reference_comparison_figure(particles, dt,
                                                                 line_styles=['--', '-.', ':'])
        else:
            # Convert particle min and max to exponents for logspace domain to work properly.
            # This is essentially taking a number N and turning it into a, where a is N=10^a
            extents = np.log([self.outputs["particle_min"],
                              self.outputs["particle_max"]]) / np.log([10])
            particles = np.logspace(extents[0], extents[1],
                                    self.outputs["particle_divisions"], dtype=int)

            dts = np.linspace(self.outputs["dt_min"], self.outputs["dt_max"],
                              self.outputs["dt_divisions"])

            # Find the RMSE values for given particles and dts, 
            # also retrieve fitting information for the graph.
            rmse_array, fitted_values, fitting_parameters = self.validation.fit_rmse_curve(particles, dts)

            if type == "linear":
                figure = self.validation.rmse_figure(particles, dts, 
                                                     rmse_array, "linear")
            elif type == "log":
                figure = self.validation.rmse_figure(particles, dts, 
                                                     rmse_array, "log",
                                                     fitted_values, 
                                                     fitting_parameters)
                # Print the ?? values in case the user
                # desires to copy them from the console.
                print("?? values: " + str([b for a, b in fitting_parameters]))

        # Clear the Validation Tasks window in preparation for a plot to appear.
        utility.clear_widgets(self.ui.container)

        utility.create_button(self.ui.container, "Back", 1, 0,
                              self.press, pady=(5, 0), ipady=15,
                              fg="black", bg="pink")
        self.ui.embed_plot(figure, row_heights=[96, 4]).draw()


    def output_validation(self, outputs: Dict[str, any]):
        """
        Validates entry field inputs and notifies the user 
        if any or all of them do not fit required criteria.
        Args:
            outputs: Dictionary full of parameters to validate.
        Returns:
            True if all outputs meet the required conditions, false otherwise.
        """
        simulation_max_time = self.validation.sim_args["time_max"]
        valid = utility.check(outputs["particle_divisions"] > 0,
                              "Number of particle divisions must be greater than 0") & \
                utility.check(outputs["particle_min"] > 0,
                              "Minimum number of particles must be greater than 0") & \
                utility.check(outputs["particle_max"] > 0,
                              "Maximum number of particles must be greater than 0") & \
                utility.check(outputs["particle_max"] > outputs["particle_min"],
                              "Maximum number of particles must be greater than minimum") & \
                utility.check(outputs["dt_divisions"] > 0,
                              "Number of time step divisions must be greater than 0") & \
                utility.check(outputs["dt_min"] > 0,
                              "Minimum time step must be greater than 0") & \
                utility.check(outputs["dt_max"] > 0,
                              "Maximum time step must be greater than 0") & \
                utility.check(outputs["dt_max"] > outputs["dt_min"],
                              "Maximum time step must be greater than minimum") & \
                utility.check(outputs["dt_max"] <= simulation_max_time,
                              "Maximum time step cannot exceed simulation maximum time (" + \
                              str(simulation_max_time) + ")")
        return valid


"""Responsible for creating and managing the custom conditions menu"""
class CustomConditions(MainMenuButton):
    def press(self):
        super().press()

        # Count the number of input fields and add 2 rows for the run and back buttons.
        row_count = len(self.data["fields"].keys()) + 2
        relative_height = int(100 / row_count)
        utility.set_grid_sizes(self.ui.container,
                               rows=np.full(row_count, relative_height))

        self.inputs = []
        # Generate and store input field entry boxes based on the json and input dictionary.
        for row, (text, field_info) in enumerate(self.data["fields"].items()):
            # Find the type of input entry to create from the input dictionary.
            input = input_dictionary[field_info["type"]](self.ui, field_info, row)
            # Call the create function of the parent class (to initialize the label).
            super(type(input), input).create(text)
            # Initialize the entry field.
            input.create(text)
            self.inputs.append(input)

        utility.create_button(self.ui.container, "Run Simulation", row_count - 1, 0,
                              self.collect_outputs, pady=(5, 0),ipady=10,
                              fg="black", bg="pink")
        utility.create_button(self.ui.container, "Back", row_count, 0,
                              self.ui.create_menu_buttons, pady=(5, 0), ipady=10,
                              fg="black", bg="pink")

    def collect_outputs(self):
        """
        Called by the run simulation button, collects 
        and parses user entries into a dictionary.
        If all the required information is found,
        continues on to plot the requested type of graph.
        """
        # Parse the user input fields for their values.
        self.outputs = {}
        for input in self.inputs:
            keys = input.field_info["key"]
            defaults = input.field_info["default"]
            # Recrusive parsing for inner lists.
            if isinstance(keys, list):
                for index, entry in enumerate(input.entries):
                    self.outputs[keys[index]] = utility.parse_entry(defaults[index],
                                                                    utility.get_entry(entry))
            else:
                self.outputs[keys] = utility.parse_entry(defaults,
                                                         utility.get_entry(input.entries))
        # Any value of None (invalid) in the outputs dictionary
        # will prevent the button from continuing.
        if not utility.contains_value(self.outputs, None) and self.output_validation(self.outputs):
            self.plot()

    def plot(self):
        """Plots the desired type of concentration graph."""
        utility.clear_widgets(self.ui.container)

        self.sim = simulation.Simulation(self.outputs)

        # Non-animated graphs need to be calculated first.
        if not self.sim.animated:
            self.sim.simulate(print_time=True)
            self.sim.calculate_concentrations()

        figure = None
        one_dimensional_case = False
        
        for i in [X, Y]:
            # If either cell dimension is == 1, store it and 
            # the other axis and switch to the 1D plot case. 
            if self.sim.cell_size[i] == 1:
                one_dimensional_case = True
                self.single_dimension = i
                self.other_dimension = (i + 1) % 2
        if one_dimensional_case:
            # Create an array for the specified domain to plot the concentrations against.
            self.domain = np.linspace(self.sim.min[self.single_dimension],
                                      self.sim.max[self.single_dimension],
                                      self.sim.cell_size[self.other_dimension])
            # Convert the concentration array to 1D.
            single_dimension_concentration = np.reshape(self.sim.concentrations,
                                                        (self.sim.cell_size[self.other_dimension]))
            # Create the figure for the concentration versus (x/y) position plot.
            figure, self.axes, self.lines = utility.create_line_plot(
                self.domain, single_dimension_concentration,
                self.sim.min[self.single_dimension], self.sim.max[self.single_dimension], 
                0, 1, dimension_labels[self.single_dimension], "Concentration ??")
        else:
            # Create the heatmap for concentration plotting.
            figure, self.axes, self.heatmap = utility.create_heatmap(self.sim.concentrations, 
                                                                    self.data["color_map"],
                                                                    self.sim.animated,
                                                                    self.sim.min, self.sim.max,
                                                                    "x", "y")
        if self.sim.animated:
            # Update the label with animation time information.
            self.ui.label["text"] = self.name + " (animating until t=" + \
                                    str(self.sim.time_max) + "s," + \
                                    "dt=" + str(self.sim.dt) + "s)"
        else:
            self.ui.label["text"] = self.name
            self.axes.set_title("Time: " + str(self.sim.time_max) + "s")

        utility.create_button(self.ui.container, "Reset Plot", 1, 0,
                              self.plot, pady=(5, 0), ipady=15,
                              fg="black", bg="pink")
        utility.create_button(self.ui.container, "Back", 2, 0,
                              self.press, pady=(5, 0), ipady=15,
                              fg="black", bg="pink")
        
        self.canvas = self.ui.embed_plot(figure)
        if self.sim.animated:
            # Created after canvas to fix animation for macOS.
            self.anim = animation.FuncAnimation(figure, func=self.animate_plot,
                                                frames=self.sim.steps, fargs=(one_dimensional_case,), 
                                                interval=1, repeat=False)
            

    def animate_plot(self, step: int, one_dimensional: bool):
        """
        Animation function called once per frame of simulation animation, 
        updates the heatmap or 1D line plot with new concentrations.
        Args:
            step:            Current step of the simulation.
            one_dimensional: Whether to use 1D or 2D.
        """
        self.axes.set_title("Time: " + str(round(step * self.sim.dt, 2)) + "s")
        # Recalculate concentrations every simulation step.
        self.sim.calculate_concentrations()
        if one_dimensional:
            # Concentrations array needs to be converted to 1D before it is set.
            self.lines.set_data(self.domain, np.reshape(self.sim.concentrations,
                                                        (self.sim.cell_size[self.other_dimension])))
        else:
            self.heatmap.set_array(self.sim.concentrations)
        # Enables plotting t = 0.
        if step > 0:
            self.sim.update()
        self.canvas.draw()

    def output_validation(self, outputs: Dict[str, any]):
        """
        Validates entry field inputs and notifies the user
        if any or all of them do not fit required criteria.
        All conditions must be met in order for validity to hold.
        Args:
            outputs: Dictionary full of parameters to validate.
        Returns:
            True if all outputs meet the required conditions, false otherwise.
        """
        valid = utility.check(outputs["time_max"] > 0,
                              "Max time must be greater than 0") & \
                utility.check(outputs["dt"] > 0,
                              "Time step must be greater than 0") & \
                utility.check(outputs["dt"] < outputs["time_max"],
                              "Time step cannot exceed maximum time") & \
                utility.check(outputs["diffusivity"] > 0,
                              "Diffusivity must be greater than or equal to 0") & \
                utility.check(outputs["particle_count"] > 0,
                              "Particle count must be greater than 0") & \
                utility.check(outputs["max"][X] > outputs["min"][X],
                              "X_max must be greater than X_min") & \
                utility.check(outputs["max"][Y] > outputs["min"][Y],
                              "Y_max must be greater than Y_min") & \
                utility.check(outputs["cell_size"][X] > 0,
                              "Cell width must be greater than 0") & \
                utility.check(outputs["cell_size"][Y] > 0,
                              "Cell height must be greater than 0")
        if outputs["use_velocity"]:
            # Check that the velocity field file can be read and has 4 columns.
            coordinates, vectors = utility.read_data_file(
                outputs["velocity_field_path"], [0, 1], [2, 3])
            valid &= utility.check(not isinstance(coordinates, type(None)) and \
                                   not isinstance(vectors, type(None)),
                                   "Velocity field data file does not " + \
                                   "contain the required data columns")
        if outputs["use_circle"]:
            valid &= utility.check(outputs["circle_value"] == 0 or \
                                   outputs["circle_value"] == 1,
                                   "Circle concentration must start " + 
                                   "as 0 or 1 (red or blue)")
            valid &= utility.check(outputs["circle_radius"] >= 0,
                                   "Circle radius must be greater than " + \
                                   "or equal to 0")
        if outputs["use_rectangle"]:
            valid &= utility.check(outputs["rectangle_value"] == 0 or \
                                   outputs["rectangle_value"] == 1,
                                   "Rectangle concentration must start " + \
                                   "as 0 or 1 (red or blue)")
        return valid


"""Entry point to the application"""
if __name__ == "__main__":
    UserInterface(utility.relative_to_absolute(__file__, "config.json"))