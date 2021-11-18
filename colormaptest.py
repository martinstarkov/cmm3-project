import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


def custom_colour_map():
    red = [(0.0, 0.0, 1.0), (0.30, 0.5, 1.0),(0.30,0.0,0.0),  (1.0, 0.0, 0.0)]
    green = [(0.0, 0.0, 0.0), (0.30, 0.0, 1.0), (1.0, 1.0, 1.0)]
    blue = [(0.0, 0.0, 0.0), (0.30, 0.5, 1.0),( 0.30,0.0,0.0),  (1.0, 0.0, 0.0)]
    colordict = dict(red=red, green=green, blue=blue)
    color_map = LinearSegmentedColormap('bluegreen', colordict, 256)
    return color_map

# Make some illustrative fake data:

x = np.arange(0, np.pi, 0.1)
y = np.arange(0, 2 * np.pi, 0.1)
X, Y = np.meshgrid(x, y)
Z = np.cos(X) * np.sin(Y) * 10

colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]  # R -> G -> B
n_bins = [3, 6, 10, 100]  # Discretizes the interpolation into bins
cmap_name = 'my_list'
fig, axs = plt.subplots(2, 2, figsize=(6, 9))
fig.subplots_adjust(left=0.02, bottom=0.06, right=0.95, top=0.94, wspace=0.05)
for n_bin, ax in zip(n_bins, axs.flat):
    # Create the colormap
    cmap = bluegreen()
    # Fewer bins will result in "coarser" colomap interpolation
    im = ax.imshow(Z, origin='lower', cmap=cmap)
    ax.set_title("N bins: %s" % n_bin)
    fig.colorbar(im, ax=ax)

plt.show()