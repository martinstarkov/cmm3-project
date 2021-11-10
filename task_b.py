import matplotlib.colors
import numpy as np
import simulation

# 0 is red, 1 is blue
color_dictionary = {
    "red": (1, 0, 0),
    "blue": (0, 0, 1),
}

# Read reference solution from file.
reference_coordinates, reference_concentration = simulation.read_data_file("reference_solution_1D.dat", [0], [1])

concentrations = []

for dt in np.linspace(0.01, 0.03, 3):
    run = simulation.Simulation(dt, 0.2, -1, 1, -1, 1, 65536, 64, 1, 0.1)
    run.add_rectangle([-1, -1], [1, 2], 1)
    run.simulate()
    run.calculate_concentrations()
    concentrations.append(run.concentrations)

#print(reference_coordinates)
#print(reference_concentration)

for concentration in concentrations:
    print(concentrations)