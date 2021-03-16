"""simple_test_dataset.py -- Create a simple data set to test installation.

Basic SALT/Tripp standardization.
"""
import pickle

import numpy as np

np.random.seed(13048293)

DATA_NAME = "simple"  # default
N_SNE = 300
# Tripp Coefficients
COFF = [
    -0.14,  # alpha, note negative sign
    3,  # beta
]


# TRUE VALUES
c_true = np.random.randn(N_SNE) * 0.1
x1_true = np.random.randn(N_SNE)
mb_true = COFF[0] * x1_true + COFF[1] * c_true - 20


# OBSERVATIONAL
x1_obs = x1_true + np.random.randn(N_SNE) * 0.3
c_obs = c_true + np.random.randn(N_SNE) * 0.04
mb_obs = mb_true + np.random.randn(N_SNE) * 0.10

# Don't use non-Gaussian parameters
age_gaus_mean = np.zeros((0, N_SNE, 0))
age_gaus_std = np.zeros((0, N_SNE, 0))
age_gaus_A = np.zeros((0, N_SNE, 0))


pickle.dump(
    dict(  # general properties
        n_sne=N_SNE,
        n_props=3,
        n_non_gaus_props=0,
        n_sn_set=1,
        sn_set_inds=[0] * N_SNE,
        # redshifts
        z_helio=[0.1] * N_SNE,
        z_CMB=[0.1] * N_SNE,
        # Gaussian defined properties
        obs_mBx1c=[[mb_obs[i], x1_obs[i], c_obs[i]] for i in range(N_SNE)],
        obs_mBx1c_cov=[
            np.diag(
                [
                    0.05 ** 2,
                    0.3 ** 2,
                    0.04 ** 2,
                ]
            )
        ]
        * N_SNE,
        # Non-Gaussian properties, skip
        n_age_mix=0,
        age_gaus_mean=age_gaus_mean,
        age_gaus_std=age_gaus_std,
        age_gaus_A=age_gaus_A,
        # Other stuff that does not really need to change
        do_fullDint=0,
        outl_frac_prior_lnmean=-4.6,
        outl_frac_prior_lnwidth=1,
        lognormal_intr_prior=0,
        allow_alpha_S_N=0,
    ),
    open(f"test_{DATA_NAME}_{N_SNE}_obs.pkl", "wb"),
)
pickle.dump(
    {"x1": x1_true, "c": c_true, "mass": mass_true, "age": age_true, "mb": mb_true},
    open(f"test_{DATA_NAME}_{N_SNE}_true.pkl", "wb"),
)
