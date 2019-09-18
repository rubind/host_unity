import pickle
import sys
from pathlib import Path

import numpy as np
import toml

file_name = Path(sys.argv[1])
uncert_cut = float(sys.argv[2])
snemo_version = int(sys.argv[3])
mass_index = snemo_version + 1
file_directory = Path.cwd()/file_name.parent


data = pickle.load(open(file_name, 'rb'))


print(data['n_sne'])

count = 0
data_index = 0 
passed_cut = []

for i, j in zip(data['obs_mBx1c_cov'], data['obs_mBx1c']):
    data_index += 1
    # cuts it down to 205 objects
    if np.all(np.sqrt(np.diag(i)[1:mass_index]) < uncert_cut) and np.all(np.abs(j[1:mass_index]) < 5):
        passed_cut.append(True)
        count += 1
        # remove outliers from <2018-12-04 data
#        if count in [9, 21, 61, 64, 68, 96]:
#            print(data_index)
#            passed_cut[-1] = False     # update passed cut to so to remove outliers
    else:
        passed_cut.append(False)


print(count)
print('passed cut', sum(map(int, passed_cut)))


data['n_sne'] = count
data['sn_set_inds'] = data['sn_set_inds'][passed_cut]
data['z_helio'] = data['z_helio'][passed_cut]
data['z_CMB'] = data['z_CMB'][passed_cut]
data['obs_mBx1c'] = data['obs_mBx1c'][passed_cut]
mean = np.mean(data['obs_mBx1c'][:,mass_index])
print('\n\nSHIFTING MASS BY MEAN OF SMAPLE: ', mean, '\n\n')
print('\n\nSHIFTING MASS BY MEAN OF SMAPLE: ', mean, '\n\n')
data['obs_mBx1c'][:,mass_index] = data['obs_mBx1c'][:,mass_index] - mean
print('\n\nSHIFTING MASS BY MEAN OF SMAPLE: ', mean, '\n\n')
print('\n\nSHIFTING MASS BY MEAN OF SMAPLE: ', mean, '\n\n')
data['obs_mBx1c_cov'] = data['obs_mBx1c_cov'][passed_cut]
print('\n\nADDING 0.1 IN QUAD TO MASS COV!\n\n')
print('\n\nADDING 0.1 IN QUAD TO MASS COV!\n\n')
data['obs_mBx1c_cov'][:, mass_index, mass_index] = np.sqrt(data['obs_mBx1c_cov'][:, mass_index, mass_index]**2 + 0.1**2)
print('\n\nADDING 0.1 IN QUAD TO MASS COV!\n\n')
print('\n\nADDING 0.1 IN QUAD TO MASS COV!\n\n')

data['n_sn_set'] = 1
data['sn_set_inds'] = np.zeros(count, dtype=np.int)
data['age_gaus_mean'] = np.zeros((0, count, 0))
data['age_gaus_std'] = np.zeros((0, count, 0))
data['age_gaus_A'] = np.zeros((0, count, 0))

output_name = file_directory/f'{file_name.stem}_err_lt{uncert_cut}.pkl'
with open(output_name.with_suffix('.txt'), 'w') as f:
    print(toml.dumps({'count': count,
                      'names': data['names'][passed_cut]}),
          file=f)
print('names: ', data['names'][passed_cut])

with open(output_name.with_suffix('.pkl'), 'wb') as f:
    pickle.dump(data, f)