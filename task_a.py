import matplotlib.colors
import simulation

# 0 is red, 1 is blue
color_dictionary = {
    "red": (1, 0, 0),
    "blue": (0, 0, 1),
}

# Read vector field data from file.
velocity_coordinates, velocity_vectors = simulation.read_data_file("velocityCMM3.dat", [0, 1], [2, 3])

#cmap = matplotlib.colors.ListedColormap(color_dictionary.values())
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("gradient", list(color_dictionary.values()), 256)

sim = simulation.Simulation(0.01, 0.2, -1, 1, -1, 1, 65536, 64, 64, 0.01, cmap, velocity_coordinates, velocity_vectors)

sim.add_rectangle([-1, -1], [1, 2], 1)

sim.animated_concentration()