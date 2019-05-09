"""get_N_dataset.py -- return the number in each data set for a list of SN.
"""

__author__ = 'Benjamin Rose <brose@stsci.edu'

import pickle
import sys
from pathlib import Path
from collections import Counter

import numpy as np

SN = sys.argv[1:]
# test from 2% error model with sigma <= 1
# SN = ['sn2004ey', 'sn2006ax', 'sn2006bh', 'sn2005ki', 'sn2005hc', 'sn2005na', 'sn2005al',
      # 'sn2005ag', 'sn2004gu', 'SDSS3901', 'SN2004eo', 'SN2006D', 'SN2005M']
data_file = Path('pub_snemo7_mcmc_jla+csp+foundation.pkl')

with open(data_file, 'rb') as f:
    data = pickle.load(f)

names = data['names']
data_sets = data['sn_set_inds']
# print(np.where(names==SN))
data_sets_in = data_sets[np.isin(names, SN)]
from_data_set = Counter(data_sets_in)
print(from_data_set)

print("Number of SN from JLA: ", from_data_set[0] + from_data_set[1] + from_data_set[2] + from_data_set[3])
print("Number of SN from CSP: ", from_data_set[4])
print("Number of SN from Foundation: ", from_data_set[5])
