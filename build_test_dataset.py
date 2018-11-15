"""
"""
import pickle

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import corner

np.random.seed(13048293)

N_SNE = 1000
YOUNG_FRAC = 0.95
N_YOUNG = int(N_SNE*YOUNG_FRAC)
N_OLD = N_SNE - N_YOUNG


# TRUE VALUES


c_true = np.random.randn(N_SNE)*0.1

mass_young = np.random.randn(N_YOUNG) + 11 - np.random.exponential(0.5, N_YOUNG)
mass_old = np.random.randn(N_OLD)*0.75 + 11
mass_true = np.concatenate((mass_young, mass_old))

x1_true = np.random.randn(N_SNE)*((mass_true>10)*0.75 + (mass_true<=10)*0.9) + ((mass_true>10)*-0.5 + (mass_true<=10)*0.1)

age_young = (np.random.triangular(0.25, 0.5, 6, size=N_YOUNG)*(mass_young/4)
             + np.random.exponential(size=N_YOUNG)*x1_true[:N_YOUNG]/3)
age_old = np.random.randn(N_OLD)*0.75 + 10
age_true = np.append(age_young, age_old)

COFF = [-0.1, 3, 0.05/0.5, 0.05/2]
# mb_true = COFF[0]*x1_true + COFF[1]*c_true + COFF[2]*mass_true + COFF[3]*age_true - 20
mb_true = COFF[0]*x1_true + COFF[1]*c_true - 20

# corner.corner(np.array([x1_true, c_true, mass_true, age_true, mb_true]).T, labels=['x1', 'c', 'mass', 'age', 'M'])
# plt.show()


# OBSERVATIONAL

x1_obs = x1_true + np.random.randn(N_SNE)*0.3
c_obs = c_true + np.random.randn(N_SNE)*0.04
mass_obs = mass_true + np.random.randn(N_SNE)*0.5
age_obs = np.abs(age_true + np.random.randn(N_SNE)*0.2*age_true)  # todo(add obs systematic)
mb_obs = mb_true + np.random.randn(N_SNE)*0.15


# corner.corner(np.array([x1_obs, c_obs, mass_obs, age_obs, mb_obs]).T, labels=['x1', 'c', 'mass', 'age', 'M'], show_titles=True)
# plt.show()


# SAVE DATA

pickle.dump(dict(n_sne=N_SNE, n_props=5, n_non_gaus_props=1, n_sn_set=1,
    sn_set_inds=[0]*N_SNE, z_helio=[0.1]*N_SNE, z_CMB=[0.1]*N_SNE,
    obs_mBx1c=[[mb_obs[i], x1_obs[i], c_obs[i], mass_obs[i]] for i in range(N_SNE)],
    obs_mBx1c_cov=[np.diag([0.05**2, 0.3**2, 0.04**2, 0.3**2])]*N_SNE,
    n_age_mix=1, age_gaus_mean=[np.array([age_obs]).T], 
    age_gaus_std=[np.array([0.2*np.abs(age_true)]).T],
    age_gaus_A=np.ones((1, N_SNE, 1), dtype=np.float),
    do_fullDint=0, outl_frac_prior_lnmean=-4.6, outl_frac_prior_lnwidth=1,
    lognormal_intr_prior=0, allow_alpha_S_N=0),
    open(f'sample_obs_{N_SNE}SNe', 'wb')
    )
pickle.dump({'x1'   : x1_true,
             'c'    : c_true,
             'mass' : mass_true,
             'age'  : age_true,
             'mb'    : mb_true},
    open(f'Sample_true_{N_SNE}SNe', 'wb')
    )