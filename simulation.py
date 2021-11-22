from scipy.spatial import cKDTree
from typing import List, Dict
import numpy.typing as npt
import numpy as np
import utility

# TODO: Add short description at the top of this file.

# These variables alias indexes. This improves code
# readability when accessing multi-dimensional arrays.
X = 0
Y = 1


class Simulation(object):
    # sim_parameters is a dictionary containing key and value pairs of variables and their respective values.
    def __init__(self, sim_parameters: Dict[str, any]):
        # Class member variables are populated using the dictionary.
        self.__dict__.update(sim_parameters)
        # Check that no parameter passed to the simulation is outside its expected envelope.
        assert self.time_max > 0, "Max time must be greater than 0"
        assert self.dt > 0, "Time step must be greater than 0"
        assert self.dt <= self.time_max, "Time step cannot exceed maximum time"
        assert self.max[X] > self.min[X], "X_max must be greater than X_min"
        assert self.max[Y] > self.min[Y], "Y_max must be greater than Y_min"
        assert self.particle_count > 0, "Particle count must be greater than 0"
        assert self.cell_size[X] > 0, "Cell width must be greater than 0"
        assert self.cell_size[Y] > 0, "Cell height must be greater than 0"
        assert self.diffusivity >= 0, "Diffusivity must be greater than or equal to 0"

        # Conversion to numpy arrays for later calculations.
        self.min = np.array(self.min)
        self.max = np.array(self.max)
        self.cell_size = np.array(self.cell_size)

        # Calculate the number of steps required to reach time max (and an extra step for t = 0).
        self.steps = int(self.time_max / self.dt) + 1

        if self.use_velocity:
            # Read vector field data from file.
            self.velocity_coordinates, self.velocity_vectors = utility.read_data_file(self.velocity_field_path,
                                                                                      [0, 1], [2, 3])
            assert self.velocity_coordinates is not None, "Could not retrieve velocity coordinates from data file"
            assert self.velocity_vectors is not None, "Could not retrieve velocity vectors from data file"
            # A KDTree is a space partioning structure which allows the user to query any coordinate
            # using its nearest neighbors. This allows for the retrieval of velocity vectors the positions
            # of which may lie between those given in the velocity field data file.
            self.spatial_velocity = cKDTree(self.velocity_coordinates)

        self.__generate_random_particle_coordinates()

        if self.use_circle:
            self.__add_circle(self.circle_center,
                              self.circle_radius, self.circle_value)

        if self.use_rectangle:
            self.__add_rectangle(self.rectangle_min,
                                 self.rectangle_max, self.rectangle_value)

        self.improved = False
        if self.improved:
            # TODO: Fix this for Task E.
            pass

        # Ensures that the 'self.concentrations' member variable is set
        # before the simulation starts (to graph concentrations at t = 0).
        self.calculate_concentrations()

    def __generate_random_particle_coordinates(self):
        # Standardize the particle coordinates to the specified min and max domain.
        self.coordinates = np.random.rand(
            self.particle_count, 2) * (self.max - self.min) + self.min
        # Each coordinate's index will have a corresponding integer in this array
        # (values 0 or 1 for red and blue respectively).
        self.particles = np.zeros(self.particle_count, dtype=int)

    def __add_rectangle(self, minimum: List[float], maximum: List[float], value: int):
        # Adds a rectangle to the particle field.
        # Find any points that lie within the x and y bounds of the rectangle.
        bound_x = np.logical_and(
            self.coordinates[:, X] >= minimum[X], self.coordinates[:, X] <= maximum[X])
        bound_y = np.logical_and(
            self.coordinates[:, Y] >= minimum[Y], self.coordinates[:, Y] <= maximum[Y])
        # Set points which lie within both bounds to the desired rectangle value.
        self.particles = np.where(np.logical_and(
            bound_x, bound_y), value, self.particles)

    def __add_circle(self, center: List[float], radius: float, value: int):
        # Adds a circle to the particle field.
        # Find the squared distances of each coordinate point to the desired center of the circle.
        distances = (self.coordinates[:, X] - center[X]) ** 2 + \
            (self.coordinates[:, Y] - center[Y]) ** 2
        # Set points which lie within the squared radius to the desired circle value.
        self.particles = np.where(
            distances < radius ** 2, value, self.particles)

    def __compute_lagrangian(self, velocities: npt.ArrayLike):
        # Performs the lagrangian computation in 2 dimensions for each of the particles.
        self.coordinates += velocities * self.dt + np.sqrt([2 * self.diffusivity * self.dt]) * \
            np.random.standard_normal(size=self.coordinates.shape)

    def __enforce_boundary_conditions(self):
        # If a particle goes past the bound of the container, add the exceeded distance to the bound to bounce it off.
        self.coordinates[:] = np.where(
            self.coordinates < self.min, self.min + (self.min - self.coordinates), self.coordinates)
        self.coordinates[:] = np.where(
            self.coordinates > self.max, self.max + (self.max - self.coordinates), self.coordinates)
        # If bouncing the coordinate still takes it out of bounds, set it to the bound.
        # This may occur at the corners of the container or if dt is large
        # enough to move the particle a sizeable distance in one simulation step.
        self.coordinates[:] = np.where(
            self.coordinates < self.min, self.min, self.coordinates)
        self.coordinates[:] = np.where(
            self.coordinates > self.max, self.max, self.coordinates)

    def update(self):
        # This function encapsulates all the desired steps to be applied
        # to particles in order to move them for one step of the simulation.
        if self.use_velocity:
            # This cKDTree query call is the bottleneck of the program.
            # The number of these calls can be reduced by decreasing the number of
            # coordinates (i.e. particles) in the simulation, as outlined in Task E.
            _, indexes = self.spatial_velocity.query(self.coordinates)
            velocities = self.velocity_vectors[indexes]
            self.__compute_lagrangian(velocities)
        else:
            self.__compute_lagrangian(0)
        self.__enforce_boundary_conditions()

    def simulate(self, print_time: bool = False):
        # Calls the update function once for each step of the simulation.
        for step in range(self.steps):
            if print_time:
                print("Simulation time: " + str(round(step * self.dt, 3)))
            self.update()

    """
    In order to calculate the concentration grid, we first create a 
    flattened 1D array of size Nx * Ny full of zeros.
    We then standardize all the particle coordinates to a [0, 0] -> [1, 1] domain.
    Next we convert the above domain to a [0, 0] -> [N_x - 1, N_y - 1] integer domain. 
    This allows for each particle's relative position to remain the same but be
    represented by a cell index instead of a decimal value.
     
    Once we have this cell index form of the particle coordinates, we count the number of unique 
    cell indexes in the array which allows us to know how many particles are in each of the cells. 
    We then compute the sum of the particle values (np.bincount) in each cell by weighting the 
    occurences of each particle by their 0 or 1 value from the particles array. Dividing this sum 
    by the count of particles in the cell gives us the average value of that cell.
    
    Lastly, we must consider that there may be cells with no particles in them (edge case) in which
    case the cell will be assumed to have a concentration value of 0. This requires us to find the 1D
    flattened indexes of the particle values so we know which cells have an average.
    The cells at these indexes are set to their corresponding computed concentration value and the
    concentration array is reshaped back into 2D.
    """

    def calculate_concentrations(self):
        # The process by which this function computes the concentration grid is outlined above.
        self.concentrations = np.zeros(np.prod(self.cell_size))
        standardized = (self.coordinates - self.min) / (self.max - self.min)
        cells = np.round(standardized * (self.cell_size - 1),
                         decimals=0).astype(int)
        unique, occurences, count = np.unique(
            cells, return_inverse=True, return_counts=True, axis=0)
        if self.improved:
            # TODO: Fix this for Task E.
            concentrations = np.bincount(occurences, self.particles) / count
            pass
        else:
            concentrations = np.bincount(occurences, self.particles) / count

        # 2D to 1D flattened indexes of cells with particles in them.
        indexes = unique[:, X] * self.cell_size[Y] + unique[:, Y]
        self.concentrations[indexes] = concentrations
        # A 90 degree rotation is required due to how the indexes were found above.
        self.concentrations = np.rot90(
            np.reshape(self.concentrations, self.cell_size))


