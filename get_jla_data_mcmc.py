"""Get output of Rebekah's fits into a format for UNITY"""

import os
import copy
import pickle
import sncosmo
import numpy as np
import pandas as pd
from scipy.linalg import block_diag


JLA_PATH = '~/jla_light_curves'
FIT_DIR = './mcmc_jla_snemo7_fits/'
MODEL = sncosmo.Model(source='snemo7')
OUT_PATH = './JLA_pub_snemo7_mcmc.pkl'


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

# Read pickle files from fits
fits = {}
for fname in os.listdir(FIT_DIR):
    path = os.path.join(FIT_DIR, fname)
    try:
        name = 'SDSS{}'.format(int(fname.split('.')[0]))
    except:
        name = fname.split('.')[0]
    try:
        fits[name] = pickle.load(open(path, 'rb'))
        print(name, path)
    except IsADirectoryError:
        continue

fit_df = pd.DataFrame.from_dict(fits).T
for i, param_name in enumerate(fit_df['vparam_names'][0]):
#     fit_df[param_name] = [x[i+1] for x in fit_df['parameters'].values]
    fit_df[param_name] = [x[i] for x in fit_df['parameters'].values]
    fit_df['d'+param_name] = [x[param_name] for x in fit_df['errors'].values]


# Combine the data into a single table
data = fit_df.merge(meta,
                    right_on='name',
                    left_index=True,
                    suffixes=['_snemo7', '_jla'])

# Convert c0 to mb
data['mbstar'] = [calc_mbstar(MODEL, x['parameters'][2:], x['zhel']) for _, x in data.iterrows()]

# Convert observed parameters into an array
obs_data = np.hstack([np.array([[x] for x in data.mbstar.values]),
                      np.array([x[3:] for x in data.parameters.values]),
                      np.array([[x] for x in data['3rdvar'].values])])

# Calculate the combined covariance matrix
obs_cov = []
for _, sn in data.iterrows():
    cov = np.zeros((9, 9))
    cov[0, 0] = sn.covariance[1, 1] * (-2.5/(np.log(10)*sn.parameters[2]))**2 # diagonal, m_b
    cov[1:-1, 0] = sn.covariance[2:, 1] * (-2.5/(np.log(10)*sn.parameters[2])) # off-diagonal, m_b x c_i
    cov[0, 1:-1] = sn.covariance[1, 2:] * (-2.5/(np.log(10)*sn.parameters[2])) # off-diagonal, c_i x m_b
    cov[1:-1, 1:-1] = sn.covariance[2:, 2:] # c_i x c_j
    cov[-1, -1] = sn['d3rdvar']**2
    obs_cov.append(cov)
obs_cov = np.array(obs_cov)


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