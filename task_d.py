import matplotlib.colors
import simulation

# 0 is red, 1 is blue
color_dictionary = {
    "red": (1, 0, 0),
    "blue": (0, 0, 1),
}

# Read vector field data from file.
velocity_coordinates, velocity_vectors = simulation.read_data_file("velocityCMM3.dat", [0, 1], [2, 3])

# TODO: Figure out how to make this highlight values of 0.3
#cmap = matplotlib.colors.ListedColormap(color_dictionary.values())
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("gradient", list(color_dictionary.values()), 256)

sim = simulation.Simulation(0.01, 10, -1, 1, -1, 1, 150000, 75, 75, 0.1, cmap, velocity_coordinates, velocity_vectors)

sim.add_circle([0.4, 0.4], 0.1, 1)

sim.animated_concentration()