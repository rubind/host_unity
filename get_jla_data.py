"""Get output of Rebekah's fits into a format for UNITY"""

import os
import copy
import pickle
import sncosmo
import numpy as np
import pandas as pd
from scipy.linalg import block_diag


JLA_PATH = '~/jla_light_curves'
FIT_DIR = './pub_snemo7_jla_fits/'
MODEL = sncosmo.Model(source='snemo7')
OUT_PATH = './RH_JLA_pub_snemo7.pkl'


def calc_mbstar(model, coefs, z):
    """Calculates $m_B^*$ for a supernova model with the given coefficients
    
    Args:
        model (sncosmo.Model): sncosmo Model object to use in calculation
        coefs (np.array): array of model coefficients
        z (float): redshift of object
        
    Returns:
        mbstart (float): AB magnitude in the Bessell B-band for a supernova with
        the given model coefficients
    """
    model = copy.copy(model)
    model.set(**dict(zip(model.source.param_names, coefs)))
    model.set(z=0)
    model.set(t0=0)
    return model.bandmag(band='bessellv', time=0, magsys='ab')


# Read JLA data from Betoule et al. to get host galaxy masses
meta = pd.read_csv(os.path.join(JLA_PATH, 'jla_lcparams.txt'),
                   delim_whitespace=True)

# Read pickle files from Rebekah
fits = {}
for fname in os.listdir(FIT_DIR):
    path = os.path.join(FIT_DIR, fname)
    if len(fname[3:].split('.')) == 3:
        name = 'SDSS'+fname[3:].split('.')[0]
    else:
        name = fname[3:].split('.')[0]
    fits[name] = pickle.load(open(path, 'rb'))

fit_df = pd.DataFrame.from_dict(fits).T
for i, param_name in enumerate(fit_df['vparam_names'][0]):
    fit_df[param_name] = [x[i+1] for x in fit_df['parameters'].values]
    fit_df['d'+param_name] = [x[param_name] for x in fit_df['errors'].values]
    
# Combine the data into a single table
data = fit_df.merge(meta,
                    right_on='name',
                    left_index=True,
                    suffixes=['_snemo7', '_jla'])

# Convert c0 to mb
data['mbstar'] = [calc_mbstar(MODEL, x['parameters'][2:], x['zhel']) for _, x in data.iterrows()]
data['dmbstar'] = [(2.5 * np.sqrt(x['covariance'][1, 1])/(x['parameters'][2] * np.log(10)))**2 for _, x in data.iterrows()]

# Convert observed parameters into an array
obs_data = np.hstack([np.array([[x] for x in data.mbstar.values]),
                      np.array([x[3:] for x in data.parameters.values]),
                      np.array([[x] for x in data['3rdvar'].values])])

# Calculate the combined covariance matrix
obs_cov = np.array([block_diag(x**2, y[2:, 2:], z**2) for x, y, z in zip(data.dmbstar.values,
                                                                         data.covariance.values,
                                                                         data['d3rdvar'].values)])
# Format for Stan
stan_data = {'n_sne': len(data),
             'names': data.name.values,
             'n_props': 9,
             'n_non_gaus_props': 0,
             'n_sn_set': len(data.set.unique()),
             'sn_set_inds': (data.set.values.astype(int)-1).astype(int),
             'z_helio': data.zhel.values.astype(float),
             'z_CMB': data.zcmb.values.astype(float),
             'obs_mBx1c': obs_data,
             'obs_mBx1c_cov': obs_cov,
             'n_age_mix': 0,
             'age_gaus_mean': np.array([]).reshape(0, len(data), 0),
             'age_gaus_std': np.array([]).reshape(0, len(data), 0),
             'age_gaus_A': np.array([]).reshape(0, len(data), 0),
             'do_fullDint': 0,
             'outl_frac_prior_lnmean': -4.6,
             'outl_frac_prior_lnwidth': 1.,
             'lognormal_intr_prior': 0,
             'allow_alpha_S_N': 0}

# Dump to pickle file
pickle.dump(stan_data, open(OUT_PATH, 'wb'))