from scipy.spatial import cKDTree
from matplotlib import animation
import matplotlib.colors
import numpy as np
import matplotlib.pyplot as plt

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

def animate(step, dt, axes, fluid_coordinates, x_min, x_max, y_min, y_max, spatial_field, field_vectors, scatter, particles):
    simulate(fluid_coordinates, x_min, x_max, y_min, y_max, field_vectors, spatial_field, dt)
    axes.set_title("Time: " + str(round(step * dt, 3)))
    scatter.set_offsets(fluid_coordinates)
    scatter.set_array(particles)

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

def animated_particle_diffusion(steps, dt, x_min, x_max, y_min, y_max, fluid_coordinates, spatial_field, field_vectors, particles, color_dictionary):
    figure, axes, scatter = setup_plot(fluid_coordinates, x_min, x_max, y_min, y_max, color_dictionary)
    anim = animation.FuncAnimation(figure, animate, fargs=(dt, axes, fluid_coordinates, x_min, x_max, y_min, y_max, spatial_field, field_vectors, scatter, particles), frames=steps, interval=1, repeat=False)    
    plt.show()

def static_particle_diffusion(steps, dt, x_min, x_max, y_min, y_max, fluid_coordinates, spatial_field, field_vectors, particles, color_dictionary):
    for i in range(steps):
        # TEMPORARY: skip simulating steps in order to test initial conditions.
        pass
        #simulate(fluid_coordinates, x_min, x_max, y_min, y_max, field_vectors, spatial_field, dt)
    figure, axes, scatter = setup_plot(fluid_coordinates, x_min, x_max, y_min, y_max, color_dictionary)
    scatter.set_array(particles)
    plt.show()

def static_concentration_diffusion(steps, dt, x_min, x_max, y_min, y_max, fluid_coordinates, spatial_field, field_vectors, particles, color_dictionary):
    for i in range(steps):
        simulate(fluid_coordinates, x_min, x_max, y_min, y_max, field_vectors, spatial_field, dt)
    figure, axes, scatter = setup_plot(fluid_coordinates, x_min, x_max, y_min, y_max, color_dictionary)

def generate_random_particles(N_p, x_min, x_max, y_min, y_max):
    coordinates = np.random.rand(N_p, 2) * [x_max - x_min, y_max - y_min] + [x_min, y_min]
    particles = np.zeros(N_p, dtype=int)
    return coordinates, particles

def read_data_file(file, *args):
    return [np.loadtxt(file, usecols=tuple(c)) for c in args]

def display_vector_field(coordinates, vectors):
    plt.quiver(coordinates[:, 0], coordinates[:, 1], vectors[:, 0], vectors[:, 1])
    plt.show()

def get_concentration_field(N_x, N_y, coordinates, particles):
    pass

def add_rectangle(coordinates, particles, bottom_left_x, bottom_left_y, width, height, value: int):
    bound_x = np.logical_and(coordinates[:, 0] >= bottom_left_x, coordinates[:, 0] <= bottom_left_x + width)
    bound_y = np.logical_and(coordinates[:, 1] >= bottom_left_y, coordinates[:, 1] <= bottom_left_y + height)
    return np.where(np.logical_and(bound_x, bound_y), value, particles)

def add_circle(coordinates, particles, x, y, radius, value: int):
    distances = (coordinates[:, 0] - x) ** 2 + (coordinates[:, 1] - y) ** 2
    return np.where(distances < radius ** 2, value, particles)

field_file = "velocityCMM3.dat"

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

fluid_coordinates, fluid_particles = generate_random_particles(N_p, x_min, x_max, y_min, y_max)

#fluid_particles = add_circle(fluid_coordinates, fluid_particles, 0.0, 0.0, color_dictionary["blue"])

fluid_particles = add_rectangle(fluid_coordinates, fluid_particles, -1, -1, 1, 2, color_dictionary["blue"])

static_particle_diffusion(steps, h, x_min, x_max, y_min, y_max, fluid_coordinates, spatial_field, field_vectors, fluid_particles, color_dictionary)

animated_particle_diffusion(steps, h, x_min, x_max, y_min, y_max, fluid_coordinates, spatial_field, field_vectors, fluid_particles, color_dictionary)

# get_concentration_field(N_x, N_y, fluid_coordinates, fluid_particles)