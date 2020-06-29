'''cli.py -- The CLI to Unity
'''
from pathlib import Path
from collections import namedtuple

import click
from numpy import array
from toml import loads

# from unity import unity, plot_stan
from . import unity, plot_stan


CWD = Path.cwd()  # cwd from where python was called

config = namedtuple('config', 'run plot')


def load_config(file_path):
    """Loads the config file into a config-namedtuple
        
    Parameters:
        input (pathlib.Path):
            takes a Path object for the config file. It does not correct any
            relative path issues.
    
    Returns:
        (namedtuple -- config):
            Contains two sub-structures (run, plot) that will return a
            dictionary of configuration options. You can get your desired
            config-dictionary via `config.run` or `config.plot`.
    """
    with open(file_path) as f:
        return config(**loads(f.read()))


@click.group()
@click.version_option()
def cli():
    pass


@cli.command()
@click.argument('data')
@click.option('--config', help='The path to a config file')
@click.option('--model', default='stan_code_simple.txt',
              help='The file containing the Stan model to be used.')
@click.option('--steps', default=1000,
              help='How many steps should the fit be performed for. Default is 1000. (pystan option `iter`)')
@click.option('--chains', default=4,
              help='The number of chains to run. At most one chain per core. Default is four. (pystan option `chains`)')
@click.option('--interactive', is_flag=True,
              help='Drop into an interactive debugger when fit is done to explore results.')
@click.option('--max_cores', default=1,
              help='The maximum number of cores to use. Chains run in series if needed. Default is one. (pystan option `n_jobs`)')
def run(data, config, model, steps, chains, interactive, max_cores):
    """Run Unity on the pickle DATA file."""
    # load config file if exists, or use cli/default values
    if config is not None:
        config = load_config(CWD/Path(config))
        print(config.run)
        import sys; sys.exit()
        unity.run(**config.run)
    else:
        # over ride with cli, for any argument given,
        unity.run(model, data, steps, chains, interactive, max_cores)


@cli.command()
@click.argument('data', nargs=-1)
@click.option('--params', default='snemo+m',
              help="What parameters are you plotting? Use a set of bash-escaped " + 
                   "strings (aka, use single quotes) 'M$_B$ $\\alpha$ $\\beta$' " + 
                   "or an implemented dataset name: snemo, snemo+m (default), salt, salt+m?")
@click.option('--axlimits', help='Define axis limits with the form "var1_min var1_max var2_min var2_max".')
@click.option('--kde/--no-kde', default=True,
              help='Make the plot using kde_corner (default) or corner.py.')
