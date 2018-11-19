from matplotlib import use
use("PDF")
import gzip
import corner
import sys
import matplotlib.pyplot as plt
import numpy as np
import pickle

fit_params = pickle.load(gzip.open(sys.argv[1], 'rb'))

params_to_plot = []
labels = []

for key in fit_params:
    print (key)

for param in ["MB", "sigma_int", "coeff", "outl_frac"]:
    if len(fit_params[param].shape) == 1:
        params_to_plot.append(fit_params[param])
        labels.append(param)
    else:
        for i in range(fit_params[param].shape[1]):
            params_to_plot.append(fit_params[param][:,i])
            labels.append(param + "_" + str(i))
params_to_plot = np.array(params_to_plot).T
            
fig = corner.corner(params_to_plot, labels = labels, show_titles = True, title_fmt = ".3f")
plt.savefig("corner.pdf")
plt.close()
