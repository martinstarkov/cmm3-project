#variables will be defined beforehand so dummy variables will be used instead


#Stochastic differential equations (NOT NEEDED!)
DXp = u*dt+((2D)**0.5)*DWx
DYp = v*dt+((2D)**0.5)*DWy

#u and v are the velocities of the particle
#D is the gas diffusivity constant
#DWx and DWy are Wiener processes

#Solutions to the stochastic differential equations
Xnext = x + u*h + ((2D)**0.5)*((h)**0.5)*randomx
Ynext = y + u*h + ((2D)**0.5)*((h)**0.5)*randomy

#h is the time step
#randomx and randomy are simply random numbers with 0 mean, unity variance?

def diffusion(l1,l2,h1,h2,n)

