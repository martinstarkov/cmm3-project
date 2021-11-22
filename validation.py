from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from scipy.signal import lfilter
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy.typing as npt
import numpy as np
import simulation
import utility

# TODO: Add short description of file here.

class Validation(object):
    # Sim args is a dictionary containing all the parameters used by the simulation (dt, max time, cell size, etc).
    def __init__(self, sim_args: Dict[str, any]):
        self.sim_args = sim_args

        coordinates, concentrations = utility.read_data_file(self.sim_args["reference_file_path"], [0], [1])
        assert coordinates is not None, "Could not retrieve coordinates from reference file"
        assert concentrations is not None, "Could not retrieve concentrations from reference file"
        # Create a linear interpolation function for the reference concentration data.
        reference_function = interp1d(coordinates, concentrations, "linear", fill_value="extrapolate")
        
        # Map the reference function onto an array of length equal to the cell width (for comparing with the calculated concentrations).
        self.reference_cells = np.linspace(self.sim_args["min"][0], self.sim_args["max"][1], self.sim_args["cell_size"][0])
        self.reference_concentrations = reference_function(self.reference_cells)

    # Accesses simulation class and returns the concentration data at different time steps.
    def __get_concentrations(self, particles: npt.NDArray, dts: npt.NDArray):
        concentrations = np.array([])
        for dt in dts:
            self.sim_args["dt"] = dt
            for particle_count in particles:
                # Let the user know the progress of the Monte Carlo.
                print("Running simulation with [particle_count=" + str(particle_count) + ", dt=" + str(dt) + "]")
                self.sim_args["particle_count"] = particle_count
                run = simulation.Simulation(self.sim_args)
                # Run the simulation for given dts and particle counts.
                run.simulate()
                # Find and store the concentration at final time.
                run.calculate_concentrations()
                concentrations = np.append(concentrations, run.concentrations)
        # Reshaping the array allows for accessing specific time steps and numbers of particles easier.
        return np.reshape(concentrations, (dts.size, particles.size, run.concentrations.size))

    # Returns the root mean square for different numbers of particles and time steps.
    def __calculate_rmse(self, particles: npt.NDArray, dts: npt.NDArray):
        calculated = self.__get_concentrations(particles, dts)
        # Create an array of reference concentrations that matches 
        # the dimensions of the calculated concentrations.
        reference = np.full(calculated.shape, self.reference_concentrations)
        # Apply the formula for the root mean square for each set of concentrations.
        return np.sqrt(np.average((reference - calculated) ** 2, axis = 2))

    # Produces a concentration versus x position figure to compare reference data to the simulation data.
    def reference_comparison_figure(self, particles: npt.NDArray, dt: float, line_styles: List[str] = None):
        figure = plt.figure(figsize=(8, 6))
        # The style of each line is set to None by default or if not
        # enough line styles are provided for each particle count.
        if line_styles is None or len(line_styles) is not len(particles):
            line_styles = [None] * len(particles)
        calculated_concentrations = self.__get_concentrations(particles, np.array([dt]))
        plt.plot(self.reference_cells, self.reference_concentrations, label="Reference")
        # Plot each of the calculated concentrations on the same plot as the reference concentrations.
        for index, calculated_concentration in enumerate(calculated_concentrations[0]):
            plt.plot(self.reference_cells, calculated_concentration, label="Number of Particles: " + str(particles[index]), linestyle=line_styles[index])
        utility.configure_plot("Concentration ϕ vs x (t=0.2s, dt=" + str(dt) + "s)", "x", "Concentration ϕ", "linear")
        return figure

    # Produces a root mean square error versus number of particles figure with a given scale and optional fitting.
    def rmse_figure(self, particles: npt.NDArray, dts: npt.NDArray, rmse_array: npt.NDArray, scale: str, plot_curve_fits: bool = False, \
                    fitted_values: List[List[float]] = None, fitting_parameters: List[npt.NDArray] = None):
        figure = plt.figure(figsize=(8, 6))
        fit = fitted_values is not None and fitting_parameters is not None
        for index, dt in enumerate(dts):
            dt_label = "dt: " + str(round(dt, 3)) + "s"
            # If curve fitting is desired, the scatter data should not have labels
            # (to avoid labelling both the points and the lines).
            scatter_label = None
            if not fit:
                scatter_label = dt_label
            else:
                # Plot a fitted line of expected rmse against particle count.
                plt.plot(particles, fitted_values[index], label=dt_label + ", β: " + str(round(fitting_parameters[index][1], 3)))
            # Plot the rmse values against particle count.
            plt.scatter(particles, rmse_array[index], label=scatter_label)
        utility.configure_plot("RMS Error vs Number of Particles (" + scale + ")", "Number of Particles", "RMS Error", scale)
        return figure

    # Finds the rmse array, fitted values of rmse and the fitting slope β.
    def fit_rmse_curve(self, particles: npt.NDArray, dts: npt.NDArray):
        rmse_array = self.__calculate_rmse(particles, dts)
        # Smoothing parameter for the data filter.
        smoothing = 3
        # The model we expect for the curve fit (exponential).
        E = lambda N, a, B: a * N ** B
        fitting_parameters = []
        fitted_values = []
        for index in range(len(dts)):
            # Filter the RMSE array values before applying the curve fitting.
            # This is done because the rmse values have a lot of variation between runs.
            filtered_rmse = lfilter([1.0 / smoothing] * smoothing, 1, x=rmse_array[index])
            parameters, _ = curve_fit(E, particles, filtered_rmse, p0=[1, -0.5])
            # Store the fitted values and fitting parameters for printing or graphing later.
            fitting_parameters.append(parameters)
            fitted_values.append(E(particles, *parameters))
        return rmse_array, fitted_values, fitting_parameters