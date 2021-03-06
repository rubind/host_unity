""" Script to generate scripts for fitting the data
"""

import os
import sys
import click
import pickle
import sncosmo
import numpy as np
import pandas as pd
from astropy.table import Table

SCRIPT_DIR = 'scripts'
if not os.path.isdir(SCRIPT_DIR):
    os.makedirs(SCRIPT_DIR)

TEMPLATE = """#!/bin/bash
#$ -N {dataset}_{model}_{err_int}_{start}_{end}
#$ -e /home/samdixon/host_unity/fitting/logs
#$ -o /home/samdixon/host_unity/fitting/logs

/home/samdixon/anaconda3/bin/python /home/samdixon/host_unity/fitting/mcmc_lc_{dataset}_fit.py {model} {start} {end} {err_float} {no_mc}"""

@click.command()
@click.argument('dataset', type=click.Choice(['jla', 'csp', 'ps', 'all']))
@click.option('-m', '--model', default='snemo7', type=click.Choice(['salt2', 'snemo2', 'snemo7']))
@click.option('-e', '--err_floor', default=0., help='Desired error floor as fraction of maximum band flux.')
@click.option('-n', '--njobs', default=16, help='Number of scripts to generate.')
@click.option('-c', '--no_mc', default=False, type=bool)
def cli(dataset, model, err_floor, njobs, no_mc):
    if dataset == 'all':
        for err_floor in [0, 0.01, 0.02, 0.03]:
            for model in ['salt2', 'snemo2', 'snemo7']:
                for dataset in ['jla', 'csp', 'ps']:
                    for no_mc in [0, 1]:
                        make_scripts(dataset, model, err_floor, 16, no_mc)
    else:
        make_scripts(dataset, model, err_floor, 16, no_mc)

def make_scripts(dataset, model, err_floor, njobs, no_mc):
    if dataset == 'jla':
        n_sne = len(os.listdir('/home/samdixon/jla_light_curves/'))
    elif dataset == 'csp':
        n_sne = len(os.listdir('/home/samdixon/CSP_Photometry_DR3/'))
    elif dataset == 'ps':
        data = pd.read_csv('/home/samdixon/foundation_photometry.txt', delimiter=', ', engine='python')
        n_sne = len(data.SN.unique())
    if not no_mc:
        submit_fname = 'submit_{}_{}_{:02d}_mcmc.sh'.format(dataset, model, int(err_floor*100))
    else:
        submit_fname = 'submit_{}_{}_{:02d}.sh'.format(dataset, model, int(err_floor*100))
    submit_script_path = os.path.join(SCRIPT_DIR, submit_fname)
    with open(submit_script_path, 'w') as subf:
        for script_id in range(njobs):
            start = int(n_sne/njobs*script_id)
            end = int(n_sne/njobs*(script_id+1))
            if not no_mc:
                script_fname = '{}_{}_{:02d}_{}_{}_mcmc.sh'.format(dataset, model, int(err_floor*100), start, end)
            else:
                script_fname = '{}_{}_{:02d}_{}_{}.sh'.format(dataset, model, int(err_floor*100), start, end)
            script_path = os.path.join(SCRIPT_DIR, script_fname)
            with open(script_path, 'w') as f:
                f.write(TEMPLATE.format(dataset=dataset,
                                        model=model,
                                        err_int=int(err_floor*100),
                                        start=start,
                                        end=end,
                                        err_float=err_floor,
                                        no_mc=int(no_mc)))
            os.chmod(script_path, 0o755)
            subf.write('qsub {}\n'.format(os.path.abspath(script_path)))
    os.chmod(submit_script_path, 0o755)

if __name__=='__main__':
    cli()