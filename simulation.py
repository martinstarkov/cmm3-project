from scipy.spatial import cKDTree
import numpy as np
import numpy.typing as npt
import math
import os
from typing import List

# TODO: Add short description at the top of this file.

X = 0
Y = 1

class Simulation(object):
    # If curious why last parameter is **_, have a look at this answer: https://stackoverflow.com/a/43238973.
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        assert self.time_max > 0, "Max time must be greater than 0"
        assert self.dt > 0, "Time step must be greater than 0"
        assert self.dt <= self.time_max, "Time step cannot exceed maximum time"
        assert self.max[X] > self.min[X], "X_max must be greater than X_min"
        assert self.max[Y] > self.min[Y], "Y_max must be greater than Y_min"
        assert self.particle_count > 0, "Particle count must be greater than 0"
        assert self.cell_size[X] > 0, "Cell width must be greater than 0"
        assert self.cell_size[Y] > 0, "Cell height must be greater than 0"
        assert self.diffusivity >= 0, "Diffusivity must be greater than or equal to 0"
        
        self.min = np.array(self.min)
        self.max = np.array(self.max)
        self.cell_size = np.array(self.cell_size)
        
        # Let us consider an example situation: dt = 0.6, t_max = 1.0, 
        # in this case the code will stop after two steps: 0.0 and 0.6.
        # If the user wishes to continue to 1.2 (exceeding t_max by 1)
        # they can round the fraction below before converting to an int.
        self.steps = int(self.time_max / self.dt) + 1
        
        if self.use_velocity:
            # Read vector field data from file.
            self.velocity_coordinates, self.velocity_vectors = read_data_file(self.velocity_field_path, \
                                                                              [0, 1], [2, 3])
            self.spatial_velocity = cKDTree(self.velocity_coordinates)
        
        self.__generate_random_particles()
        
        if self.use_circle:
            self.__add_circle(self.circle_center, self.circle_radius, self.circle_value)
        
        if self.use_rectangle:
            self.__add_rectangle(self.rectangle_min, self.rectangle_max, self.rectangle_value)

    def __generate_random_particles(self):
        self.coordinates = np.random.rand(self.particle_count, 2) * (self.max - self.min) + self.min
        self.particles = np.zeros(self.particle_count, dtype=int)
        
    def __add_rectangle(self, minimum: List[float], maximum: List[float], value: int):
        bound_x = np.logical_and(self.coordinates[:, X] >= minimum[X], self.coordinates[:, X] <= maximum[X])
        bound_y = np.logical_and(self.coordinates[:, Y] >= minimum[Y], self.coordinates[:, Y] <= maximum[Y])
        self.particles = np.where(np.logical_and(bound_x, bound_y), value, self.particles)
        
    def __add_circle(self, center: List[float], radius: float, value: int):
        distances = (self.coordinates[:, X] - center[X]) ** 2 + (self.coordinates[:, Y] - center[Y]) ** 2
        self.particles = np.where(distances < radius ** 2, value, self.particles)
        
    def __lagrangian(self, velocities: npt.ArrayLike):
        self.coordinates += velocities * self.dt + math.sqrt(2 * self.diffusivity * self.dt) * \
                            np.random.standard_normal(size=self.coordinates.shape)

    def __boundary_conditions(self):
        self.coordinates[:] = np.where(self.coordinates < self.min, 2 * self.min - self.coordinates, self.coordinates)
        self.coordinates[:] = np.where(self.coordinates > self.max, 2 * self.max - self.coordinates, self.coordinates)
        # If bouncing the coordinate still takes it out of bounds, set it to the bound.
        # This may occur at the corners of the container or if dt is large
        # enough to move the particle a sizeable distance in one frame.
        self.coordinates[:] = np.where(self.coordinates < self.min, self.min, self.coordinates)
        self.coordinates[:] = np.where(self.coordinates > self.max, self.max, self.coordinates)
        
    def update(self):
        if self.use_velocity:
            _, indexes = self.spatial_velocity.query(self.coordinates)
            velocities = self.velocity_vectors[indexes]
            self.__lagrangian(velocities)
        else:
            self.__lagrangian(0)
        self.__boundary_conditions()

    def simulate(self, print_time: bool = False):
        for step in range(self.steps):
            if print_time:
                print("Simulation time: " + str(round(step * self.dt, 3)))
            self.update()
         
    def calculate_concentrations(self):
        # Create flattened concentration array.
        self.concentrations = np.zeros(np.prod(self.cell_size))
        # Coordinates standardized to [0, 0] -> [1, 1] domain.
        standardized = (self.coordinates - self.min) / (self.max - self.min)
        # Convert domain to [0, 0] -> [N_x - 1, N_y - 1] integer domain.
        cells = np.round(standardized * (self.cell_size - 1), decimals=0).astype(int)
        # Count the number of particles in each unique cell.
        unique, occurences, count = np.unique(cells, return_inverse=True, return_counts=True, axis=0)
        # Get the average of the particles as the concentration value
        weights = np.bincount(occurences, self.particles) / count
        # Determine flattened indexes of unique array.
        indexes = unique[:, Y] + unique[:, X] * self.cell_size[Y]
        # Set concentrations at those indexes to the calculated averages
        # for their corresponding cells.
        self.concentrations[indexes] = weights
        # Turn the concentration array back into its original shape.
        # 90 degree rotation required because of how the indexes are flattened above.
        self.concentrations = np.rot90(np.reshape(self.concentrations, self.cell_size))

def read_data_file(file, *columns):
    data = []
    for column in columns:
        try:
            data.append(np.genfromtxt(file, usecols=tuple(column), invalid_raise=True))
        except:
            print("Could not retrieve " + str(column) + " columns from file " + str(os.path.basename(file)))
            return [None for column in columns]
    return data