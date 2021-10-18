#Conditions

#Task A: general solution of the diffusion advection problem in
#        a 2D rectangular domain

x_min = -1
x_max = 1
y_min = -1
y_max = 1

#x and y define the size of the rectangular domain

#These variables must be definable and changeable by a user

N_x = 64
N_y = 64

#N_x and N_y define the number of cells for each dimension in the rectangular
#domain

#The number of cells must be definable and changeable by a user

#The code must work for when N_y = 1

N_P = "Varies"

#The number of particles is not clearly defined so a suitable value should be
#chosen

########################################################################

#Task B: general solution for a 1D diffusion problem

if x <= 0:
    phi_xy = 1

else:
    phi_xy = 0

    
#phi_xy defines the concentration field for a cell in the rectangular domain

#These conditional statements define the conditions required for the Task B

#In graphical form, the left hand-side is of one chemical and the right-hand side
#is a different chemical

Diffusivity = 0.1

#Self-explanatory

u = 0
v = 0

#U and v represent the velocities in the x and y direction, respectively, which are 0

N_x = 64
N_y = 1

#This is the required quantity of cells for this task

#Since N_y cannot be changed for this task

N_P = "varies"

#N_P defines the number of particles but the value needs to changeable to perform
#multiple simulations for error analysis

t = 0.2

#The solution is to be plotted at this time

h = 0.01

#This is value for the time step is NOT REQUIRED

#The value needs to be changeable to perform multiple simulations

###########################################################################

#Task C: User interface task with no specific conditions

###########################################################################

#Task D: use the code to perform an "engineering simulation"

phi_limit = 0.3

#This is the maximum concentration of the chemical to be acceptable and the code
#must be able to locate areas of the rectangular domain where the cells reach
#a concentration that exceeds this value (water = 0, chemical = 1)

radius = 0.1
phi_chemical = 1
x = 0.4
y = 0.4

#radius defines a circle where the chemical starts

#phi_chemical defines the chemical concentration as being 1

#The circle is to be centred at x = 0.4 and y = 0.4

Diffusivity = 0.1

#Self-explanatory

t = "long"

#t isn't clearly defined; it simply mentions that it needs to be "long enough"
#so t can be whatever we choose it to be (maybe t = 20?)

N_x = 75
N_y = 75

#N_x and N_y can vary between 50 and 100

x_min = -1
x_max = 1
y_min = -1
y_max = 1

#x and y define the size of the rectangular domain and are not to vary

N_P = 150000

#It is recommended that the number of particles is approximately close to
#150,000

#############################################################################

#Task E: Improvement on the mathematical method
