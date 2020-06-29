"""cleandata.py --- Makes input datasets from Cambpell/UNITY analysis

Takes Table 7 and SN LC data from Rose, Garnavich, Berg (2019) and:
* sets mean to zero for log-stellar mass and ages.
* save out four UNITY input files
    * mass, local age, global age
    * mass plus local age
    * mass plus global age
    * mass alone
"""

import pickle

import pandas as pd
import numpy as np
from astropy.table import Table

__email__ = "brose@stsci.edu"
__author__ = f"Benjamin Rose <{__email__}>"
__date__ = "2019-09-09"
__python__ = "3.7"    # should work on ^3.5, but currently not tested

INPUT_FILE = 'results-summary.csv'
SN_DATA_FILE = 'SDSS_Photometric_SNe_Ia.fits'


def build_UNITY_dict(n_sne, n_props, z_helio, obs_mBx1c, obs_mBx1c_cov):
    # construct full UNITY input dictionary
    # true for all samples.
    age_gaus_mean = np.zeros((0, n_sne, 0))
    age_gaus_std = np.zeros((0, n_sne, 0))
    age_gaus_A = np.zeros((0, n_sne, 0))
    return dict(# general information
                n_sne=n_sne, n_props=n_props, n_non_gaus_props=0, n_sn_set=1,
                sn_set_inds=[0]*n_sne,
                     # redshifts
                z_helio=z_helio, z_CMB=z_helio,
                     # Gaussian defined properties
                obs_mBx1c=obs_mBx1c, obs_mBx1c_cov=obs_mBx1c_cov,
                     # Non-Gaussian properties, aka complicated age
                n_age_mix=0, age_gaus_mean=age_gaus_mean,
                age_gaus_std=age_gaus_std, age_gaus_A=age_gaus_A,
                     # Other stuff that does not really need to change
                do_fullDint=0, outl_frac_prior_lnmean=-4.6, outl_frac_prior_lnwidth=1,
                lognormal_intr_prior=0, allow_alpha_S_N=0)


def save_UNITY(data, data_name):
    with open(f'{data_name}.pkl', 'wb') as f:
        pickle.dump(data, f)


# import table 7
# Read in, change column names, then set index - there has to be a way to chain these.
rgb2019_data = pd.read_csv(INPUT_FILE)
rgb2019_data.columns = ['snid', 'age_l', 'age_l_err', 'age_g', 'age_g_err', 'mass', 'pc1']
rgb2019_data.set_index("snid", inplace=True)
N_SNE = len(rgb2019_data)
rgb2019_data['mass_err'] = 0.3*np.ones(N_SNE)


means = []
# set means to zero
for param in ['mass', 'age_l', 'age_g']:
    means.append(rgb2019_data[param].mean())
    rgb2019_data[param] = rgb2019_data[param] - rgb2019_data[param].mean()


# get SN LC data
lc_data = Table.read(SN_DATA_FILE)
lc_data = lc_data.to_pandas().set_index('CID')
lc_data = lc_data.loc[rgb2019_data.index]   # get just the SN in Table 7
lc_data = lc_data[['Z', 'Z_ERR', 'X0', 'X0_ERR', 'X1', 'X1_ERR', 'COLOR',
                   'COLOR_ERR', 'C01', 'C00', 'C11', 'C22', 'C02', 'C12',
                   'MU_MB', 'MU_ERR']]
assert len(lc_data) == N_SNE


m_b = -2.5*np.log10(lc_data['X0'].values) + 10.63     # 10.63 is from some random plot from David of mB-2.5log10(x0) vs color.
obs_mBx1c = [[m_b[i], lc_data['X1'].iloc[i], lc_data['COLOR'].iloc[i], 
             rgb2019_data['mass'].iloc[i], rgb2019_data['age_l'].iloc[i],
             rgb2019_data['age_g'].iloc[i]] for i in range(N_SNE)]
obs_mBx1c = np.array(obs_mBx1c)  # need array slicing

cov = np.zeros((N_SNE, 6, 6))
cov[:, 0, 0] = (2.5/np.log(10))**2*(lc_data['C00'].values/lc_data['X0']**2)
cov[:, 0, 1] = (-2.5/np.log(10))*(lc_data['C01'].values/lc_data['X0'])
cov[:, 0, 2] = (-2.5/np.log(10))*(lc_data['C02'].values/lc_data['X0'])
cov[:, 1, 0] = (-2.5/np.log(10))*(lc_data['C01'].values/lc_data['X0'])
cov[:, 1, 1] = lc_data['C11'].values
cov[:, 1, 2] = lc_data['C12'].values
cov[:, 2, 0] = (-2.5/np.log(10))*(lc_data['C02'].values/lc_data['X0'])
cov[:, 2, 1] = lc_data['C12'].values
cov[:, 2, 2] = lc_data['C22'].values
cov[:, 3, 3] = rgb2019_data['mass_err']**2
cov[:, 4, 4] = rgb2019_data['age_l_err']**2
cov[:, 5, 5] = rgb2019_data['age_g_err']**2

