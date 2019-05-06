'''cli.py -- The CLI to Unity
'''
from pathlib import Path

import click

from unity import unity, plot_stan
# import plot_stan


@click.group()
def cli():
    pass


@cli.command()
@click.argument('data')
@click.option('--model', default='stan_code_simple.txt',
              help='The file containing the Stan model to be used.')
@click.option('--steps', default=1000,
              help='How many steps should the fit be performed for. Default is 1000.')
@click.option('--chains', default=4,
              help='The number of chains to run. At most one chain per core. Default is four.')
@click.option('--interactive', is_flag=True,
              help='Drop into an interactive debugger when fit is done to explore results.')
def run(model, data, steps, chains, interactive):
    """Run Unity on the pickle DATA file."""
    unity.run(model, data, steps, chains, interactive)


@cli.command()
@click.argument('data', nargs=-1)
@click.option('--params', default='snemo+m',
              help='What parameters are you plotting: snemo, snemo+m (default), salt, salt+m?')
@click.option('--kde/--no-kde', default=True,
              help='Make the plot using kde_corner (default) or corner.py.')
def plot(data, params, kde):
    """Make a corner plot from Unity's output. 

    Specifying no [DATA] will plot the last modified output file.

    """
    # print('cli gets ', data)
    # passing no variadic argument passes an empty tuple. 
    if not data:
        latest = ('', 0)
        for output in Path('.').glob('*_fitparams.gzip.pkl'):
            if output.stat().st_mtime > latest[1]:
                latest = (output, output.stat().st_mtime)
        plot_stan.plot((str(latest[0]),), params, kde)
    else:
        plot_stan.plot(data, params, kde)