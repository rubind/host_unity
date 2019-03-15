""" cut_salt.py -- Cut the salt fit data to match the SNEMO7 qualtiy cuts.
"""

__author__ = "Benjamin Rose"
__email__ = "brose@stsci.edu"
__data__ = "2019-03-14"
__python__ = "^3.6"

import pickle

import numpy as np

# list of SN names that passed SNEMO 0% error floor and sigma_i <= 2 cuts.
PASSED_02 = ['05D4bm', 'sn2004s', 'sn2005ms', '06D2fb', 'sn2004ey', 'SDSS14816', 'sn2001cn',
             '05D3jr', 'sn2006oa', 'sn2006mo', 'SDSS12779', 'SDSS19155', 'sn2006qo',
             'sn2000ca', '04D4jr', 'SDSS14279', '06D4co', 'sn2005kc', 'SDSS13135', '05D4fo',
             'sn1999gp', '04D2fs', 'sn2002ha', 'sn2001ep', 'SDSS18241', '04D3nh', '05D3dd',
             'SDSS1241', 'sn1993h', 'sn2005el', 'sn2000cf', 'sn2006ax', 'sn2001bf', '06D3fp',
             '03D1ax', 'sn2006az', '05D2ab', '03D4cj', 'sn2001v', 'sn2007ci', 'sn2007ae',
             'sn2006td', '06D4dh', '04D3fk', 'sn2006an', 'sn2007bc', '04D1hd', 'sn2005iq',
             'sn2006bh', 'SDSS3592', 'sn1995ac', 'sn2006ej', 'sn2005ki', 'sn2006s',
             'sn2002hu', 'sn2003fa', 'sn2005eq', 'sn1998ab', 'sn2005hc', 'sn2005ir',
             '05D1hk', 'sn1998v', '03D1bp', 'sn2001ba', '04D4gg', '03D4ag', 'sn2006mp',
             'sn2005bo', 'sn2006ac', 'SDSS17784', 'sn1992bp', 'sn2006n', '04D3ez',
             'SDSS12950', '05D3kx', 'sn2005bg', 'sn2006bq', 'sn2007co', 'sn1999aa',
             'SDSS6057', 'sn1999dq', 'SDSS722', 'sn1992bc', 'SDSS17880', 'sn2006sr',
             'SDSS12898', 'sn2008bf', 'sn1992al', '05D2ah', 'sn2005eu', 'SDSS2102',
             'sn2006gr', 'sn2004eo', 'sn2005na', 'sn2005al', 'sn2006on', '06D3el',
             'sn2007qe', 'sn2004gs', '06D3dt', 'sn2005ag', 'sn1992bl', 'SDSS12781', '05D1ix',
             'SDSS6558', 'sn1999ac', 'SDSS17745', 'SDSS19899', 'sn2001cz', 'sn2004gu',
             '04D1dc', 'sn2007f', 'SDSS17186', 'sn2006et', 'sn2001bt', 'SDSS3901',
             'ASASSN-15lg', '2016fbk', 'PS17yt', 'ASASSN-15hg', '2016gmg', 'PS15bsq',
             'PS15cms', 'PS15aii', '2016W', 'ASASSN-15mf', 'ASASSN-15np', '2017jl',
             '2016ews', '2016hns', '2017cfc', '2017mf', 'ASASSN-15sf', 'ASASSN-15pm',
             'ASASSN-15uv', 'ASASSN-17co', '2016bln', 'PS15bdr', 'ASASSN-15la', 'PS15bwh',
             'ASASSN-15pn', 'ASASSN-15il', 'PS15cku', '2017wb', 'PS17tn', 'ASASSN-15mg',
             'ASASSN-15tg', '2016esh', '2017hn', 'ASASSN-15od', 'ASASSN-15mi', '2016aqb',
             '2016cyt', '2017ckx', 'ASASSN-15fa', 'ASASSN-15fs', '2016afk', '2017cfb',
             'PS15ahs', '2016cvv', '2016gmb', 'PS15bbn', 'ASASSN-15bc', 'ASASSN-15nr',
             '2017cii', 'PS15asb', 'ASASSN-15ss', '2016glz', '2016htm', 'SN2005bo',
             'SN2005na', 'SN2006ej', 'SN2007sr', 'SN2006bh', 'SN2006gj', 'SN2008bq',
             'SN2005ki', 'SN2005W', 'SN2008gp', 'SN2006lu', 'SN2008bt', 'SN2004gs',
             'SN2004ef', 'SN2007hx', 'SN2006et', 'SN2005el', 'SN2006hb', 'SN2006ev',
             'SN2004gu', 'SN2009D', 'SN2006eq', 'SN2007bc', 'SN2005bg', 'SN2005kc',
             'SN2008hj', 'SN2007bm', 'SN2004ey', 'SN2007bd', 'SN2006ax', 'SN2005eq',
             'SN2006ob', 'SN2005hk', 'SN2004eo', 'SN2008gl', 'SN2006bt', 'SN2008bz',
             'SN2008hv', 'SN2008hu', 'SN2007jg', 'SN2007jd', 'SN2007le', 'SN2006hx',
             'SN2006is', 'SN2008C', 'SN2007ux', 'SN2005iq', 'SN2006D', 'SN2005mc',
             'SN2006py', 'SN2005be', 'SN2008bf', 'SN2006fw', 'SN2005hc', 'SN2005ag',
             'SN2007ai', 'SN2006ef', 'SN2008cf', 'SN2005lu', 'SN2007S', 'SN2005hj',
             'SN2008ar', 'SN2008R', 'SN2006gt', 'SN2005ku', 'SN2005M', 'SN2005ir',
             'SN2007ba', 'SN2007af', 'SN2008fr', 'SN2004gc', 'SN2007nq', 'SN2004dt',
             'SN2009ds', 'SN2006kf']

with open('jla+csp+ps_salt2_00.pkl', 'rb') as f:
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
    raise Warning(f'{count} found in pickle file, but {len(PASSED_02)} passed SNEMO7 cuts.')
    print('SN not in pickle file:')
    for name in PASSED_02:
        if name not in data['names']:
            print(name)
    from sys import exit; exit()


data['n_sne'] = count
data['n_props'] = 4
data['sn_set_inds'] = data['sn_set_inds'][passed_cut]
data['z_helio'] = data['z_helio'][passed_cut]
data['z_CMB'] = data['z_CMB'][passed_cut]
data['obs_mBx1c'] = data['obs_mBx1c'][passed_cut]
print('\n\nCHANGING COLOR VALUE BY -0.27!!\n')
data['obs_mBx1c'][:,1] = data['obs_mBx1c'][:,1] - 0.27
print('\nCHANGING COLOR VALUE BY -0.27!!\n\n')
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

pickle.dump(data, open(f'satl2_jla+csp+ps_SNEMO7_02_passed.pkl', 'wb'))
print('\n\nChanged color value by -0.27!')