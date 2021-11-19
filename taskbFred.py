import matplotlib.colors
import numpy as np
import simulation
from scipy.optimize import curve_fit
from sympy import symbols
import pylab as pl
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit

# Read reference solution from file.
reference_coordinates, reference_concentration = simulation.read_data_file("reference_solution_1D.dat", [0], [1])
reference_func = interp1d(reference_coordinates, reference_concentration, "linear", fill_value="extrapolate")
reference_data = reference_func(np.linspace(-1,1,64))

# Array of values of different numbers of particles, lower values are repeated more often for accuracy
particle_divisions = 50
particle_array = np.linspace(1000, 30000, num = particle_divisions, dtype=int)
#np.logspace(2, 4, particle_divisions, dtype=int)
num_dts = 10
dts = np.linspace(0.001, 0.1, num = num_dts)

reference_array = np.full((particle_array.size, reference_data.size), reference_data)
bigger_reference = np.full((num_dts, particle_array.size, reference_data.size), reference_data)

def concentration_run(particle_array, dts):
    concentrations = np.array([])
    for index, dt in enumerate(dts):
        for nP in particle_array:
            run = simulation.Simulation(dt, 0.2, -1, 1, -1, 1, nP, 64, 1, 0.1)
            run.add_rectangle([-1, -1], [1, 2], 1)
            run.simulate()
            run.calculate_concentrations()
            concentrations = np.append(concentrations, run.concentrations)
    return np.reshape(concentrations, (dts.size, particle_array.size, run.concentrations.size))

simulation_concentrations = concentration_run(particle_array, dts)

def rmse(reference, simulation):
    rmse_vals = np.sqrt(np.average((reference - simulation) ** 2, axis = 2))
    return rmse_vals

rmse_array = rmse(bigger_reference, simulation_concentrations)
##############################################################################################################################

# Fitting the graph

# def func(w, a, b):
#     return a*(w)**(b)

# pars, cov = curve_fit(func, particle_array, rmse_array)

# a = round(pars[0], 2)
# b = round(pars[1], 2)  # beta


# # Printing the fitting equation 

# E, Np = symbols('E Np')

# answr = a*(Np)**b
last_five = simulation_concentrations[0, -5:-1, :]

plt.figure(figsize=(8, 6))
plt.plot(np.linspace(-1,1,64), reference_data, label = 'Reference')
for index, s in enumerate(last_five):
    plt.plot(np.linspace(-1,1,64), s, label = 'Number of Particles: ' + str(particle_array[index-4]))
plt.legend()
plt.title('ϕ vs x')
plt.ylabel('ϕ')
plt.xlabel('x')
plt.grid()
plt.show()
############################################################################################################################

# Plotting the graph normally

# x_tester = np.linspace(5000, 1000000, 100)
# y = a*(x_tester)**b

plt.figure(figsize=(8, 6))
for index, dt in enumerate(dts):
    plt.scatter(particle_array, rmse_array[index], label = 'DT: ' + str(round(dt, 2)))
# pl.plot(x_tester, y, 'r--', label = 'Trendline')
plt.legend()
plt.title('RMS Error vs Number of Particles')
plt.xlabel('Number of Particles')
plt.ylabel('RMS Error')
plt.grid()
plt.show()

################################################################################################################################
x = particle_array[10:]
print(x.shape)
y = np.reshape(rmse_array, (particle_divisions, num_dts))[10:]
print(y[:,0].shape)

def func(t, a, b):
    return a*t**b

# Plotting the log graph
# m, b = np.polyfit(x, y, 1, w=np.sqrt(y[0][0]))



plt.figure(figsize=(8, 6))
for index, dt in enumerate(dts):
    plt.scatter(x, rmse_array[index][10:], label = 'DT: ' + str(round(dt, 2)))
for dt in range(num_dts):
    popt, pcov = curve_fit(lambda t,a,b: a*t**b,  x,  y[:,dt])
    plt.plot(x, func(x, *popt))
#     plt.plot(x, b[dt] + m[dt]*(x))
plt.legend()
plt.yscale('log')
plt.xscale('log')
plt.title('E vs Np (log scale)')
plt.xlabel('Np')
plt.ylabel('E')
plt.grid()
plt.show()


#################################################################################################################################
# Showing final fitting equation