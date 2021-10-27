from scipy.spatial import cKDTree
from matplotlib import animation
import numpy as np
import matplotlib.pyplot as plt

# TODO: Modify this formula to match the one in the slides.
def diffuse(fluid_coordinates, velocities, dt):
    fluid_coordinates += velocities * dt

def simulate(fluid_coordinates, field_vectors, spatial_field, dt):
    _, indexes = spatial_field.query(fluid_coordinates)
    velocities = field_vectors[indexes]
    diffuse(fluid_coordinates, velocities, dt)

def animate(step, dt, axes, fluid_coordinates, spatial_field, field_vectors, points):
    simulate(fluid_coordinates, field_vectors, spatial_field, dt)
    axes.set_title("Time: " + str(round(step, 3)))
    points.set_data(fluid_coordinates[:,0], fluid_coordinates[:,1])
    return points

def setup_plot(x_min, x_max, y_min, y_max):
    figure = plt.figure()
    axes = plt.axes()
    axes.set_xlim(x_min, x_max)
    axes.set_ylim(y_min, y_max)
    return figure, axes

def animated_particle_diffusion(steps, dt, x_min, x_max, y_min, y_max, fluid_coordinates, spatial_field, field_vectors):
    figure, axes = setup_plot(x_min, x_max, y_min, y_max)
    points, = axes.plot(fluid_coordinates[:,0], fluid_coordinates[:,1], 'o')
    anim = animation.FuncAnimation(figure, animate, fargs=(dt, axes, fluid_coordinates, spatial_field, field_vectors, points), frames=steps, interval=1, repeat=False)    
    plt.show()

def static_particle_diffusion(steps, dt, x_min, x_max, y_min, y_max, fluid_coordinates, spatial_field, field_vectors):
    figure, axes = setup_plot(x_min, x_max, y_min, y_max)
    for i in range(steps):
        simulate(fluid_coordinates, field_vectors, spatial_field, dt)
    points, = axes.plot(fluid_coordinates[:,0], fluid_coordinates[:,1], 'o')
    plt.show()

def generate_random_particles(N_p, x_min, x_max, y_min, y_max):
    return np.random.rand(N_p, 2) * [x_max - x_min, y_max - y_min] + [x_min, y_min]

def read_data_file(file, *args):
    return [np.loadtxt(file, usecols=tuple(c)) for c in args]

def display_vector_field(coordinates, vectors):
    plt.quiver(coordinates[:,0], coordinates[:,1], vectors[:,0], vectors[:,1])
    plt.show()

field_file = "velocityCMM3.dat"

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

t_max = 0.4 # Total simulation time.
h = 0.01 # Time step.
steps = int(t_max / h)

# Read vector field data from file.
field_coordinates, field_vectors = read_data_file(field_file, [0, 1], [2, 3])
spatial_field = cKDTree(field_coordinates)

display_vector_field(field_coordinates, field_vectors)

fluid_coordinates = generate_random_particles(N_p, x_min, x_max, y_min, y_max)
static_particle_diffusion(steps, h, x_min, x_max, y_min, y_max, fluid_coordinates, spatial_field, field_vectors)

# fluid_coordinates = generate_random_particles(N_p, x_min, x_max, y_min, y_max)
# animated_particle_diffusion(steps, h, x_min, x_max, y_min, y_max, fluid_coordinates, spatial_field, field_vectors)