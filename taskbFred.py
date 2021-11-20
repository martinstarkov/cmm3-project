import numpy as np
import simulation
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import lfilter

# Array of values of different numbers of particles, lower values are repeated more often for accuracy
particle_divisions = 100
particle_array = np.logspace(2, 4, particle_divisions, dtype=int)

# Number of DTs
num_dts = 5
min_dt = 0.001
max_dt = 0.5
dts = np.linspace(min_dt, max_dt, num = num_dts)

# Read reference solution from file.
reference_coordinates, reference_concentration = simulation.read_data_file("reference_solution_1D.dat", [0], [1])
reference_func = interp1d(reference_coordinates, reference_concentration, "linear", fill_value="extrapolate")
reference_data = reference_func(np.linspace(-1,1,64))

def concentration_run(particles, times):
    # Accesses simulation class and returns the concentration data at different dts
    concentrations = np.array([])
    for index, dt in enumerate(times):
        for nP in particles:
            run = simulation.Simulation(dt, 0.2, -1, 1, -1, 1, nP, 64, 1, 0.1)
            run.add_rectangle([-1, -1], [1, 2], 1)
            run.simulate()
            run.calculate_concentrations()
            concentrations = np.append(concentrations, run.concentrations)
    return np.reshape(concentrations, (times.size, particles.size, run.concentrations.size))

def rmse(reference, particles, times):
    # Caldulates the RMSE between the Reference Data and the simulation data, at multiple dts
    bigger_reference = np.full((times.size, particles.size, reference.size), reference)
    simulation_array = concentration_run(particles, times)
    rmse_vals = np.sqrt(np.average((bigger_reference - simulation_array) ** 2, axis = 2))
    return rmse_vals

def setup_plot(scale, title, x_label, y_label):
    # Sets up plot, reduces the amount of repeating code in further functions.
    plt.legend()
    plt.yscale(scale)
    plt.xscale(scale)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid()
    plt.show()

def reference_data_comparison(x, y_reference, particles, dt):
    # Produces a ϕ vs x plot to compare reference data to the simulation data
    y_simulation_array = np.reshape(concentration_run(particles, dt), (particles.size, x.size))
    plt.figure(figsize=(8, 6))
    plt.plot(x, y_reference, label = 'Reference')
    for index, s in enumerate(y_simulation_array):
        plt.plot(x, s, label = 'Number of Particles: ' + str(particles[index]))
    setup_plot("linear", 'Concentrationϕ vs x', 'Concentration ϕ', 'x')

reference_data_comparison(np.linspace(-1,1,64), reference_data, particle_array[-5:-1], np.array([0.2]))

def normal_scale_rmse_plot(reference, times, particles):
    # Produces a normalscale plot of E vs Np
    rmse_array = rmse(reference, particles, times)
    plt.figure(figsize=(8, 6))
    for index, dt in enumerate(dts):
        plt.scatter(particles, rmse_array[index], label = 'DT: ' + str(round(dt, 3)))
    setup_plot("linear", 'RMS Error vs Number of Particles', 'Number of Particles', 'RMS Error')

normal_scale_rmse_plot(reference_data, dts, particle_array)

def log_scale_rmse_plot(reference, times, particles):
    # Produces a log scale plot of E vs Np with Logarithmic regression lines to find B
    rmse_array = rmse(reference, particles, times)
    smoothing = 7  # the larger n is, the smoother curve will be
    b = [1.0 / smoothing] * smoothing
    a = 1
    def func(t, a, b):
        return a*t**b
    # Plotting the log graph
    plt.figure(figsize=(8, 6))
    for index, dt in enumerate(times):
        plt.scatter(particles, rmse_array[index])
    for index, dt in enumerate(times):
        yy = lfilter(b,a,rmse_array[index])
        popt, pcov = curve_fit(func,  particles,  yy, p0=[1, -0.5])
        plt.plot(particles, func(particles, *popt), label = 'DT: ' + str(round(dt, 3)) + "s, β:" + str(popt[1]))
    setup_plot("log", 'RMS Error vs Number of Particles: Log Scale', 'Number of Particles', 'RMS Error')

log_scale_rmse_plot(reference_data, dts, particle_array)

def find_b(reference, times, particles):
    # Finds the constant B from the RMSE Data
    rmse_array = rmse(reference, particles, times)
    smoothing = 7  # the larger n is, the smoother curve will be
    c = [1.0 / smoothing] * smoothing
    d = 1
    popts = np.array([])
    def func(t, a, b):
        return a*t**b
    for index, dt in enumerate(times):
        yy = lfilter(c,d,rmse_array[index])
        popt, pcov = curve_fit(func,  particles,  yy, p0=[1, -0.5])
        popts = np.append(popts, popt)
    return popts

results = find_b(reference_data, dts, particle_array)
print(results)