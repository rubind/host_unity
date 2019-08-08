'''cli.py -- The CLI to Unity
'''
from pathlib import Path

import click
from numpy import array

from unity import unity, plot_stan

@click.group()
@click.version_option()
def cli():
    pass


@cli.command()
@click.argument('data')
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
def run(model, data, steps, chains, interactive, max_cores):
    """Run Unity on the pickle DATA file."""
    unity.run(model, data, steps, chains, interactive, max_cores)


@cli.command()
@click.argument('data', nargs=-1)
@click.option('--params', default='snemo+m',
              help='What parameters are you plotting: snemo, snemo+m (default), salt, salt+m?')
@click.option('--axlimits', help='Define axis limits with the form "var1_min var1_max var2_min var2_max".')
@click.option('--kde/--no-kde', default=True,
              help='Make the plot using kde_corner (default) or corner.py.')
def plot(data, params, axlimits, kde):
    """Make a corner plot from Unity's output. 

    Specifying no [DATA] will plot the last modified output file.

    """
    # passing no variadic argument passes an empty tuple. 
    if not data:
        latest = ('', 0)
        for output in Path('.').glob('*_fitparams.gzip.pkl'):
            if output.stat().st_mtime > latest[1]:
                latest = (output, output.stat().st_mtime)
        data = (str(latest[0]),)

    axlimits = array(axlimits.split(' '), dtype=float)
    axlimits = axlimits.reshape(axlimits.size//2, 2)

    plot_stan.plot(data, params, axlimits, kde)


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
  # print(f'Running UNITY version {__version__}')
  print(f'Running Python version {sys.version}', '\n') # or sys.version_info for python version
  # print(sys.version_info, '\n')
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