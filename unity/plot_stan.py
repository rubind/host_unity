# from matplotlib import use
# use("PDF")
import gzip
import corner
import sys
import pickle

import matplotlib.pyplot as plt
import numpy as np

import kde_corner

def collect_plot_params(fit_params):
    # type: (dict) -> numpy.ndarray
    """Collect the parameters to be plotted from the full UNITY output
    """
    params_to_plot = []
    labels = []
    
    for param in ["MB", "sigma_int", "coeff", "outl_frac"]:
        if len(fit_params[param].shape) == 1:
            params_to_plot.append(fit_params[param])
            labels.append(param)
        else:
            for i in range(fit_params[param].shape[1]):
                params_to_plot.append(fit_params[param][:,i])
                labels.append(param + "_" + str(i))
    
    # to make it compatible with corner.py
    params_to_plot = np.array(params_to_plot).T
    
    return params_to_plot


def plot(file_name, data_type, kde=True):
    # type: (Union(string, tuple), string) -> None
    """Make a corner plot of the UNITY output data.

    Parameters
    ----------
    file_name: string or tuple of strings
        This is the string to the UNITY output file. If a tuple is passed, then 
    data_type: string
        This defines what standardization coefficients should label the
        axis.
    """
    print('Plotting ', file_name)

    if not data_type in ['snemo', 'salt', 'snemo+m', 'salt+m']:
        sys.exit('Model not specified')
    else:
        if data_type == 'snemo+m':
            # plot_labels = ['M$_B$', '$\sigma_{intrinsic}$', 'color', 'c1', 'c2', 'c3',
                      # 'c4', 'c5', 'c6', 'mass', 'outl_frac']
            plot_labels = ['M$_B$', '$\sigma_{intrinsic}$', r'$\beta$', r'$\alpha_1$', r'$\alpha_2$', r'$\alpha_3$',
                      r'$\alpha_4$', r'$\alpha_5$', r'$\alpha_6$', r'$\delta$', r'$f^{outl}$']
            truths = [None, None, None, 0, 0, 0, 0, 0, 0, 0, 0]
        if data_type == 'salt+m':
            plot_labels = ['M$_B$', '$\sigma_{intrinsic}$', r'$\alpha$', r'$\beta$', r'$\delta$', r'$f^{outl}$']
            truths = [None, None, None, None, 0, 0]
    # truths=[None, 0, -0.14, 3.2, 0, 0, 0, None],   # Campbell data
    # labels=['M$_B$', '$\sigma_{intrinsic}$', r'$\alpha$', r'$\beta$', 'mass', 'local age', 'global age', 'outl_frac'],      # Campbell
    

    if type(file_name) == tuple:
        data_sets = [collect_plot_params(pickle.load(gzip.open(f, 'rb'))) for f in file_name]
        FIG_NAME = file_name[:-9] + '_and_others'
    else:
        fit_params = pickle.load(gzip.open(file_name, 'rb'))
        data_sets = [collect_plot_params(fit_params)]
        FIG_NAME = file_name[:-9]
    



    if kde:
        # fig = kde_corner.kde_corner([ 1.4*params_to_plot, params_to_plot, 0.7*params_to_plot], labels=plot_labels, contours = [0.0455003])
        # fig = kde_corner.kde_corner(params_to_plot, labels=plot_labels)
        fig = kde_corner.kde_corner(data_sets, labels=plot_labels, contours = [0.0455003])
    else:
        # plot with corner.py, this only works for 1 data set.
        raise RuntimeWarning('corner.py can only plot one dataset.')
        fig = corner.corner(data_sets[0], 
                            labels=plot_labels, show_titles=True, title_fmt=".3f",
                            truths=truths, quantiles=[.25, .16, .84, .975])
        # fig.suptitle(file_name, fontsize=16)

    # TODO: fix this to work when file_name is a list
    plt.savefig(f"{FIG_NAME}.pdf")
    # plt.savefig('del.pdf')

    plt.close()


if __name__ == '__main__':
    plot(sys.argv[1], sys.argv[2])