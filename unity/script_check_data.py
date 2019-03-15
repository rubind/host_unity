""" script_check_data.py
"""
import pickle

import numpy as np
from matplotlib import use
use('pdf')
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from corner import corner


file_name = 'pub_snemo7_mcmc_jla+csp+foundation_err_lt1.pkl'
test_data = pickle.load(open(file_name, 'rb'))

pdf = PdfPages(f'check_{file_name}_data.pdf')


plt.figure()
plt.plot(test_data['z_CMB'], test_data['obs_mBx1c'][:, 0], '.')
plt.title('Hubble Diagram')
pdf.savefig()
plt.close()
# plt.savefig('test_hubble.pdf')

plt.figure()
plt.plot(test_data['z_CMB'], test_data['obs_mBx1c'][:, 0] - 5*np.log10(test_data['z_CMB']*(1+test_data['z_CMB'])), '.')
plt.title('Approx Hubble residuals, check log')
pdf.savefig()
plt.close()
# plt.savefig('test_hubble.pdf')

plt.figure()
f = corner(test_data['obs_mBx1c'])
f.suptitle('obs_mBx1c')
pdf.savefig()
plt.close()
# plt.savefig('test_hubble.pdf')
# add mass?

plt.figure()
for i in range(len(test_data['obs_mBx1c'][0])):
    plt.subplot(3,3,i+1)
    plt.hist(test_data['obs_mBx1c'][:, i]/np.sqrt(test_data['obs_mBx1c_cov'][:, i, i]))
    print('pass', i)
plt.suptitle('Value/sqrt(cov[i,i])')
pdf.savefig()
plt.close()
# plt.savefig('test_hubble.pdf')


pdf.close()

print('number of SN data sets: ', test_data['n_sn_set'])
print('median covariance: ', np.median(test_data['obs_mBx1c_cov'], axis=0))
