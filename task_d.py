import matplotlib.colors
import simulation
import os

def custom_colour_map():
    red = [(0.0, 0.0, 1.0), (0.30, 0.5, 1.0),(0.30,0.0,0.0),  (1.0, 0.0, 0.0)]
    green = [(0.0, 0.0, 0.0), (0.30, 0.0, 1.0), (1.0, 1.0, 1.0)]
    blue = [(0.0, 0.0, 0.0), (0.30, 0.5, 1.0),( 0.30,0.0,0.0),  (1.0, 0.0, 0.0)]
    colordict = dict(red=red, green=green, blue=blue)
    color_map = matplotlib.colors.LinearSegmentedColormap('bluegreen', colordict, 256)
    return color_map

# Read vector field data from file.
velocity_coordinates, velocity_vectors = simulation.read_data_file(os.path.join(os.path.dirname(__file__), "velocityCMM3.dat"), [0, 1], [2, 3])

# TODO: Figure out how to make this highlight values of 0.3
#cmap = matplotlib.colors.ListedColormap(color_dictionary.values())
cmap = custom_colour_map()

sim = simulation.Simulation(0.01, 10, -1, 1, -1, 1, 150000, 75, 75, 0.1, cmap, velocity_coordinates, velocity_vectors)

sim.add_circle([0.4, 0.4], 0.1, 1)

sim.animated_concentration()