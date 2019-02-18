import os
import sys
import pickle
import sncosmo
import requests
import numpy as np
import pandas as pd
from astropy.io import ascii
from astropy.table import Table

DATA = pd.read_csv('/home/samdixon/foundation_photometry.txt', delimiter=', ')
SAVE_DIR = 'mcmc_jones_snemo7_fits'
SCRIPT_DIR = 'scripts'

if not os.path.isdir(SAVE_DIR):
    os.makedirs(SAVE_DIR)
if not os.path.isdir(SCRIPT_DIR):
    os.makedirs(SCRIPT_DIR)
    
TEMPLATE = """#!/bin/bash
#$ -N mcmc_ps_{}_{}
#$ -cwd

/home/samdixon/miniconda3/bin/python /home/samdixon/host_unity/mcmc_lc_foundation_fit.py {} {}"""

PS_FILTS = ascii.read('/home/samdixon/PSfilters.txt')

def read_and_register(name):
    name = name.lower()
    wave = PS_FILTS['Wave']*10
    trans = PS_FILTS[name]
    band = sncosmo.Bandpass(wave=wave, trans=trans, name=name)
    sncosmo.register(band, force=True)

    
def make_scripts(n):
    n_sne = len(DATA.SN.unique())
    submit_script_path = 'submit_mcmc_ps.sh'
    with open(submit_script_path, 'w') as subf:
        for script_id in range(n):
            start = int(n_sne/n*script_id)
            end = int(n_sne/n*(script_id+1))
            print(start, end)
            script_path = os.path.join(SCRIPT_DIR, 'mcmc_ps_{}_{}.sh'.format(start, end))
            with open(script_path, 'w') as f:
                f.write(TEMPLATE.format(start, end, start, end))
            os.chmod(script_path, 0o755)
            subf.write('qsub {}\n'.format(os.path.abspath(script_path)))
    os.chmod(submit_script_path, 0o755)


def get_foundation_lc(sn_name):
    sn_data = data[data['SN'] == sn_name]
    meta_data = foundation_params.loc[sn_name]
    meta = {'name': sn_name,
            'z': float(meta_data['z_helio'].split()[0]),
            't0': float(meta_data['Peak_MJD'].split()[0])}
    lc = {'time': sn_data['MJD'],
          'band': sn_data['Filter'],
          'flux': sn_data['Flux'],
          'flux_err': sn_data['Flux_Uncertainty'],
          'zp': [27.5 for x in range(len(sn_data))],
          'zpsys': ['ab' for x in range(len(sn_data))]}
    return Table(lc, meta=meta)
    

def fit_lc_and_save(lc):
    name = lc.meta['name']
    model = sncosmo.Model(source='snemo7')
    if type(name) is float:
        name = int(name)
    z = lc.meta['z']
    bounds = {}
    t0 = np.mean(lc['mjd'])
    bounds['t0'] = (min(lc['mjd'])-20, max(lc['mjd']))
    for param_name in model.source.param_names[1:]:
        bounds[param_name] = (-50, 50)
    model.set(z=z, t0=t0)
    try:
        minuit_result, minuit_fit_model = sncosmo.fit_lc(lc, model, model.param_names[1:], bounds=bounds,
                                                         phase_range=(-10, 40), warn=False)
        emcee_result, emcee_fit_model = sncosmo.mcmc_lc(sncosmo.select_data(lc, minuit_result['data_mask']),
                                                        minuit_fit_model,
                                                        model.param_names[1:],
                                                        guess_t0=False,
                                                        bounds=bounds,
                                                        warn=False,
                                                        nwalkers=20)
        save_path = os.path.join(SAVE_DIR, '{}.pkl'.format(name))
        pickle.dump(emcee_result, open(save_path, 'wb'))
    except:
        print('Error fitting {}'.format(name))


def main():
    try:
        start, finish = sys.argv[1:]
    except:
        print('Making scripts')
        make_scripts(16)
        print('Must supply start and end indices for fit')
        return
    
    for filt in DATA['Filter'].unique():
        read_and_register(filt)

    lcs = []
    for sn in DATA.SN.unique()[int(start):int(finish)]:
        lc = get_foundation_lc(sn)
        name = lc.meta['name']
        load_path = os.path.join(SAVE_DIR, '{}.pkl'.format(name))
        try:
            pickle.load(open(load_path, 'rb'))
            print('{}: loaded'.format(name))
            sys.stdout.flush()
        except IOError:
            print('Fitting {}'.format(name))
            sys.stdout.flush()
            fit_lc_and_save(lc)

                
if __name__=='__main__':
    main()
