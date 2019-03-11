import os
import sys
import click
import pickle
import sncosmo
import numpy as np
from astropy.table import Table


DATA_PATH = '/home/samdixon/jla_light_curves/'

    
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
    
    
def fit_lc_and_save(lc, model_name, save_dir):
    name = lc.meta['SN']
    model = sncosmo.Model(source=model_name)
    if type(name) is float:
        name = int(name)
    z = lc.meta['Z_HELIO']
    bounds = {}
    try:
        t0 = float(lc.meta['DayMax'].split()[0])
        bounds['t0'] = (t0-5, t0+5)
    except KeyError:
        try:
            t0 = np.mean(lc['Date'])
            bounds['t0'] = (min(lc['Date'])-20, max(lc['Date']))
        except KeyError:
            t0 = np.mean(lc['time'])
            bounds['t0'] = (min(lc['time'])-20, max(lc['time']))
    bounds['z'] = ((1-1e-4)*z, (1+1e-4)*z)
    for param_name in model.source.param_names[1:]:
        bounds[param_name] = (-50, 50)
    modelcov = model_name=='salt2'
    model.set(z=z, t0=t0)
    try:
        minuit_result, minuit_fit_model = sncosmo.fit_lc(lc, model, model.param_names, bounds=bounds,
                                                         phase_range=(-10, 40), warn=False, modelcov=modelcov)
        emcee_result, emcee_fit_model = sncosmo.mcmc_lc(sncosmo.select_data(lc, minuit_result['data_mask']),
                                                        minuit_fit_model,
                                                        model.param_names,
                                                        guess_t0=False,
                                                        bounds=bounds,
                                                        warn=False,
                                                        nwalkers=20,
                                                        modelcov=modelcov)
        save_path = os.path.join(save_dir, '{}.pkl'.format(name))
        pickle.dump(emcee_result, open(save_path, 'wb'))
    except:
        print('Fit to {} failed'.format(name))
        sys.stdout.flush()
    
    
def main():
    model_name, start, finish, err_floor = sys.argv[1:]
    start = int(start)
    finish = int(finish)
    err_floor = float(err_floor)
    save_dir = 'results/jla_{}_{:02d}'.format(model_name, int(err_floor*100))
    
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)

    lcs = []
    for f in os.listdir(DATA_PATH)[int(start):int(finish)]:
        if f[:2] == 'lc':
            lc = sncosmo.read_lc(os.path.join(DATA_PATH, f), format='salt2', expand_bands=True, read_covmat=True)
            lc = modify_error(lc, err_floor)
            name = lc.meta['SN']
            if type(name) is float:
                name = int(name)
            load_path = os.path.join(save_dir, '{}.pkl'.format(name))
            try:
                pickle.load(open(load_path, 'rb'))
                print('{}: loaded'.format(name))
                sys.stdout.flush()
            except IOError:
                print('Fitting {}'.format(name))
                sys.stdout.flush()
                fit_lc_and_save(lc, model_name, save_dir)
        else:
            continue
                
if __name__=='__main__':
    main()
