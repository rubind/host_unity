""" cut_salt.py -- Cut the salt fit data to match the SNEMO7 qualtiy cuts.
"""

__author__ = "Benjamin Rose"
__email__ = "brose@stsci.edu"
__data__ = "2019-03-14"
__python__ = "^3.6"

from pathlib import Path
import pickle
import warnings

import numpy as np
import toml

# list of SN names that passed SNEMO 0% error floor and sigma_i <= 2 cuts.

PASSED_02_FILE = Path('snemo7_00_err_lt2.0.txt')
with open(PASSED_02_FILE, 'r') as f:
    PASSED_02_DATA = toml.loads(f.read())
# This next line is bad for memory, but good for quick when rewriting this script to be better above, but the same below.
PASSED_02 = PASSED_02_DATA['names']


with open('salt2_00.pkl', 'rb') as f:
    data = pickle.load(f)

passed_cut = []

for name in data['names']:
    # This if statement could become a lambda function, but this is easier to create
    if name in PASSED_02:
        passed_cut.append(True)
    else:
        passed_cut.append(False)

count = sum(passed_cut)

if count != len(PASSED_02):
    warnings.warn(f'{count} found in pickle file, but {len(PASSED_02)} passed SNEMO7 cuts.', Warning)
    print('SN not in pickle file:')
    for name in PASSED_02:
        if name not in data['names']:
            print(name)
    # TODO(Update so that this stops all makefile dependent operations)
    from sys import exit; exit()


data['n_sne'] = count
data['n_props'] = 4
data['sn_set_inds'] = data['sn_set_inds'][passed_cut]
data['z_helio'] = data['z_helio'][passed_cut]
data['z_CMB'] = data['z_CMB'][passed_cut]
data['obs_mBx1c'] = data['obs_mBx1c'][passed_cut]
mean = np.mean(data['obs_mBx1c'][:,-1])
print('\n\nSHIFTING MASS BY MEAN OF SMAPLE: ', mean, '\n')
data['obs_mBx1c'][:,-1] = data['obs_mBx1c'][:,-1] - mean
print('\nSHIFTING MASS BY MEAN OF SMAPLE: ', mean, '\n\n')
data['obs_mBx1c_cov'] = data['obs_mBx1c_cov'][passed_cut]
print('\n\nADDING 0.1 IN QUAD TO MASS COV!\n')
data['obs_mBx1c_cov'][:, -1, -1] = np.sqrt(data['obs_mBx1c_cov'][:, -1, -1]**2 + 0.1**2)
print('\nADDING 0.1 IN QUAD TO MASS COV!\n\n')

data['n_sn_set'] = 1
data['sn_set_inds'] = np.zeros(count, dtype=np.int)
data['age_gaus_mean'] = np.zeros((0, count, 0))
data['age_gaus_std'] = np.zeros((0, count, 0))
data['age_gaus_A'] = np.zeros((0, count, 0))

with open('salt2_00_passed_snemo7_02.pkl', 'wb') as f:
    pickle.dump(data, f)
