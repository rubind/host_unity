import os
import sys
import pickle
import sncosmo
import numpy as np

DATA_PATH = '/home/samdixon/jla_light_curves/'
SAVE_DIR = 'mcmc_jla_snemo7_fits'
SCRIPT_DIR = 'scripts'
if not os.path.isdir(SAVE_DIR):
    os.makedirs(SAVE_DIR)
if not os.path.isdir(SCRIPT_DIR):
    os.makedirs(SCRIPT_DIR)
    
TEMPLATE = """#!/bin/bash
#$ -N mcmc_jla_{}_{}
#$ -cwd

/home/samdixon/miniconda3/bin/python /home/samdixon/host_unity/mcmc_lc_fit.py {} {}"""
    
def make_scripts(n):
    fnames = [f for f in os.listdir(DATA_PATH)]
    submit_script_path = 'submit_mcmc_jla.sh'
    with open(submit_script_path, 'w') as subf:
        for script_id in range(n):
            start = int(len(fnames)/n*script_id)
            end = int(len(fnames)/n*(script_id+1))
            print(start, end)
            script_path = os.path.join(SCRIPT_DIR, 'mcmc_jla_{}_{}.sh'.format(start, end))
            with open(script_path, 'w') as f:
                f.write(TEMPLATE.format(start, end, start, end))
            os.chmod(script_path, 0o755)
            subf.write('qsub {}\n'.format(os.path.abspath(script_path)))
    os.chmod(submit_script_path, 0o755)

def fit_lc_and_save(lc):
    name = lc.meta['SN']
    model = sncosmo.Model(source='snemo7')
    if type(name) is float:
        name = int(name)
    z = lc.meta['Z_HELIO']
    bounds = {}
    try:
        t0 = float(lc.meta['DayMax'].split()[0])
        bounds['t0'] = (t0-5, t0+5)
    except KeyError:
        t0 = np.mean(lc['Date'])
        bounds['t0'] = (min(lc['Date'])-20, max(lc['Date']))
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
        if f[:2] == 'lc':
            lc = sncosmo.read_lc(os.path.join(DATA_PATH, f), format='salt2', expand_bands=True, read_covmat=True)
            name = lc.meta['SN']
            if type(name) is float:
                name = int(name)
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
