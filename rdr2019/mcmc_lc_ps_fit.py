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

HOSTDATA = pd.read_csv('/home/samdixon/host_unity/fitting/gupta_host.txt', delim_whitespace=True)
HOSTDATA = HOSTDATA.set_index('name')
HOSTDATA.index = [name.replace('_', '-') if name[:6]=='ASASSN' else name for name in HOSTDATA.index]

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


def get_foundation_lc(sn_name):
    sn_data = DATA[DATA['SN'] == sn_name]
    meta_data = META.loc[sn_name]
    try:
        host = HOSTDATA[HOSTDATA.index.str.contains(sn_name)]
        mwebv = host['MW_EBV'][0]
    except IndexError:
        print('no MW EBV value found. Assuming 0.')
        sys.stdout.flush()
        mwebv = 0
    meta = {'name': sn_name,
            'z': float(meta_data['z_helio'].split()[0]),
            't0': float(meta_data['Peak_MJD'].split()[0]),
            'mwebv': mwebv}
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


def fit_lc_and_save(lc, model_name, save_dir, no_mc):
    name = lc.meta['name']
    model = sncosmo.Model(source=model_name,
                          effects=[sncosmo.CCM89Dust()],
                          effect_names=['mw'],
                          effect_frames=['obs'])
    z = lc.meta['z']
    mwebv = lc.meta['mwebv']
    bounds = {}
    t0 = np.mean(lc['time'])
    bounds['t0'] = (min(lc['time'])-20, max(lc['time']))
    bounds['z'] = ((1-1e-5)*z, (1+1e-5)*z)
    for param_name in model.source.param_names[1:]:
        bounds[param_name] = (-50, 50)
    model.set(z=z, t0=t0, mwebv=mwebv)
    modelcov = model_name == 'salt2'
    phase_range = (-15, 45) if model_name=='salt2' else (-10, 40)
    wave_range = (3000, 7000) if model_name=='salt2' else None
    save_path = os.path.join(save_dir, '{}.pkl'.format(name))
    try:
        minuit_result, minuit_fit_model = sncosmo.fit_lc(lc, model, model.param_names[:-2], bounds=bounds,
                                                         phase_range=phase_range, wave_range=wave_range,
                                                         warn=False, modelcov=modelcov)
        if not no_mc:
            emcee_result, emcee_fit_model = sncosmo.mcmc_lc(sncosmo.select_data(lc, minuit_result['data_mask']),
                                                            minuit_fit_model,
                                                            model.param_names[:-2],
                                                            guess_t0=False,
                                                            bounds=bounds,
                                                            warn=False,
                                                            nwalkers=20,
                                                            modelcov=modelcov)
            pickle.dump(emcee_result, open(save_path, 'wb'))
        else:
            pickle.dump(minuit_result, open(save_path, 'wb'))
    except:
        print('Fit to {} failed'.format(name))
        sys.stdout.flush()


def main():
    model_name, start, finish, err_floor, no_mc = sys.argv[1:]
    start = int(start)
    finish = int(finish)
    err_floor = float(err_floor)
    no_mc = bool(int(no_mc))
    if no_mc:
        save_dir = '/home/samdixon/host_unity/fitting/results_mw_reddening/ps_{}_{:02d}'.format(model_name, int(err_floor*100))
    else:
        save_dir = '/home/samdixon/host_unity/fitting/results_mw_reddening_mcmc/ps_{}_{:02d}'.format(model_name, int(err_floor*100))
    
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    
    for filt in DATA['Filter'].unique():
        read_and_register(filt)

    lcs = []
    for sn in DATA.SN.unique()[int(start):int(finish)]:
        try:
            lc = get_foundation_lc(sn)
        except:
            print('Error reading LC {}'.format(sn))
            sys.stdout.flush()
            continue
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
            fit_lc_and_save(lc, model_name, save_dir, no_mc)

                
if __name__=='__main__':
    main()
