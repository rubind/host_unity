'''cli.py -- The CLI to Unity
'''
import click

import unity


@click.group()
def cli():
    pass


@cli.command()
@click.argument('data')
@click.option('--model', default='stan_code_simple.txt')
@click.option('--steps', default=1000,
              help='How many steps should the fit be performed for.')
@click.option('--chains', default=8,
              help='The number of chains to run. At most one chain per core.')
@click.option('--interactive', is_flag=True,
              help='Drop into an interactive debugger when fit is done to explore results.')
def run(model, data, steps, chains, interactive):
    unity.run(model, data, steps, chains, interactive)


@cli.command()
@click.option('--dataset', help='Test data set to build.')
def build(dataset):
    click.echo('Update build_test_dataset.py to work with CLI.')