# index 3 is mass, 4 is local age, 5 is global age
# np.delete(np.delete(a, 4, axis=2), 4, axis=1) removes only row and column number 4 of a 3D object
mass_local_global = build_UNITY_dict(N_SNE, 6, lc_data["Z"], obs_mBx1c, cov)
mass_local = build_UNITY_dict(N_SNE, 5, lc_data["Z"], obs_mBx1c[:, :5], cov[:, :5, :5])
mass_global = build_UNITY_dict(N_SNE, 5, lc_data["Z"], np.delete(obs_mBx1c, 4, axis=1), 
                               np.delete(np.delete(cov, 4, axis=2), 4, axis=1))
local_global = build_UNITY_dict(N_SNE, 5, lc_data["Z"], np.delete(obs_mBx1c, 3, axis=1), 
                                np.delete(np.delete(cov, 3, axis=2), 3, axis=1))
mass = build_UNITY_dict(N_SNE, 4, lc_data["Z"], obs_mBx1c[:, :4], cov[:, :4, :4])
local = build_UNITY_dict(N_SNE, 4, lc_data["Z"], np.delete(obs_mBx1c, [3, 5], axis=1), 
                         np.delete(np.delete(cov, [3, 5], axis=2), [3, 5], axis=1))
global_ = build_UNITY_dict(N_SNE, 4, lc_data["Z"], np.delete(obs_mBx1c, [3, 4], axis=1), 
                           np.delete(np.delete(cov, [3, 4], axis=2), [3, 4], axis=1))
salt = build_UNITY_dict(N_SNE, 3, lc_data["Z"], obs_mBx1c[:, :3], cov[:, :3, :3])


# Make datasets with mass and local age, but cut between low and high mass.
MASS_CUT = 10
is_low_mass = obs_mBx1c[:,3] < MASS_CUT - means[0]
low_mass_with_age_dataset = build_UNITY_dict(np.array(is_low_mass).sum(), 4,
                                    lc_data["Z"][is_low_mass],
                                    np.delete(obs_mBx1c, [3, 4], axis=1)[is_low_mass],
                                    np.delete(np.delete(cov, [3, 4], axis=2), [3, 4], axis=1)[is_low_mass]
                                    )
high_mass_with_age_dataset = build_UNITY_dict(np.array(~is_low_mass).sum(), 4,
                                     lc_data["Z"][~is_low_mass],
                                     np.delete(obs_mBx1c, [3, 4], axis=1)[~is_low_mass],
                                     np.delete(np.delete(cov, [3, 4], axis=2), [3, 4], axis=1)[~is_low_mass]
                                     )
low_mass_dataset = build_UNITY_dict(np.array(is_low_mass).sum(), 3, lc_data["Z"][is_low_mass],
                                    obs_mBx1c[:, :3][is_low_mass], cov[:, :3, :3][is_low_mass]
                                    )
high_mass_dataset = build_UNITY_dict(np.array(~is_low_mass).sum(), 3, lc_data["Z"][~is_low_mass],
                                     obs_mBx1c[:, :3][~is_low_mass], cov[:, :3, :3][~is_low_mass]
                                     )

obs_mBx1c[:, 3] += 0.1
low_mass_shifted_color = build_UNITY_dict(np.array(is_low_mass).sum(), 3, lc_data["Z"][is_low_mass],
                                    obs_mBx1c[:, :3][is_low_mass], cov[:, :3, :3][is_low_mass]
                                    )
high_mass_shifted_color = build_UNITY_dict(np.array(~is_low_mass).sum(), 3, lc_data["Z"][~is_low_mass],
                                     obs_mBx1c[:, :3][~is_low_mass], cov[:, :3, :3][~is_low_mass]
                                     )

# save four UNITY input files
datas = [mass_local_global, mass_local, mass_global, local_global, mass, local,
         global_, salt, low_mass_with_age_dataset, high_mass_with_age_dataset,
         low_mass_dataset, high_mass_dataset, low_mass_shifted_color, high_mass_shifted_color]
data_names = ['mass_local_global', 'mass_local', 'mass_global', 'local_global',
              'mass', 'local', 'global', 'salt', 'low_mass_age_only',
              'high_mass_age_only', 'low_mass', 'high_mass', 'low_mass_color_shift', 'high_mass_color_shift']
for data, data_name in zip(datas, data_names):
    save_UNITY(data, data_name)