# 33.9s with 50x reduction of red.
# 59.3s with no reduction of red.
# 31s with half the particles of each (no reduction).

# # Coordinates standardized to [0, 0] -> [1, 1] domain.
# standardized = (self.coordinates - self.min) / (self.max - self.min)
# # Convert domain to [0, 0] -> [N_x - 1, N_y - 1] integer domain.
# cells = np.round(standardized * (self.cell_size - 1), decimals=0).astype(int)
# unique, occurences, count = np.unique(cells, return_inverse=True, return_counts=True, axis=0)
# weights = np.bincount(occurences)
# blue_occurence_indexes = np.argwhere(occurences is not 0)
# print(blue_occurence_indexes)
# blue_occurences = occurences[blue_occurence_indexes]
# #print()
# self.reference = np.average(blue_occurences)
#self.reference = self.particle_count * 2 / np.prod(self.cell_size)
#self.reference = np.average(weights)
#self.reference = np.max(occurences)
#weights = weights / self.reference
#new_reference = np.max(occurences)
# print(self.reference)
#self.reference = np.max([new_reference, self.reference])
#weights = weights / self.reference
#weights = weights / result
#test = np.linalg.norm(weights)
#weights = weights / test
# print(np.max(weights))
# Determine flattened indexes of unique array.
# mask = np.ones((3, 3))
# mask[1, 1] = 0
# from scipy import ndimage
# result = ndimage.generic_filter(self.concentrations, np.nanmean, footprint=mask, mode='constant', cval=np.NaN)
# self.concentrations = np.where(result is 0, self.concentrations, self.concentrations / result)
# test = np.linalg.norm(self.concentrations)
# self.concentrations = self.concentrations / test

