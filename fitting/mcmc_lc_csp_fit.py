import os
import sys
import pickle
import sncosmo
import numpy as np
from collections import defaultdict
from astropy.table import Table
from sfdmap import SFDMap

DATA_PATH = '/home/samdixon/CSP_Photometry_DR3/'

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

MWDUSTMAP = SFDMap('/home/samdixon/sfddata/')

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
                meta['mwebv'] = MWDUSTMAP.ebv(float(ra), float(dec))
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


def fit_lc_and_save(lc, model_name, save_dir):
    name = lc.meta['name']
    model = sncosmo.Model(source=model_name,
                          effects=[sncosmo.CCM89Dust()],
                          effect_names=['mw'],
                          effect_frames=['obs'])
    if type(name) is float:
        name = int(name)
    z = lc.meta['z']
    mwebv = lc.meta['mwebv']
    bounds = {}
    t0 = np.mean(lc['time'])
    bounds['t0'] = (min(lc['time'])-20, max(lc['time']))
    bounds['z'] = ((1-1e-4)*z, (1+1e-4)*z)
    for param_name in model.source.param_names[1:]:
        bounds[param_name] = (-50, 50)
    modelcov = model_name == 'salt2'
    model.set(z=z, t0=t0, mwebv=mwebv)
    phase_range = (-15, 45) if model_name=='salt2' else (-10, 40)
    wave_range = (3000, 7000) if model_name=='salt2' else None
    try:
        minuit_result, minuit_fit_model = sncosmo.fit_lc(lc, model, model.param_names[:-2], bounds=bounds,
                                                         phase_range=phase_range, wave_range=wave_range,
                                                         warn=False, modelcov=modelcov)
#         emcee_result, emcee_fit_model = sncosmo.mcmc_lc(sncosmo.select_data(lc, minuit_result['data_mask']),
#                                                         minuit_fit_model,
#                                                         model.param_names,
#                                                         guess_t0=False,
#                                                         bounds=bounds,
#                                                         warn=False,
#                                                         nwalkers=20,
#                                                         modelcov=modelcov)
        save_path = os.path.join(save_dir, '{}.pkl'.format(name))
        pickle.dump(minuit_result, open(save_path, 'wb'))
    except:
        print('Fit to {} failed'.format(name))
        sys.stdout.flush()


def main():
    model_name, start, finish, err_floor = sys.argv[1:]
    start = int(start)
    finish = int(finish)
    err_floor = float(err_floor)
    save_dir = '/home/samdixon/host_unity/fitting/results_mw_reddening/csp_{}_{:02d}'.format(model_name, int(err_floor*100))
    
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
                fit_lc_and_save(lc, model_name, save_dir)
        else:
            continue
                
if __name__=='__main__':
    main()
