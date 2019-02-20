import os
import sys
import pickle
import sncosmo
import numpy as np
from collections import defaultdict
from astropy.table import Table

DATA_PATH = '/home/samdixon/CSP_Photometry_DR3/'
SCRIPT_DIR = 'scripts'
if not os.path.isdir(SCRIPT_DIR):
    os.makedirs(SCRIPT_DIR)
    
TEMPLATE = """#!/bin/bash
#$ -N mcmc_csp_{}_{}
#$ -cwd

/home/samdixon/miniconda3/bin/python /home/samdixon/host_unity/mcmc_lc_csp_fit.py {} {}"""

TEMPLATE_ERR = """#!/bin/bash
#$ -N mcmc_csp_{:02d}_{}_{}
#$ -cwd

/home/samdixon/miniconda3/bin/python /home/samdixon/host_unity/mcmc_lc_csp_fit.py {} {} {}"""

CSP_FILT_MAP = {'u': 'cspu',
                'g': 'cspg',
                'r': 'cspr',
                'i': 'cspi',
                'B': 'cspb',
                'V0': 'cspv3014',
                'V1': 'cspv3009',
                'V': 'cspv9844',
                'Y': 'cspys',
                'H': 'csphs',
                'J': 'cspjs',
                'Jrc2': 'cspjs',
                'Ydw': 'cspyd',
                'Jdw': 'cspjd',
                'Hdw': 'csphd'}
MAGSYS = sncosmo.get_magsystem('csp')

def make_scripts(n, err_floor=None):
    fnames = [f for f in os.listdir(DATA_PATH)]
    if err_floor is not None:
        submit_script_path = 'submit_mcmc_csp_error_floor_{:02d}.sh'.format(int(err_floor*100))
    else:
        submit_script_path = 'submit_mcmc_csp.sh'
    with open(submit_script_path, 'w') as subf:
        for script_id in range(n):
            start = int(len(fnames)/n*script_id)
            end = int(len(fnames)/n*(script_id+1))
            print(start, end)
            if err_floor is not None:
                script_path = os.path.join(SCRIPT_DIR, 'mcmc_csp_err_floor_{:02d}_{}_{}.sh'.format(int(err_floor*100), start, end))
                with open(script_path, 'w') as f:
                    f.write(TEMPLATE_ERR.format(int(err_floor*100), start, end, start, end, err_floor))
            else:
                script_path = os.path.join(SCRIPT_DIR, 'mcmc_csp_{}_{}.sh'.format(start, end))
                with open(script_path, 'w') as f:
                    f.write(TEMPLATE.format(start, end, start, end))
            os.chmod(script_path, 0o755)
            subf.write('qsub {}\n'.format(os.path.abspath(script_path)))
    os.chmod(submit_script_path, 0o755)


def parse_csp_lc(path):
    meta = {}
    lc = defaultdict(list)
    current_filt = None
    with open(path) as f:
        for l in f.readlines():
            if l.split()[0][:2]=='SN':
                name, z, ra, dec = l.split()
                meta['name'] = name.strip()
                meta['z'] = float(z.strip())
                continue
            if l.split()[0] == 'filter':
                current_filt = CSP_FILT_MAP[l.split()[-1]]
            else:
                time, mag, mag_err = [float(x.strip()) for x in l.split()]
                flux = MAGSYS.band_mag_to_flux(mag, current_filt)
                flux_err = mag_err*flux*np.log(10)/2.5
                lc['time'].append(53000 + time)
                lc['flux'].append(flux)
                lc['flux_err'].append(flux_err)
                lc['zp'].append(2.5*np.log10(MAGSYS.zpbandflux(current_filt)))
                lc['zpsys'].append('csp')
                lc['band'].append(current_filt)
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
    if type(name) is float:
        name = int(name)
    z = lc.meta['z']
    bounds = {}
    t0 = np.mean(lc['time'])
    bounds['t0'] = (min(lc['time'])-20, max(lc['time']))
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
        save_dir = 'mcmc_csp_snemo7_fits_error_floor_{:02d}'.format(int(err_floor*100))
    else:
        save_dir = 'mcmc_csp_snemo7_fits'
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)

    lcs = []
    for f in os.listdir(DATA_PATH)[int(start):int(finish)]:
        if '_snpy.txt' in f:
            lc = parse_csp_lc(os.path.join(DATA_PATH, f))
            lc = modify_error(lc, 0.03)
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
        else:
            print(f)
                
if __name__=='__main__':
    main()
