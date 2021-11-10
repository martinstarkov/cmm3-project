from scipy.spatial import cKDTree
from matplotlib import animation
import matplotlib.colors
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from sys import platform as sys_pf
import tkinter as tk


if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

# TODO: Make colors options for the user (in case of color blindness) by passing the dictionary accessors as function parameters.

def diffuse(fluid_coordinates, velocities, dt):
    # TODO: Modify this formula to match the one in the slides.
    fluid_coordinates += velocities * dt

def boundary_conditions(fluid_coordinates, x_min, x_max, y_min, y_max):
    # TODO: Remove these once there is a class with these variables.
    min = np.array([x_min, y_min])
    max = np.array([x_max, y_max])
    np.where(fluid_coordinates < min, 2 * min - fluid_coordinates, fluid_coordinates)
    np.where(fluid_coordinates > max, 2 * max - fluid_coordinates, fluid_coordinates)

def simulate(fluid_coordinates, x_min, x_max, y_min, y_max, field_vectors, spatial_field, dt):
    _, indexes = spatial_field.query(fluid_coordinates)
    velocities = field_vectors[indexes]
    diffuse(fluid_coordinates, velocities, dt)
    boundary_conditions(fluid_coordinates, x_min, x_max, y_min, y_max)

def animate(step, dt, axes, fluid_coordinates, x_min, x_max, y_min, y_max, spatial_field, field_vectors, scatter, concentrations, color_dictionary):
    simulate(fluid_coordinates, x_min, x_max, y_min, y_max, field_vectors, spatial_field, dt)
    colors = np.where(concentrations < 0.5, color_dictionary["red"], color_dictionary["blue"])
    axes.set_title("Time: " + str(round(step * dt, 3)))
    scatter.set_offsets(fluid_coordinates)
    scatter.set_array(colors)
    return

def setup_plot(fluid_coordinates, x_min, x_max, y_min, y_max, color_dictionary):
    # TODO: Possibly add more axis / plot formatting here.
    figure, axes = plt.subplots()
    axes.set_xlim(x_min, x_max)
    axes.set_ylim(y_min, y_max)
    cmap = matplotlib.colors.ListedColormap(color_dictionary.keys())
    scatter = axes.scatter(fluid_coordinates[:, 0], fluid_coordinates[:, 1])
    scatter.set_cmap(cmap)
    figure.colorbar(matplotlib.cm.ScalarMappable(cmap=cmap))
    return figure, axes, scatter

def animated_particle_diffusion(root, back, steps, dt, x_min, x_max, y_min, y_max, fluid_coordinates, spatial_field, field_vectors, concentrations, color_dictionary):
    animated_particle_diffusion.figure, axes, animated_particle_diffusion.scatter = setup_plot(fluid_coordinates, x_min, x_max, y_min, y_max, color_dictionary)
    canvas = FigureCanvasTkAgg(animated_particle_diffusion.figure, master=root)
    canvas.get_tk_widget().grid(column=0,row=1)
    label = tk.Label(root,text="SHM Simulation").grid(column=0, row=0)
    back_btn = tk.Button(root, text="Back", padx=10, pady=10, fg="black", bg="pink",command=back)
    back_btn.grid(columnspan=4, column=0, row=6, sticky = tk.W+tk.E)
    animated_particle_diffusion.anim = animation.FuncAnimation( animated_particle_diffusion.figure, animate, fargs=(dt, axes, fluid_coordinates, x_min, x_max, y_min, y_max, spatial_field, field_vectors, animated_particle_diffusion.scatter, concentrations, color_dictionary), frames=steps, interval=1, repeat=False, blit=False)

def static_particle_diffusion(steps, dt, x_min, x_max, y_min, y_max, fluid_coordinates, spatial_field, field_vectors, concentrations, color_dictionary):
    for i in range(steps):
        # TEMPORARY: skip simulating steps in order to test initial conditions.
        pass
        #simulate(fluid_coordinates, x_min, x_max, y_min, y_max, field_vectors, spatial_field, dt)
    figure, axes, scatter = setup_plot(fluid_coordinates, x_min, x_max, y_min, y_max, color_dictionary)
    colors = np.where(concentrations < 0.5, color_dictionary["red"], color_dictionary["blue"])
    scatter.set_array(colors)
    plt.show()

def static_concentration_diffusion(steps, dt, x_min, x_max, y_min, y_max, fluid_coordinates, spatial_field, field_vectors, concentrations, color_dictionary):
    for i in range(steps):
        simulate(fluid_coordinates, x_min, x_max, y_min, y_max, field_vectors, spatial_field, dt)
    figure, axes, scatter = setup_plot(fluid_coordinates, x_min, x_max, y_min, y_max, color_dictionary)

def generate_random_particles(N_p, x_min, x_max, y_min, y_max):
    coordinates = np.random.rand(N_p, 2) * [x_max - x_min, y_max - y_min] + [x_min, y_min]
    concentrations = np.zeros(N_p)
    return coordinates, concentrations

def read_data_file(file, *args):
    return [np.loadtxt(file, usecols=tuple(c)) for c in args]

def display_vector_field(coordinates, vectors):
    plt.quiver(coordinates[:, 0], coordinates[:, 1], vectors[:, 0], vectors[:, 1])
    plt.show()

def add_rectangle(coordinates, concentrations, bottom_left_x, bottom_left_y, width, height, value):
    bound_x = np.logical_and(coordinates[:, 0] >= bottom_left_x, coordinates[:, 0] <= bottom_left_x + width)
    bound_y = np.logical_and(coordinates[:, 1] >= bottom_left_y, coordinates[:, 1] <= bottom_left_y + height)
    return np.where(np.logical_and(bound_x, bound_y), value, concentrations)

def add_circle(coordinates, concentrations, x, y, radius, value):
    distances = (coordinates[:, 0] - x) ** 2 + (coordinates[:, 1] - y) ** 2
    return np.where(distances < radius ** 2, value, concentrations)

field_file = os.path.join(os.path.dirname(__file__), "velocityCMM3.dat")

color_dictionary = {
    "red": 0,
    "blue": 1
}

# Domain size.
x_min = -1
x_max = 1
y_min = -1
y_max = 1

N_p = 5000 # Number of particles.
D = 0.01 # Diffusivity.

# Number of points used to reconstruct the Eulerian field.
N_x = 64
N_y = 64

t_max = 1.0 # Total simulation time.
h = 0.01 # Time step.
steps = int(t_max / h)

# Read vector field data from file.
field_coordinates, field_vectors = read_data_file(field_file, [0, 1], [2, 3])
spatial_field = cKDTree(field_coordinates)

#display_vector_field(field_coordinates, field_vectors)

fluid_coordinates, fluid_concentrations = generate_random_particles(N_p, x_min, x_max, y_min, y_max)

#fluid_concentrations = add_circle(fluid_coordinates, fluid_concentrations, 0.0, 0.0, 0.3, color_dictionary["blue"])

fluid_concentrations = add_rectangle(fluid_coordinates, fluid_concentrations, -1, -1, 1, 2, color_dictionary["blue"])

if __name__ == '__main__':
    static_particle_diffusion(steps, h, x_min, x_max, y_min, y_max, fluid_coordinates, spatial_field, field_vectors, fluid_concentrations, color_dictionary)
    animated_particle_diffusion(steps, h, x_min, x_max, y_min, y_max, fluid_coordinates, spatial_field, field_vectors, fluid_concentrations, color_dictionary)