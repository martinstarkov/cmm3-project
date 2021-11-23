from scipy.spatial import cKDTree
from typing import List, Dict
import numpy.typing as npt
import numpy as np
import utility

"""
This file implements the mathematics and physics related to the fluid simulation.
Each simulation is represented by an instance of the Simulation class.

The X and Y variables alias indexes. This improves code readability when accessing
multi-dimensional arrays.
"""
X = 0
Y = 1

"""
The Simulation class initializes fluid particles and their coordinates in its constructor.
The user can call the calculate_concentrations() method which will update the
'concentrations' member with the latest 2D concentration grid.

The simulation can be updated to the next step calling the update() method or run
until time_max using simulate().
Methods with double underscores at the front are private (only used internally by the class). 
"""
class Simulation(object):
    def __init__(self, parameters: Dict[str, any]):
        """
        Args:
            parameters: Contains simulation arguments defined by the JSON configuration file or passed by
                        the user interface. Using a dictionary avoids having to pass each individual parameter
                        and store it. It also enables flexibility regarding passing differing initial conditions.
        """
        # Members populated using the dictionary.
        self.__dict__.update(parameters)
        self.__validate_parameters()
        
        # Conversion to numpy arrays important for later calculations.
        self.min = np.array(self.min)
        self.max = np.array(self.max)
        self.cell_size = np.array(self.cell_size)

        # Calculate the number of steps required to reach time max (and an extra step for t = 0).
        self.steps = int(self.time_max / self.dt) + 1

        if self.use_velocity:
            # Read columns [0, 1] and [2, 3] of the data file as the
            # coordinates and vectors of the velocity field respectively.
            self.velocity_coordinates, self.velocity_vectors = utility.read_data_file(self.velocity_field_path,
                                                                                      [0, 1], [2, 3])
            assert self.velocity_coordinates != None, "Could not retrieve velocity coordinates from data file"
            assert self.velocity_vectors != None,     "Could not retrieve velocity vectors from data file"
            """
            A KDTree is a space partioning structure which allows the user to query any coordinate
            using its nearest neighbors. This allows for the retrieval of velocity vectors for the
            positions which may lie between those given in the velocity field data file.
            """
            self.spatial_velocity = cKDTree(self.velocity_coordinates)

        self.__generate_random_particles()

        if self.use_circle:
            self.__add_circle(self.circle_center, self.circle_radius, self.circle_value)

        if self.use_rectangle:
            self.__add_rectangle(self.rectangle_min, self.rectangle_max, self.rectangle_value)

        if self.optimized:
            """
            For Task E, we choose to delete the 'red' particles and use the number of 'blue' particles
            per cell divided by the average density of particles per cell in the whole grid to estimate
            the concentration of each cell.
            Here we delete the 'red' particles and compute the average density of particles per cell
            at the beginning of the simulation.
            """
            red_indexes = np.argwhere(self.particles == 0)
            self.particles = np.delete(self.particles, red_indexes)
            self.coordinates = np.delete(self.coordinates, red_indexes, axis=0)
            self.average_density = self.particles.size / np.prod(self.cell_size)

        # Calculating the concentrations at t = 0 ensures that the 
        # concentrations member is set before the simulation starts.
        self.calculate_concentrations()
    
    
    def __validate_parameters(self):
        """
        Check that no parameter passed to the simulation is outside its expected envelope.
        """
        assert self.time_max > 0,         "Max time must be greater than 0"
        assert self.dt > 0,               "Time step must be greater than 0"
        assert self.dt <= self.time_max,  "Time step cannot exceed maximum time"
        assert self.max[X] > self.min[X], "X_max must be greater than X_min"
        assert self.max[Y] > self.min[Y], "Y_max must be greater than Y_min"
        assert self.particle_count > 0,   "Particle count must be greater than 0"
        assert self.cell_size[X] > 0,     "Cell width must be greater than 0"
        assert self.cell_size[Y] > 0,     "Cell height must be greater than 0"
        assert self.diffusivity >= 0,     "Diffusivity must be greater than or equal to 0"


    def __generate_random_particles(self):
        # Standardize random particle coordinates to the specified min and max domain.
        self.coordinates = np.random.rand(self.particle_count, 2) * (self.max - self.min) + self.min
        
        # Each coordinate 'shares' an index in the below array which represents the
        # value of the particle (0 and 1 for red and blue respectively).
        self.particles = np.zeros(self.particle_count, dtype=int)


    def __add_rectangle(self, minimum: List[float], maximum: List[float], value: int):
        """
        Adds a rectangle to the particle field.
        Args:
            minimum: Left and bottom bounds of the rectangle respectively.
            maximum: Right and top bounds of the rectangle respectively.
            value:   Particle value to be set inside rectangle bounds.
        """
        # Find any points that lie within the x and y bounds of the rectangle.
        in_x_bound = np.logical_and(self.coordinates[:, X] >= minimum[X], 
                                    self.coordinates[:, X] <= maximum[X])
        in_y_bound = np.logical_and(self.coordinates[:, Y] >= minimum[Y],
                                    self.coordinates[:, Y] <= maximum[Y])
        # Set points which lie within both bounds to the desired rectangle value.
        self.particles = np.where(np.logical_and(in_x_bound, in_y_bound), value, self.particles)


    def __add_circle(self, center: List[float], radius: float, value: int):
        """
        Adds a circle to the particle field.
        Args:
            center: Center x and y coordinates of the rectangle.
            radius: Radius of the circle.
            value:  Particle value to be set inside circle bounds.
        """
        # Find the squared Euclidean distances of each particle coordinate to the center of the circle.
        distances = (self.coordinates[:, X] - center[X]) ** 2 + \
                    (self.coordinates[:, Y] - center[Y]) ** 2
        # Set points which lie within the squared radius bound to the desired circle value.
        self.particles = np.where(distances <= radius ** 2, value, self.particles)


    def __compute_lagrangian(self, velocities: npt.ArrayLike):
        """
        Performs the Lagrangian computation in 2 dimensions for each of the particles.
        Args:
            velocities: Either a 2D (x, y) array of velocities for each coordinate or 0 for no velocity.
        """
        self.coordinates += velocities * self.dt + \
                            np.sqrt([2 * self.diffusivity * self.dt]) * \
                            np.random.standard_normal(size=self.coordinates.shape)


    def __enforce_boundary_conditions(self):
        """
        Ensures that any particles moved past the bounds of the container are
        bounced off of the boundary of the container by the exceeded distance.
        
        If bouncing the particle still takes it out of bounds, it will be set
        to the second hit bound. This may occur at the corners of the container or
        if the time step is large enough to move the particle a sizeable distance
        in one simulation step.
        """
        # Regular bounce.
        self.coordinates[:] = np.where(self.coordinates < self.min, 
                                       self.min + (self.min - self.coordinates), 
                                       self.coordinates)
        self.coordinates[:] = np.where(self.coordinates > self.max,
                                       self.max + (self.max - self.coordinates),
                                       self.coordinates)

        # Edge case for second bounces.
        self.coordinates[:] = np.where(self.coordinates < self.min, 
                                       self.min,
                                       self.coordinates)
        self.coordinates[:] = np.where(self.coordinates > self.max, 
                                       self.max,
                                       self.coordinates)


    def update(self):
        """
        This function encapsulates all the desired steps to be applied to
        particles in order to move them one simulation step forward in time.
        
        The cKDTree query call in this method is the bottleneck of the simulation.
        The number of these calls can be reduced by decreasing the number of queried
        coordinates (i.e. particles) in the simulation, as is done in Task E.
        """
        if self.use_velocity:
            # workers=-1 ensures that all CPU threads are used when querying the KDTree.
            _, indexes = self.spatial_velocity.query(self.coordinates, workers=-1)
            velocities = self.velocity_vectors[indexes]
            self.__compute_lagrangian(velocities)
        else:
            self.__compute_lagrangian(0)

        self.__enforce_boundary_conditions()


    def simulate(self, print_time: bool = False):
        """
        Simply runs the simulation until completion, calling the update method
        once for each step of the simulation.
        Args:
            print_time: Whether or not to print the current time step of the simulation
                        in the console. Keeps the user aware of simulation progress.
        """
        for step in range(self.steps):
            if print_time:
                print("Simulation time: " + str(round(step * self.dt, 3)))
            self.update()


    def calculate_concentrations(self):
        """
        In order to find the concentration grid the particle coordinates are first standardized 
        to a [0, 0] -> [1, 1] domain and then a [0, 0] -> [N_x - 1, N_y - 1] integer domain.
        This maintains each particle's relative position while mapping them to cell indexes.
        """
        standardized = (self.coordinates - self.min) / (self.max - self.min)
        cells = np.round(standardized * (self.cell_size - 1), decimals=0).astype(int)

        """
        The number of unique cell indexes is then counted which allows the program to know how many 
        particles are in each cell of the concentration grid. The average of the weighted sum of
        particles (see np.bincount) in each cell gives us the concentration of the cell.
        """
        unique, indexes, count = np.unique(cells, return_inverse=True, return_counts=True, axis=0)
        if self.optimized:
            """
            For Task E, the concentration is estimated by considering just the number of 'blue' particles
            relative to the average density of 'blue' particles per cell at the beginning of the simulation.
            """
            flat_concentrations = count / self.average_density
        else:
            flat_concentrations = np.bincount(indexes, self.particles) / count
        """
        An edge case for no particles in a cell must be considered. This could statistically occur no matter
        the number of particles in the simulation as all particles could move out of a cell in one step.
        We will assume that no particles in a cell will give it a concentration value of 0. 
        
        To create a complete concentration grid, a flattened array of 0s with size Nx * Ny is created.
        The indexes with unique particles can be found in one dimensional form using the equation:
            index = x * width + y
        The concentrations at those indexes are then set, keeping the empty cells as 0.
        """
        self.concentrations = np.zeros(np.prod(self.cell_size))
        occurences = unique[:, X] * self.cell_size[Y] + unique[:, Y]
        self.concentrations[occurences] = flat_concentrations
        # Cap concentrations at 1 for the optimized case.
        self.concentrations = np.where(self.concentrations > 1, 1, self.concentrations)
        # A 90 degree rotation and reshape to 2D is required due to how the indexes were computed in 1D.
        self.concentrations = np.rot90(np.reshape(self.concentrations, self.cell_size))