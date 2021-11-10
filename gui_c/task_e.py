from matplotlib import animation
import numpy as np
import matplotlib.pyplot as plt

# Boundary conditions.

x_min = -1
x_max = 1
y_min = -1
y_max = 1

# Particle granularity in each direction per direction.

N_x = 32
N_y = 32

particle_count = N_x * N_y

# Setup particle arrays 
# (will be used later).

densities = np.zeros(shape=(N_x, N_y))
previous_densities = np.copy(densities)

# Extract vector field data from file.

vector_field_file = "velocityCMM3.dat"

field_x_coordinates = np.genfromtxt(vector_field_file, usecols=0)
field_y_coordinates = np.genfromtxt(vector_field_file, usecols=1)
field_x_components = np.genfromtxt(vector_field_file, usecols=2)
field_y_components = np.genfromtxt(vector_field_file, usecols=3)

# Figure out the number of unique coordinates in each dimension.
# This is equivalent to the width and height of the velocity field.
# (will be used later).

field_width = np.unique(field_x_coordinates).size
field_height = np.unique(field_y_coordinates).size

# Function which finds the index of the closest point in
# Euclidean distance when compared to a numpy array of points.
# @return The index of the closest point in the given list of points.
def closest_point_to(point, points):
    assert len(points) == 2
    assert points[0].size == points[1].size
    assert len(point) == 2
    return np.argmin((points[0] - point[0]) ** 2 + (points[1] - point[1]) ** 2)

# Generate random fluid coordinates normalised to the range min to max.

fluid_x_coordinates = np.random.rand(particle_count) * (x_max - x_min) + x_min
fluid_y_coordinates = np.random.rand(particle_count) * (y_max - y_min) + y_min

# Set delta time step.

dt = 0.01

# Animation function which governs the movement of fluid particles.

def animate(frame, points, axes, dt, particle_count, x, y, field_x, field_y, v_x, v_y):
    for i in range(particle_count):
        # Determine the index in the velocity field which is closest to the given coordinate.
        closest_index = closest_point_to([x[i], y[i]], [field_x, field_y])
        # Add the velocity components at that index to each fluid particle's position.
        x[i] += v_x[closest_index] * dt
        y[i] += v_y[closest_index] * dt
    # Update plot elements.
    axes.set_title("Frame: " + str(frame))
    points.set_data(x, y)
    return points

# Setup plot elements.

figure = plt.figure()
axes = plt.axes()
axes.set_xlim(x_min, x_max)
axes.set_ylim(y_min, y_max)
points, = axes.plot(fluid_x_coordinates, fluid_y_coordinates, 'o')

# Create animation object for animating the plot.

anim = animation.FuncAnimation(figure, animate, fargs=(points, axes, dt, particle_count, fluid_x_coordinates, fluid_y_coordinates, field_x_coordinates, field_y_coordinates, field_x_components, field_y_components), frames=1000, interval=1)

# Start animation.

plt.show()