# outputs = {
#     "time_max": 100,
#     "dt": 0.001,
#     "diffusivity": 0.1,
#     "particle_count": 100000,
#     "min": [-1.0, -1.0],
#     "max": [1.0, 1.0],
#     "cell_size": [100, 100],
#     "use_velocity": True,
#     "use_circle": False,
#     "use_rectangle": True,
#     "velocity_field_path": os.path.join(os.path.dirname(__file__), "velocityCMM3.dat"),
#     "rectangle_min": [-1.0, -1.0],
#     "rectangle_max": [0.0, 1.0],
#     "rectangle_value": 1
#     #"circle_center": [0.4, 0.4],
#     #"circle_radius": 0.1,
#     #"circle_value": 1
# }
# import matplotlib.pyplot as plt
# import matplotlib.colors
# import matplotlib.cm
# from matplotlib import animation
# sim = Simulation(**outputs)
# plt.close('all')
# figure, axes = plt.figure(), plt.axes()
# axes.set_xlabel("x")
# axes.set_ylabel("y")
# sim.calculate_concentrations()
# highlighted = np.copy(sim.concentrations)
# heatmap = axes.imshow(sim.concentrations, animated=True, \
#                                 extent=(sim.min[X], sim.max[X], sim.min[Y], sim.max[Y]))
# # Color gradient which goes blue to green to green (0.0 to 0.3 to 1.0).
# #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [(0, 'lime'), (0.7, 'lime'), (0.7, 'g'), (1, 'b')])
# #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [(0, 'b'), (0.3, 'g'), (0.3, 'lime'), (1, 'lime')])
# #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [(0, 'w'), (1, 'b')])
# cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [(0, 'r'), (1, 'b')])
# heatmap.set_cmap(cmap)
# figure.colorbar(matplotlib.cm.ScalarMappable(cmap=cmap))
# def animate_plot(step: int, sim: Simulation):
#     global axes
#     global highlighted
#     global heatmap
#     axes.set_title("Time: " + str(round(step * sim.dt, 3)))
#     sim.calculate_concentrations()
#     above_threshold = np.logical_or(sim.concentrations >= 0.3, highlighted >= 0.3)
#     highlighted = np.where(above_threshold, 1.0, sim.concentrations)
#     heatmap.set_array(sim.concentrations)
#     if step > 0:
#         sim.update()
# anim = animation.FuncAnimation(figure, func=animate_plot, \
#                                 fargs=(sim,), frames=sim.steps, \
#                                 interval=1, repeat=False)
# plt.show()
