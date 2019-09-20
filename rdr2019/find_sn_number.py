"""find_sn_number.py -- Converts UNITY index number to SN name.

This script can either take a command line arguments (WIP) or use hard
coded values for the UNITY analyzed data set and indexes of interest.
The data set is something like `snemo2_01_err_lt1.0.pkl` and the index
are the first dimensional indexes in a UNITY variable like `true_x1cs`.
These indexes are zero indexed, just like python.
"""

__author__ = 'Benjamin Rose <brose@stsci.edu>'
__email__ = 'brose@stsci.edu'
__python__ = '^3.7'
__date__ = '2019-05-21'

import pickle
from sys import argv

if len(argv) > 1:
    model = argv[1]
    indexes = argv[2:]
else:
    model = 'snemo2_01_err_lt1.0.pkl'
    indexes = [622, 791, 792, 795, 797, 803, 805, 812, 814, 822, 830, 839, 840, 850, 855, 860,
             867, 869, 879, 884, 886, 888]

with open(model, 'rb') as f:
    data = pickle.load(f)

names = data['names']
print(names[indexes])