import os
import sys
import pickle
import sncosmo
import requests
import numpy as np
import pandas as pd
from astropy.io import ascii
from astropy.table import Table

DATA = pd.read_csv('/home/samdixon/foundation_photometry.txt', delimiter=', ', engine='python')
META = ascii.read('/home/samdixon/foundation_lc_params.tex', format='latex').to_pandas()
META = META.set_index('SN')

SCRIPT_DIR = 'scripts'
if not os.path.isdir(SCRIPT_DIR):
    os.makedirs(SCRIPT_DIR)
    
TEMPLATE = """#!/bin/bash
#$ -N mcmc_ps_{}_{}
#$ -cwd

/home/samdixon/miniconda3/bin/python /home/samdixon/host_unity/mcmc_lc_foundation_fit.py {} {}"""

TEMPLATE_ERR = """#!/bin/bash
#$ -N mcmc_ps_{:02d}_{}_{}
#$ -cwd

/home/samdixon/miniconda3/bin/python /home/samdixon/host_unity/mcmc_lc_foundation_fit.py {} {} {}"""

PS_FILTS = ascii.read('/home/samdixon/PSfilters.txt')

def read_and_register(name):
    name = name.lower()
    wave = PS_FILTS['Wave']*10
    trans = PS_FILTS[name]
    band = sncosmo.Bandpass(wave=wave, trans=trans, name=name)
    sncosmo.register(band, force=True)

    
def make_scripts(n, err_floor=None):
    n_sne = len(DATA.SN.unique())
    if err_floor is not None:
        submit_script_path = 'submit_mcmc_ps_error_floor_{:02d}.sh'.format(int(err_floor*100))
    else:
        submit_script_path = 'submit_mcmc_ps.sh'
    with open(submit_script_path, 'w') as subf:
        for script_id in range(n):
            start = int(n_sne/n*script_id)
            end = int(n_sne/n*(script_id+1))
            print(start, end)
            if err_floor is not None:
                script_path = os.path.join(SCRIPT_DIR, 'mcmc_ps_error_floor_{:02d}_{}_{}.sh').format(int(err_floor*100), start, end)
                with open(script_path, 'w') as f:
                    f.write(TEMPLATE_ERR.format(int(err_floor*100), start, end, start, end, err_floor))
            else:
                script_path = os.path.join(SCRIPT_DIR, 'mcmc_ps_{}_{}.sh'.format(start, end))
                with open(script_path, 'w') as f:
                    f.write(TEMPLATE.format(start, end, start, end))
            os.chmod(script_path, 0o755)
            subf.write('qsub {}\n'.format(os.path.abspath(script_path)))
    os.chmod(submit_script_path, 0o755)


def get_foundation_lc(sn_name):
    print(sn_name)
    sn_data = DATA[DATA['SN'] == sn_name]
    meta_data = META.loc[sn_name]
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


def modify_error(lc, error_floor=0.):
    """Add an error floor of `error_floor` times the maximum flux of the band
    to each observation
    """
    data = sncosmo.photdata.photometric_data(lc).normalized(zp=25., zpsys='ab')
    new_lc = {'time': data.time,
              'band': data.band,
              'flux': data.flux,
              'fluxerr': data.fluxerr,
              'zp': data.zp,
              'zpsys': data.zpsys}
    for band in set(data.band):
        band_cut = data.band==band
        max_flux_in_band = np.max(data.flux[band_cut])
        new_lc['fluxerr'][band_cut] = np.sqrt((error_floor*max_flux_in_band)**2+data.fluxerr[band_cut]**2)
    new_lc = Table(new_lc, meta=lc.meta)   
    return new_lc


def fit_lc_and_save(lc, save_dir):
    name = lc.meta['name']
    model = sncosmo.Model(source='snemo7')
    z = lc.meta['z']
    bounds = {}
    t0 = np.mean(lc['time'])
    bounds['t0'] = (min(lc['time'])-20, max(lc['time']))
    try:
        for param_name in model.source.param_names[1:]:
            bounds[param_name] = (-50, 50)
        model.set(z=z, t0=t0)
        minuit_result, minuit_fit_model = sncosmo.fit_lc(lc, model, model.param_names[1:], bounds=bounds,
                                                         phase_range=(-10, 40), warn=False)
        emcee_result, emcee_fit_model = sncosmo.mcmc_lc(sncosmo.select_data(lc, minuit_result['data_mask']),
                                                        minuit_fit_model,
                                                        model.param_names[1:],
                                                        guess_t0=False,
                                                        bounds=bounds,
                                                        warn=False,
                                                        nwalkers=20)
        save_path = os.path.join(save_dir, '{}.pkl'.format(name))
        pickle.dump(emcee_result, open(save_path, 'wb'))
    except:
        print('Error fitting {}'.format(name))


def main():
    err_floor = None
    if len(sys.argv[1:]) == 0:
        make_scripts(16)
        return
    elif len(sys.argv[1:]) == 1:
        err_floor = float(sys.argv[1])
        make_scripts(16, err_floor)
        return
    elif len(sys.argv[1:]) == 2:
        start, finish = sys.argv[1:]
    elif len(sys.argv[1:]) == 3:
        start, finish, err_floor = sys.argv[1:]
        err_floor = float(err_floor)
    else:
        return
    
    if err_floor is not None:
        save_dir = 'mcmc_ps_snemo7_fits_error_floor_{:02d}'.format(int(err_floor*100))
    else:
        save_dir = 'mcmc_ps_snemo7_fits'
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    
    for filt in DATA['Filter'].unique():
        read_and_register(filt)

    lcs = []
    for sn in DATA.SN.unique()[int(start):int(finish)]:
        lc = get_foundation_lc(sn)
        if err_floor is not None:
            lc = modify_error(lc, err_floor)
        name = lc.meta['name']
        load_path = os.path.join(save_dir, '{}.pkl'.format(name))
        try:
            pickle.load(open(load_path, 'rb'))
            print('{}: loaded'.format(name))
            sys.stdout.flush()
        except IOError:
            print('Fitting {}'.format(name))
            sys.stdout.flush()
            fit_lc_and_save(lc, save_dir)

                
if __name__=='__main__':
    main()
