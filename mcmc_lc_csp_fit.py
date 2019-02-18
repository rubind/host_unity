import os
import sys
import pickle
import sncosmo
import numpy as np
from collections import defaultdict
from astropy.table import Table

DATA_PATH = '/home/samdixon/CSP_Photometry_DR3/'
SAVE_DIR = 'mcmc_csp_snemo7_fits'
SCRIPT_DIR = 'scripts'
if not os.path.isdir(SAVE_DIR):
    os.makedirs(SAVE_DIR)
if not os.path.isdir(SCRIPT_DIR):
    os.makedirs(SCRIPT_DIR)
    
TEMPLATE = """#!/bin/bash
#$ -N mcmc_csp_{}_{}
#$ -cwd

/home/samdixon/miniconda3/bin/python /home/samdixon/host_unity/mcmc_lc_csp_fit.py {} {}"""

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

def make_scripts(n):
    fnames = [f for f in os.listdir(DATA_PATH)]
    submit_script_path = 'submit_mcmc_csp.sh'
    with open(submit_script_path, 'w') as subf:
        for script_id in range(n):
            start = int(len(fnames)/n*script_id)
            end = int(len(fnames)/n*(script_id+1))
            print(start, end)
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
    

def fit_lc_and_save(lc):
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
    save_path = os.path.join(SAVE_DIR, '{}.pkl'.format(name))
    pickle.dump(emcee_result, open(save_path, 'wb'))


def main():
    try:
        start, finish = sys.argv[1:]
    except:
        print('Making scripts')
        make_scripts(16)
        print('Must supply start and end indices for fit')
        return
    lcs = []
    for f in os.listdir(DATA_PATH)[int(start):int(finish)]:
        if '_snpy.txt' in f:
            lc = parse_csp_lc(os.path.join(DATA_PATH, f))
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
        else:
            print(f)
                
if __name__=='__main__':
    main()
