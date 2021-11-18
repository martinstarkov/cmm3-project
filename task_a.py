import matplotlib.colors
import simulation
import os

def custom_specifications(time, step, diffusivity, particle_count, domain, cell_size, animated, velocity_info, circle_info, rectangle_info):
    
    # 0 is red, 1 is blue
    colors = [(1, 0, 0), (0, 0, 1)]

    # Read vector field data from file.
    if velocity_info[0]:
        velocity_coordinates, velocity_vectors = simulation.read_data_file(velocity_info[1], [0, 1], [2, 3])
    else:
        velocity_coordinates = velocity_vectors = None

    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors, 256)

    sim = simulation.Simulation(step, time, domain[0], domain[1], domain[2], domain[3], particle_count, cell_size[0], cell_size[1], diffusivity, cmap, velocity_coordinates, velocity_vectors)

    if circle_info[0]:
        sim.add_circle([circle_info[2], circle_info[3]], circle_info[4], circle_info[1])
    
    if rectangle_info[0]:
        sim.add_rectangle([rectangle_info[2], rectangle_info[4]], [rectangle_info[3], rectangle_info[5]], rectangle_info[1])
    
    if animated:
        sim.animated_concentration()
    else:
        sim.static_concentration()