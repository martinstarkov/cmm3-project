from scipy.spatial import cKDTree
from matplotlib import animation
import matplotlib.colors
import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
import math
import os
from typing import List, Dict, Tuple

# TODO: Add short description at the top of this file.

X = 0
Y = 1

class Simulation(object):
    # If curious why last parameter is **_, have a look at this answer: https://stackoverflow.com/a/43238973.
    def __init__(self, color_gradient: Dict[str, List[Tuple[float, float, float]]], time_max: float, dt: float, diffusivity: float, \
                 particle_count: int, min: List[float], max: List[float], cell_size: List[int], use_velocity: bool, velocity_field_path: str = "", **_):
        assert time_max > 0, "Max time must be greater than 0"
        assert dt > 0, "Time step must be greater than 0"
        assert dt <= time_max, "Time step cannot exceed maximum time"
        assert max[X] > min[X], "X_max must be greater than X_min"
        assert max[Y] > min[Y], "Y_max must be greater than Y_min"
        assert particle_count > 0, "Particle count must be greater than 0"
        assert cell_size[X] > 0, "Cell width must be greater than 0"
        assert cell_size[Y] > 0, "Cell height must be greater than 0"
        assert diffusivity >= 0, "Diffusivity must be greater than or equal to 0"
        
        self.dt = dt
        self.min = np.array(min)
        self.max = np.array(max)
        self.particle_count = particle_count
        self.cell_size = np.array(cell_size)
        self.diffusivity = diffusivity
        self.use_velocity = use_velocity
    
        self.cmap = matplotlib.colors.LinearSegmentedColormap("", color_gradient, 256)
        
        if self.use_velocity:
            # Read vector field data from file.
            self.velocity_coordinates, self.velocity_vectors = read_data_file(velocity_field_path, [0, 1], [2, 3])
            self.spatial_velocity = cKDTree(self.velocity_coordinates)
        
        # Let us consider an example situation: dt = 0.6, t_max = 1.0, 
        # in this case the code will stop after two steps: 0.0 and 0.6.
        # If the user wishes to continue to 1.2 (exceeding t_max by 1)
        # they can round the fraction below before converting to an int.
        self.steps = int(time_max / self.dt) + 1
            
        self.__generate_random_particles()
        
    def __generate_random_particles(self):
        self.coordinates = np.random.rand(self.particle_count, 2) * (self.max - self.min) + self.min
        self.particles = np.zeros(self.particle_count, dtype=int)
        
    def __lagrangian(self, velocities: npt.ArrayLike):
        self.coordinates += velocities * self.dt + math.sqrt(2 * self.diffusivity * self.dt) * \
                            np.random.normal(size=self.coordinates.shape)

    def __boundary_conditions(self):
        self.coordinates[:] = np.where(self.coordinates < self.min, 2 * self.min - self.coordinates, self.coordinates)
        self.coordinates[:] = np.where(self.coordinates > self.max, 2 * self.max - self.coordinates, self.coordinates)
        # If bouncing coordinate still takes it out of bounds, set it to the bound.
        self.coordinates[:] = np.where(self.coordinates < self.min, self.min, self.coordinates)
        self.coordinates[:] = np.where(self.coordinates > self.max, self.max, self.coordinates)
        
    def __update(self):
        if self.use_velocity:
            _, indexes = self.spatial_velocity.query(self.coordinates)
            velocities = self.velocity_vectors[indexes]
            self.__lagrangian(velocities)
        else:
            self.__lagrangian(0)
        self.__boundary_conditions()

    def __init_animation(self):
        self.calculate_concentrations()
        self.heatmap.set_array(self.concentrations)

    def __animate(self, step: int):
        self.axes.set_title("Time: " + str(round(step * self.dt, 3)))
        self.calculate_concentrations()
        self.heatmap.set_array(self.concentrations)
        self.__update()

    def simulate(self, print_time: bool = False):
        for step in range(self.steps):
            if print_time:
                print("Simulation time: " + str(round(step * self.dt, 3)))
            self.__update()
            
    def calculate_concentrations(self):
        # Create flattened concentration array.
        self.concentrations = np.zeros(np.prod(self.cell_size))
        # Coordinates normalized to [0, 0] -> [1, 1] domain.
        normalized = (self.coordinates - self.min) / (self.max - self.min)
        # Convert domain to [0, 0] -> [N_x - 1, N_y - 1] integer domain.
        cells = np.round(normalized * (self.cell_size - 1)).astype(int)
        # Count the number of particles in each unique cell.
        unique, occurences, count = np.unique(cells, return_inverse=True, return_counts=True, axis=0)
        # Get the average of the particles as the concentration value
        weights = np.bincount(occurences, self.particles) / count
        # Determine flattened indexes of unique array.
        indexes = unique[:, Y] + unique[:, X] * self.cell_size[Y]
        # Set concentrations at those indexes to the calculated averages
        # for their corresponding cells.
        self.concentrations[indexes] = weights
        # Turn the concentration array back into its original shape (flip required due to reshape axis order).
        self.concentrations = np.rot90(np.reshape(self.concentrations, np.flip(self.cell_size)))
        
    def __setup_concentration_plot(self, animated: bool):
        self.figure, self.axes = plt.subplots()
        self.calculate_concentrations()
        self.heatmap = self.axes.imshow(self.concentrations, animated=animated, extent=(self.min[X], self.max[X], self.min[Y], self.max[Y]))
        self.heatmap.set_cmap(self.cmap)
        self.figure.colorbar(matplotlib.cm.ScalarMappable(cmap=self.cmap))

    def setup_animated_plot(self):
        self.__setup_concentration_plot(animated=True)
        self.axes.set_title("Time: " + str(0))
        self.anim = animation.FuncAnimation(self.figure, func=self.__animate, init_func=self.__init_animation, frames=self.steps, interval=1, repeat=False)

    def setup_static_plot(self):
        self.simulate(print_time=True)
        self.__setup_concentration_plot(animated=False)
        self.axes.set_title("Time: " + str(round((self.steps - 1) * self.dt, 3)))

    def add_rectangle(self, minimum: List[float], maximum: List[float], value: int):
        bound_x = np.logical_and(self.coordinates[:, X] >= minimum[X], self.coordinates[:, X] <= maximum[X])
        bound_y = np.logical_and(self.coordinates[:, Y] >= minimum[Y], self.coordinates[:, Y] <= maximum[Y])
        self.particles = np.where(np.logical_and(bound_x, bound_y), value, self.particles)
        
    def add_circle(self, center: List[float], radius: float, value: int):
        distances = (self.coordinates[:, X] - center[X]) ** 2 + (self.coordinates[:, Y] - center[Y]) ** 2
        self.particles = np.where(distances < radius ** 2, value, self.particles)

def read_data_file(file, *columns):
    data = []
    for column in columns:
        try:
            data.append(np.genfromtxt(file, usecols=tuple(column), invalid_raise=True))
        except:
            print("Could not retrieve " + str(column) + " columns from file " + str(os.path.basename(file)))
            return [None for column in columns]
    return data