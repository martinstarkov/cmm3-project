from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from scipy.signal import lfilter
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy.typing as npt
import numpy as np
import simulation
import utility

"""
This file implements a class which handles error validation related tasks.
"""

"""
The Validation class encapsulates some of the data required for performing
the error analysis tasks, which makes it easier for the GUI to interface with.
"""
class Validation(object):
    def __init__(self, sim_args: Dict[str, any]):
        """
        Args:
            sim_args: Dictionary containing all the parameters used by the
                      simulation (e.g. dt, max time, cell size, etc).
        """
        self.sim_args = sim_args

        coordinates, concentrations = utility.read_data_file(
            self.sim_args["reference_file_path"], [0], [1])
        assert not isinstance(coordinates, type(None)), \
            "Could not retrieve coordinates from reference file"
        assert not isinstance(concentrations, type(None)), \
            "Could not retrieve concentrations from reference file"

        # Creates a linear interpolation function for the reference concentration data.
        reference_function = interp1d(
            coordinates, concentrations, "linear", fill_value="extrapolate")

        # Maps the reference function onto an array of length equal to the
        # cell width (for comparing with the calculated concentrations).
        self.reference_cells = np.linspace(
            self.sim_args["min"][0], 
            self.sim_args["max"][1], 
            self.sim_args["cell_size"][0])
        self.reference_concentrations = reference_function(self.reference_cells)

    
    def __get_concentrations(self, particles: npt.NDArray, dts: npt.NDArray):
        """
        Generates an array of concentrations for given particle count and time steps.
        Args:
            particles: Particle counts to retrieve the concentrations for.
            dts:       Time steps to to retrieve the concentrations for.
        Returns:
            Multi-dimensional array of concentrations.
            shape=(dts.size, particles.size, concentrations.size)
        """
        concentrations = np.array([])
        for dt in dts:
            self.sim_args["dt"] = dt
            for particle_count in particles:
                # Let the user know the progress of the retrieval.
                print("Running simulation with [particle_count=" +
                      str(particle_count) + ", dt=" + str(dt) + "]")
                self.sim_args["particle_count"] = particle_count
                run = simulation.Simulation(self.sim_args)
                run.simulate()
                # Find and store the concentration at the final time.
                run.calculate_concentrations()
                concentrations = np.append(concentrations, run.concentrations)
        # Reshaping the array allows for accessing specific
        # time steps and numbers of particles easier.
        return np.reshape(concentrations, 
                          (dts.size, particles.size, run.concentrations.size))


    def __calculate_rmse(self, particles: npt.NDArray, dts: npt.NDArray):
        """
        Finds the root mean square error (RMSE) for 
        different particle counts and time steps.
        Args:
            particles: Particle counts to retrieve the RMSE for.
            dts:       Time steps to retrieve the RMSE for.
        Returns:
            Array of RMSE values.
        """
        calculated = self.__get_concentrations(particles, dts)
        # Create an array of reference concentrations that matches
        # the dimensions of the calculated concentrations.
        reference = np.full(calculated.shape, self.reference_concentrations)
        # Apply the formula for the root mean square for each set of concentrations.
        return np.sqrt(np.average((reference - calculated) ** 2, axis=2))


    def reference_comparison_figure(self, particles: npt.NDArray, 
                                    dt: float, line_styles: List[str] = []):
        """
        Produces a concentration versus x position figure 
        to compare reference data to the simulation data.
        Args:
            particles:   Particle counts to compare against reference data.
            dt:          Time step to use for the simulation.
            line_styles: List of line styles to use for the plotted data.
                         Must match length of particles array to be used.
                         Defaults to [] which will make it use solid lines.
        Returns:
            Matplotlib figure of the reference comparison plot.
        """
        figure = plt.figure(figsize=(8, 6))
        # If not enough line styles are provided for
        # each particle count default to solid lines.
        if len(line_styles) is not len(particles):
            line_styles = [None] * len(particles)
        
        calculated = self.__get_concentrations(particles, np.array([dt]))
        plt.plot(self.reference_cells, self.reference_concentrations, label="Reference")
        
        # Plot each of the calculated concentrations on 
        # the same plot as the reference concentrations.
        for index, calculated_concentration in enumerate(calculated[0]):
            plt.plot(self.reference_cells, calculated_concentration,
                     label="Number of Particles: " + str(particles[index]), 
                     linestyle=line_styles[index])
        utility.configure_plot("Concentration ϕ vs x (t=0.2s, dt=" + str(dt) + "s)",
                               "x", "Concentration ϕ", "linear")
        return figure


    def rmse_figure(self, particles: npt.NDArray, dts: npt.NDArray, 
                    rmse_array: npt.NDArray, scale: str,
                    fitted_values: List[any] = None,
                    fitting_parameters: List[any] = None):
        """
        Produces a root mean square error versus number of particles
        figure with a given scale and optional fitting.
        Args:
            particles:          Particle counts to plot.
            dts:                Time steps to label the data sets with.
            rmse_array:         RMSE values to plot.
            scale:              Scale to plot in ("linear" or "log")
            fitted_values:      Array of fitted RMSE values. 
                                Defaults to None (meaning ignored).
            fitting_parameters: Array of fitting parameters. shape=(particles.size, 2).
                                Defaults to None (meaning ignored).
        Returns:
            Matplotlib figure of the RMSE vs particle count plot.
        """
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
                # Add a fitted line of expected RMSE against particle count to the plot.
                plt.plot(particles, fitted_values[index], label=dt_label +
                         ", β: " + str(round(fitting_parameters[index][1], 3)))
            # Add the RMSE values against particle counts to the plot.
            plt.scatter(particles, rmse_array[index], label=scatter_label)
        utility.configure_plot("RMS Error vs Number of Particles (" + scale + ")",
                               "Number of Particles", "RMS Error", scale)
        return figure


    def fit_rmse_curve(self, particles: npt.NDArray, dts: npt.NDArray):
        """ 
        Args:
            particles: Particle counts to find the RMSE and curve fit for.
            dts:       Time steps to find the RMSE and curve fit for.
        Returns:
            RMSE array, fitted values of RMSE, and the fitting slopes (β values).
        """
        rmse_array = self.__calculate_rmse(particles, dts)
        # Smoothing parameter for the data filter.
        smoothing = 3
        # The model we expect for the curve fit (exponential).
        def E(N, a, B): return a * N ** B
        fitting_parameters = []
        fitted_values = []
        for index in range(len(dts)):
            """
            Filter the RMSE array values before applying the curve fitting.
            This is done because the RMSE values have a lot of variation between runs.
            """
            filtered_rmse = lfilter([1.0 / smoothing] * smoothing, 1, x=rmse_array[index])
            # Fit the particle counts and the filtered 
            # RMSE values based on the expected model.
            parameters, _ = curve_fit(E, particles, filtered_rmse, p0=[1, -0.5])
            # Store the fitted values and fitting parameters
            # for printing or graphing later.
            fitting_parameters.append(parameters)
            fitted_values.append(E(particles, *parameters))
        return rmse_array, fitted_values, fitting_parameters