def plot(data, params, axlimits, kde):
    """Make a corner plot from Unity's output. 

    Specifying no [DATA] will plot the last modified output file.

    """
    # parse data
    # passing no variadic argument passes an empty tuple. 
    if not data:
        latest = ('', 0)
        for output in Path('.').glob('*_fitparams.gzip.pkl'):
            if output.stat().st_mtime > latest[1]:
                latest = (output, output.stat().st_mtime)
        data = (str(latest[0]),)
    
    # parse --axlimits
    # parse before --params so a default axis per dataset is possible
    if axlimits is not None:
        axlimits = array(axlimits.split(' '), dtype=float)
        axlimits = axlimits.reshape(axlimits.size//2, 2)
    else:
        axlimits = []     # Inside of KDE_corner, None throws an error


    # parse --params
    # todo(should this use Enum?)
    plot_params = ["sigma_int", "coeff"]    # default value
    if params == 'snemo+m':
        plot_labels = ['M$_B$', '$\sigma_{unexplained}$', r'$\beta$', r'$\alpha_1$', 
                       r'$\alpha_2$', r'$\alpha_3$', r'$\alpha_4$', r'$\alpha_5$',
                       r'$\alpha_6$', r'$\gamma$']
        # #salt2.4 sigma, beta & alpha values from Suanders et al. 2018 (erratum).
        truths = [None, 0.135, 1.08, -0.16, -0.022, -0.102, -0.014, -0.045, 0.041, -0.0149] 
    elif params == 'salt+m':
        plot_params = ["MB", "sigma_int", "coeff"] 
        plot_labels = ['M$_B$', '$\sigma_{unexplained}$', r'$\alpha$', r'$\beta$', r'$\gamma$']
        truths = [None, None, None, None, 0]
    elif params == 'salt':
        plot_labels = ['$\sigma_{unexplained}$', r'$\alpha$', r'$\beta$']
        truths = [None, None, None]
    elif params == 'snemo2+m':
        plot_params = ["MB", "sigma_int", "coeff"] 
        plot_labels = ['M$_B$', '$\sigma_{unexplained}$', r'$\beta$', r'$\alpha_1$',
                       r'$\gamma$']
        truths = [None, 0.116, None, None, -0.0428]
    elif params == 'mass_local_global':
        plot_labels = ['$\sigma_{unexplained}$', r'$\alpha$', r'$\beta$',
                       r'$\gamma_m$', r'$\gamma_{al}$', r'$\gamma_{ag}$']
        truths = [0.123, -0.15, 3.09, 0, 0, 0]
    elif params == 'mass_local':
        plot_labels = ['$\sigma_{unexplained}$', r'$\alpha$', r'$\beta$',
                       r'$\gamma_m$', r'$\gamma_{al}$']
        truths = [0.123, -0.15, 3.09, 0, 0]
    elif params == 'mass_local_poster':
        plot_params = ["sigma_int", "coeff"]
        plot_labels = ['$\sigma_{unexplained}$', r'$\alpha$', r'$\beta$',
                       r'$\gamma_m$', r'$\gamma_{al}$']
        truths = [0.123, -0.15, 3.09, 0, 0]
    elif params == 'mass_global':
        plot_labels = ['$\sigma_{unexplained}$', r'$\alpha$', r'$\beta$',
                       r'$\gamma_m$', r'$\gamma_{ag}$']
        truths = [0.123, -0.15, 3.09, 0, 0]
    elif params == 'local_global':
        plot_labels = ['$\sigma_{unexplained}$', r'$\alpha$', r'$\beta$',
                       r'$\gamma_{al}$', r'$\gamma_{ag}$']
        truths = [0.123, -0.15, 3.09, 0, 0]
    elif params == 'local':
        plot_labels = ['$\sigma_{unexplained}$', r'$\alpha$', r'$\beta$',
                       r'$\gamma_{al}$']
        truths = [0.123, -0.15, 3.09, 0]
    elif params == 'local_poster':
        plot_params = ["sigma_int", "coeff"]
        plot_labels = ['$\sigma_{unexplained}$', r'$\alpha$', r'$\beta$',
                       r'$\gamma_{al}$']
        truths = [0.123, -0.15, 3.09, 0]
    elif params == 'local_r19_revisit':
        plot_params = ["coeff"]
        plot_labels = [r'$\alpha$', r'$\beta$',
                       r'$\gamma_{al}$']
        truths = [-0.15, 3.09, 0]
    elif params == 'global':
        plot_labels = ['$\sigma_{unexplained}$', r'$\alpha$', r'$\beta$',
                       r'$\gamma_{ag}$']
        truths = [0.123, -0.15, 3.09, 0]
    elif params == 'global_r19_revisit':
        plot_params = ["coeff"]
        plot_labels = [r'$\alpha$', r'$\beta$',
                       r'$\gamma_{al}$']
        truths = [-0.15, 3.09, 0]
        truths = [-0.15, 3.09, 0]
    elif params == 'mass':    #same as 'salt+m'
        plot_labels = ['$\sigma_{unexplained}$', r'$\alpha$', r'$\beta$',
                       r'$\gamma_{m}$']
        truths = [0.123, -0.15, 3.09, 0]
    elif params == 'mass_poster':
        plot_params = ["sigma_int", "coeff"]
        plot_labels = ['$\sigma_{unexplained}$', r'$\alpha$', r'$\beta$',
                       r'$\gamma_{m}$']
    elif params == 'high_and_low_mass':
        plot_labels = ['$\sigma_{unexplained}$', r'$\alpha$', r'$\beta$',
                       r'$\gamma_{al}$']
        truths = [0.122, -0.15, 3.09, 0]
        axlimits =array([[-19.55, -18.75],
                         [0.02, 0.25],
                         [-0.52, 0.12],
                         [ 1.5, 6],
                         [-0.26, 0.12]])
    else:
        if params is not None:
            raise NotImplementedError("User defined params is not yet implemented, https://github.com/pallets/click/issues/1366")
            plot_labels = array(params.split(' '))
            truths = [None, None, None] + [0]*int(len(params)-3)
            if len(params) > 4:
                assert len(plot_labels) == len(truths)

    plot_stan.plot(data, plot_labels, truths, plot_params, axlimits, kde)


# Todo(update to click.echo rather than print)
@cli.command()
def info():
    """Display information about this version of UNITY."""
    import sys
    import os   # should update to subprocess
    import pystan
    import numpy
    
    #unity version
    from click.testing import CliRunner
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    unity_version = result.output.strip('\n').split(' ')[-1]
    print(f'Running UNITY version {unity_version}', '\n')
    
    #python version
    print(f'Running Python version {sys.version}', '\n') # or sys.version_info for python version

    #gcc version
    print('With gcc version')
    os.system('gcc -dumpversion')
    os.system('gcc --version')   # Or could use gcc -dumpversion
    print('')

    #numpy version
    print(f'Using numpy version {numpy.__version__}')
    print(f'Using pystan version {pystan.__version__}')

    # Only load/display script dependencies if asked
    #sncosmo version
    #pandas version -- no needed in unity proper?
