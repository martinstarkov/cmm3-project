import numpy as np
import matplotlib.pyplot as plt
import time
import matplotlib.animation as animation
from matplotlib.colors import LogNorm, Normalize
from matplotlib.ticker import MaxNLocator
from math import floor

# TODO:
# - Boundary condition function.
# - Read velocity field into grid.
# - Stretch the velocity grid to match the particle grid size.

# Boundary conditions.

x_min = -1
x_max = 1
y_min = -1
y_max = 1

# Particle granularity in each direction per direction.

N_x = 64
N_y = 64

particle_count = N_x * N_y

# Function which adds a circle to the density grid.
def add_circle(x, y, radius, amount, densities):
    for i in range(-radius, radius):
        for j in range(-radius, radius):
            if i * i + j * j < radius * radius:
                densities[x + i, y + j] += amount

# Setup particle arrays.

densities = np.zeros(shape=(N_x, N_y))#(np.random.random((N_x, N_y)) * 255).astype(int)

previous_densities = np.copy(densities)

# Amount that is initially added to density field

value = 1

add_circle(32, 32, 5, value, densities)

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

# Set delta time step.

dt = 0.001

# Function which sets the current density to the previous based on time step.
def add_source(current, previous, N_x, N_y, dt):
    for i in range(0, N_x):
        for j in range(0, N_y):
            current[i, j] += previous[i, j] * dt;

# Function which diffuses the fluid
def diffuse(current, previous, diffusion, N_x, N_y, iterations, dt):
    a = dt * diffusion * (N_x - 2) * (N_y - 2)
    c_reciprocal = 1 / (1 + 6 * a)
    for n in range(iterations):
        for i in range(1, N_x - 1):
            for j in range(1, N_y - 1):
                current[i][j] = (previous[i][j] + \
                        a * ( \
                            current[i + 1][j] \
                            + current[i - 1][j] \
                            + current[i][j + 1] \
                            + current[i][j - 1] \
                            + current[i][j] \
                            + current[i][j] \
                            ) \
                        ) * c_reciprocal
        #set_boundary_conditions(b, current, N_x, N_y);

# Function which advects the fluid.
def advect(current, previous, u, v, N_x, N_y, dt):
    dtx = dt * (N_x - 2)
    dty = dt * (N_y - 2)
    for i in range(1, N_x - 1):
        for j in range(1, N_y - 1):
            # TEMPORARY: Eventually add ability to advect fluid using velocity field here.
            tmp1 = dtx * 0#v[i][j]
            tmp2 = dty * 0#u[i][j]
            x = float(i) - tmp1; 
            y = float(j) - tmp2;
            
            if x < 0.5:
                x = 0.5 
            if x > float(N_x) + 0.5:
                x = float(N_x) + 0.5 
            i0 = floor(x) 
            i1 = i0 + 1.0

            if y < 0.5:
                y = 0.5
            if y > float(N_y) + 0.5:
                y = float(N_y) + 0.5 
            j0 = floor(y)
            j1 = j0 + 1.0 
            
            s1 = x - i0
            s0 = 1.0 - s1
            t1 = y - j0
            t0 = 1.0 - t1
            
            i0i = int(i0);
            i1i = int(i1);
            j0i = int(j0);
            j1i = int(j1);
            
            current[i,j] = s0*(t0*previous[i0i,j0i]+t1*previous[i0i,j1i])+s1*(t0*previous[i1i,j0i]+t1*previous[i1i,j1i]);
    #set_boundary_conditions(b, current, N_x, N_y);

# Setup plot elements (logarithmic heatmap).

fig, ax_lst = plt.subplots()

log_norm = LogNorm(vmin=0.0001, vmax=value)

im = ax_lst.imshow(densities, cmap='BuPu', norm=log_norm)
cbar6 = ax_lst.figure.colorbar(im, ax=ax_lst, ticks=MaxNLocator(2), format='%.e')

# Program loop.

while True:
    t_start = time.time()

    # Diffuse fluid outward.

    add_source(densities, previous_densities, N_x, N_y, dt)
    diffuse(previous_densities, densities, 0.5, N_x, N_y, 4, dt)
    advect(densities, previous_densities, 0, 0, N_x, N_y, dt)
    
    # Update heatmap
    im.set_data(densities)
    
    # Reset previous densities for the next cycle
    previous_densities = np.copy(densities)
    
    plt.pause(0.0001)
    
    t_end = time.time()
    #print("Sum of fluid: " + str(np.sum(densities)))
    #print("fps = {0}".format(999 if t_end == t_start else 1/(t_end-t_start)))