from scipy import spatial
from scipy.spatial import cKDTree
from matplotlib import animation
import matplotlib.colors
import numpy as np
import matplotlib.pyplot as plt
import math

# TODO: Make colors options for the user (in case of color blindness) by passing the dictionary accessors as function parameters.
# TODO: BUG: Concentration vs particle fields spin in opposite directions.

X = 0
Y = 1

class Simulation(object):
    def __init__(self, dt, t_max, x_min, x_max, y_min, y_max, 
                 particle_count, cell_width, cell_height, diffusivity, 
                 color_map, velocity_coordinates=None, velocity_vectors=None):
        self.dt = dt
        self.steps = int(t_max / self.dt) + 1
        self.min = np.array([x_min, y_min])
        self.max = np.array([x_max, y_max])
        self.particle_count = particle_count
        self.cell_size = np.array([cell_width, cell_height])
        self.diffusivity = diffusivity
        self.cmap = color_map
        self.velocity_coordinates = velocity_coordinates
        self.velocity_vectors = velocity_vectors
        if self.velocity_coordinates is not None:
            self.spatial_velocity = cKDTree(self.velocity_coordinates)
        self.__generate_random_particles()
        
    def __generate_random_particles(self):
        self.coordinates = np.random.rand(self.particle_count, 2) * (self.max - self.min) + self.min
        self.particles = np.zeros(self.particle_count, dtype=int)
        
    def __setup_plot(self):
        # TODO: Possibly add more axis / plot formatting here.
        self.figure, self.axes = plt.subplots()
        self.axes.set_xlim(self.min[X], self.max[X])
        self.axes.set_ylim(self.min[Y], self.max[Y])
        self.figure.colorbar(matplotlib.cm.ScalarMappable(cmap=self.cmap))
        self.scatter = self.axes.scatter(self.coordinates[:, X], self.coordinates[:, Y])
        self.scatter.set_cmap(self.cmap)
        self.axes.set_title("Time: " + str(0))
        self.scatter.set_array(self.particles)
        
    def __diffuse(self, velocities):
        # TODO: Check  that this formula matches the one in the slides.
        self.coordinates += velocities * self.dt + \
                            math.sqrt(2 * self.diffusivity * self.dt) * \
                            np.random.normal(size=self.coordinates.shape)

    def __boundary_conditions(self):
        self.coordinates[:] = np.where(self.coordinates < self.min, 2 * self.min - self.coordinates, self.coordinates)
        self.coordinates[:] = np.where(self.coordinates > self.max, 2 * self.max - self.coordinates, self.coordinates)
        
    def __simulate(self):
        if self.velocity_coordinates is not None and self.velocity_vectors is not None:
            _, indexes = self.spatial_velocity.query(self.coordinates)
            velocities = self.velocity_vectors[indexes]
            self.__diffuse(velocities)
        else:
            self.__diffuse(0)
        self.__boundary_conditions()
        
    def __update(self, step):
        self.__simulate()
        self.axes.set_title("Time: " + str(round(step * self.dt, 3)))
    
    def __get_concentrations(self):
        # Create flattened concentration array.
        concentrations = np.zeros(np.prod(self.cell_size))
        # Coordinates normalized to [0, 0] -> [1, 1] domain.
        normalized = (self.coordinates - self.min) / (self.max - self.min)
        # Convert domain to [0, 0] -> [N_x - 1, N_y - 1] integer domain.
        cells = np.round(normalized * (self.cell_size - 1)).astype(int)
        unique, occurences, count = np.unique(cells, return_inverse=True, return_counts=True, axis=0)
        weights = np.bincount(occurences, self.particles) / count
        # Flattened index in unique array.
        indexes = unique[:, X] + unique[:, Y] * self.cell_size[Y]
        concentrations[indexes] = weights
        return concentrations.reshape(np.flip(self.cell_size))
    
    def __particle_animation(self, step):
        self.__update(step)
        self.scatter.set_offsets(self.coordinates)

    def __concentration_animation(self, step):
        self.__update(step)
        self.heatmap.set_array(self.__get_concentrations())

    def animated_particle(self):
        self.__setup_plot()
        anim = animation.FuncAnimation(self.figure, self.__particle_animation, frames=self.steps, interval=1, repeat=False)    
        plt.show()

    def static_particle(self):
        for i in range(self.steps):
            print("Simulation time: " + str(round(i * self.dt, 3)))
            self.__simulate()
            
        self.__setup_plot()
        self.axes.set_title("Time: " + str(round((self.steps - 1) * self.dt, 3)))
        plt.show()

    def animated_concentration(self):
        self.figure, self.axes = plt.subplots()
        
        self.axes.set_title("Time: " + str(0))
        concentration = self.__get_concentrations()
        self.heatmap = self.axes.imshow(concentration, animated=True, extent=(self.min[X], self.max[X], self.min[Y], self.max[Y]))
        
        self.heatmap.set_cmap(self.cmap)
        self.figure.colorbar(matplotlib.cm.ScalarMappable(cmap=self.cmap))
        
        anim = animation.FuncAnimation(self.figure, self.__concentration_animation, frames=self.steps, interval=1, repeat=False)    
        plt.show()   

    def static_concentration(self):
        self.figure, self.axes = plt.subplots()
        
        for i in range(self.steps):
            print("Simulation time: " + str(round(i * self.dt, 3)))
            self.__simulate()
        
        concentration = self.__get_concentrations()
        self.heatmap = self.axes.imshow(concentration, extent=(self.min[X], self.max[X], self.min[Y], self.max[Y]))
        
        self.axes.set_title("Time: " + str(round((self.steps - 1) * self.dt, 3)))

        self.heatmap.set_cmap(self.cmap)
        self.figure.colorbar(matplotlib.cm.ScalarMappable(cmap=self.cmap))
        
        plt.show()

    def display_vector_field(self):
        if self.velocity_coordinates is not None and self.velocity_vectors is not None:
            plt.quiver(self.velocity_coordinates[:, X], self.velocity_coordinates[:, Y], \
                       self.velocity_vectors[:, X], self.velocity_vectors[:, Y])
            plt.show()

    def add_rectangle(self, bottom_left, size, value: int):
        bound_x = np.logical_and(self.coordinates[:, X] >= bottom_left[X], self.coordinates[:, X] <= bottom_left[X] + size[X])
        bound_y = np.logical_and(self.coordinates[:, Y] >= bottom_left[Y], self.coordinates[:, Y] <= bottom_left[Y] + size[Y])
        self.particles = np.where(np.logical_and(bound_x, bound_y), value, self.particles)
        
    def add_circle(self, center, radius, value: int):
        distances = (self.coordinates[:, X] - center[X]) ** 2 + (self.coordinates[:, Y] - center[Y]) ** 2
        self.particles = np.where(distances < radius ** 2, value, self.particles)



def read_data_file(file, *args):
    return [np.loadtxt(file, usecols=tuple(c)) for c in args]

# 0 is red, 1 is blue
color_dictionary = {
    "red": (1, 0, 0),
    "blue": (0, 0, 1),
}

# Read vector field data from file.
velocity_coordinates, velocity_vectors = read_data_file("velocityCMM3.dat", [0, 1], [2, 3])

#cmap = matplotlib.colors.ListedColormap(color_dictionary.values())
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("gradient", list(color_dictionary.values()), 256)

sim = Simulation(0.01, 0.2, -1, 1, -1, 1, 65536, 64, 64, 0.01, cmap, velocity_coordinates, velocity_vectors)

#sim.display_vector_field()

#sim.add_circle([0.0, 0.0], 0.25, 1)

sim.add_rectangle([-1, -1], [1, 2], 1)

sim.animated_concentration()