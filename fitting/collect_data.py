"""Get output of fits into a format for UNITY"""

import os
import copy
import click
import pickle
import sncosmo
import numpy as np
import pandas as pd
from collections import defaultdict
from astropy import units as u
from astropy.io import ascii
from astropy.coordinates import SkyCoord
from scipy.linalg import block_diag


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
    mag = model.bandmag(band='bessellb', time=0, magsys='ab')
    return mag
    


def radectoxyz(RAdeg, DECdeg):
    x = np.cos(DECdeg/(180./np.pi))*np.cos(RAdeg/(180./np.pi))
    y = np.cos(DECdeg/(180./np.pi))*np.sin(RAdeg/(180./np.pi))
    z = np.sin(DECdeg/(180./np.pi))
    return np.array([x, y, z], dtype=np.float64)


def get_dz(RAdeg, DECdeg):
    dzCMB = 371.e3/299792458. # NED
    #http://arxiv.org/pdf/astro-ph/9609034
    #CMBcoordsRA = 167.98750000 # J2000 Lineweaver
    #CMBcoordsDEC = -7.22000000
    CMBcoordsRA = 168.01190437 # NED
    CMBcoordsDEC = -6.98296811
    CMBxyz = radectoxyz(CMBcoordsRA, CMBcoordsDEC)
    inputxyz = radectoxyz(RAdeg, DECdeg)
    dz = dzCMB*np.dot(CMBxyz, inputxyz)
    return dz


def get_zCMB(RAdeg, DECdeg, z_helio):
    dz = -get_dz(RAdeg, DECdeg)
    one_plus_z_pec = np.sqrt((1. + dz)/(1. - dz))
    one_plus_z_CMB = (1 + z_helio)/one_plus_z_pec
    return one_plus_z_CMB - 1.


def get_zhelio(RAdeg, DECdeg, z_CMB):
    dz = -get_dz(RAdeg, DECdeg)
    one_plus_z_pec = np.sqrt((1. + dz)/(1. - dz))
    one_plus_z_helio = (1 + z_CMB)*one_plus_z_pec
    return one_plus_z_helio - 1.


@click.command()
@click.option('-m', '--model', default='snemo7', type=click.Choice(['salt2', 'snemo2', 'snemo7']))
@click.option('-e', '--err_floor', default=0., help='Desired error floor as fraction of maximum band flux.')
@click.option('-p', '--prefix', default='')
def main(model, err_floor, prefix):
    print(model, err_floor, prefix)
    err_floor_int = int(err_floor*100)
    RESULTS_DIR = './results_mw_reddening_mcmc'
    JLA_FIT_DIR = os.path.join(RESULTS_DIR, 'jla_{}_{:02d}/'.format(model, err_floor_int))
    CSP_FIT_DIR = os.path.join(RESULTS_DIR, 'csp_{}_{:02d}/'.format(model, err_floor_int))
    PS_FIT_DIR = os.path.join(RESULTS_DIR, 'ps_{}_{:02d}/'.format(model, err_floor_int))
    
    if model=='snemo7':
        n_props = 9
    else:
        n_props = 4
    MODEL = sncosmo.Model(source=model)
    OUT_PATH = prefix + '{}_{:02d}.pkl'.format(model, err_floor_int)
    
    # Read pickle files from fits and standardize names to check for duplicates
    fits = {}
    for fit_dir in [JLA_FIT_DIR, PS_FIT_DIR, CSP_FIT_DIR]:
        lc_source = fit_dir.split('/')[-2].split('_')[0]
        print('Reading fit results from {}'.format(fit_dir))
        for fname in os.listdir(fit_dir):
            path = os.path.join(fit_dir, fname)
            try:
                name = 'SDSS{}'.format(int(fname.split('.')[0])) # SDSS SNe in JLA just have integer names
            except:
                name = fname.split('.')[0]
                
            if name[:2] == 'sn': # CSP and JLA names use lowercase 'sn'
                name = 'SN'+name[2:]
                
            try:
                if name in fits.keys():
                    duplicate_source = fits[name]['lc_source']
                    print(name+' duplicated in datasets {} and {}. Using {}'.format(duplicate_source, lc_source, lc_source))
                fits[name] = pickle.load(open(path, 'rb'))
                fits[name]['lc_source'] = lc_source
            except IsADirectoryError:
                continue
    
    fit_df = pd.DataFrame.from_dict(fits).T
    for i, param_name in enumerate(fit_df['vparam_names'][0]):
        fit_df[param_name] = [x[i] for x in fit_df['parameters'].values]
        fit_df['d'+param_name] = [x[param_name] for x in fit_df['errors'].values]
    
    # Get all meta data in the same format ######################################
    
    # JLA
    jla = pd.read_csv(os.path.join('/home/samdixon/jla_light_curves/jla_lcparams.txt'),
                       delim_whitespace=True)
    jla = jla[['name', 'zcmb', 'zhel', '3rdvar', 'd3rdvar', 'set']]
    jla = jla.rename({'3rdvar': 'logM', 'd3rdvar': 'logM_err'}, axis=1)
    jla = jla.set_index('name')
    
    standardized_names = []
    for name in jla.index:
        if name[:2] == 'sn':
            name = 'SN'+name[2:]
        standardized_names.append(name)
    jla.index = standardized_names
    jla['host_source'] = ['JLA' for x in jla.index]
    
    # CSP
    csp_meta = pd.read_csv('/home/samdixon/CSP_Photometry_DR3/tab1.dat', delimiter='\t', comment='#')
    csp_meta = csp_meta.set_index('SN')
    csp_meta['RA_deg'] = csp_meta.apply(lambda x: SkyCoord(x.RA, x.DEC,
                                                           unit=(u.hourangle, u.degree)).ra.degree, axis=1)
    csp_meta['DEC_deg'] = csp_meta.apply(lambda x: SkyCoord(x.RA, x.DEC,
                                                            unit=(u.hourangle, u.degree)).dec.degree, axis=1)
    csp_meta['zcmb'] = csp_meta.apply(lambda x: get_zCMB(x.RA_deg, x.DEC_deg, x.zhelio), axis=1)
    
    jones_csp_host = sncosmo.read_snana_ascii('CSP_lcparams.dat', default_tablename='SN')[1]['SN'].to_pandas()
    jones_csp_host = jones_csp_host.set_index('CID')
    
    gupta_host = pd.read_csv('gupta_host.txt', delim_whitespace=True)
    gupta_host = gupta_host.set_index('name')
    gupta_host.index = [name.replace('_', '-') if name[:6]=='ASASSN' else name for name in gupta_host.index]
    
    combined_csp = defaultdict(list)
    for sn in csp_meta.index:
        match_rg = gupta_host[gupta_host.index.str.contains(sn)]
        if len(match_rg)==1:
            combined_csp['SN'].append(sn)
            combined_csp['logM'].append(match_rg.Mass.values[0])
            combined_csp['logM_err'].append(np.mean([match_rg.Mass_lo, match_rg.Mass_hi]))
            combined_csp['host_source'].append('RG')
        else:
            match_dj = jones_csp_host[jones_csp_host.index.str.contains(sn.lower())]
            if len(match_dj)==1:
                combined_csp['SN'].append(sn)
                combined_csp['logM'].append(match_dj.HOST_LOGMASS.values[0])
                combined_csp['logM_err'].append(match_dj.HOST_LOGMASS_ERR.values[0])
                combined_csp['host_source'].append('DJ')
    combined_csp = pd.DataFrame(combined_csp)
    combined_csp = combined_csp.set_index('SN')
    combined_csp = combined_csp.merge(csp_meta[['zcmb', 'zhelio']], left_index=True, right_index=True)
    combined_csp = combined_csp.rename({'zhelio': 'zhel'}, axis=1)
    combined_csp.index = ['SN'+x for x in combined_csp.index]
    combined_csp['set'] = [jla.set.max()+1 for x in combined_csp.index]
    
    # Foundation
    ps_data = pd.read_csv('/home/samdixon/foundation_photometry.txt', delimiter=', ', engine='python')
    ps_meta = ascii.read('/home/samdixon/foundation_lc_params.tex', format='latex').to_pandas()
    ps_meta = ps_meta.set_index('SN')
    ps_meta['zcmb'] = [float(x.split()[0]) for x in ps_meta['z_CMB'].values]
    ps_meta['zhel'] = [float(x.split()[0]) for x in ps_meta['z_helio'].values]
    
    jones_ps_host = sncosmo.read_snana_ascii('PS_lcparams.dat', default_tablename='SN')[1]['SN'].to_pandas()
    jones_ps_host = jones_ps_host.set_index('CID')
    
    gupta_host = pd.read_csv('gupta_host.txt', delim_whitespace=True)
    gupta_host = gupta_host.set_index('name')
    gupta_host.index = [name.replace('_', '-') if name[:6]=='ASASSN' else name for name in gupta_host.index]
    
    combined_ps = defaultdict(list)
    for sn in ps_meta.index:
        match_rg = gupta_host[gupta_host.index.str.contains(sn)]
        if len(match_rg)==1:
            combined_ps['SN'].append(sn)
            combined_ps['logM'].append(match_rg.Mass.values[0])
            combined_ps['logM_err'].append(np.mean([match_rg.Mass_lo, match_rg.Mass_hi]))
            combined_ps['host_source'].append('RG')
        else:
            match_dj = jones_ps_host[jones_ps_host.index.str.contains(sn.lower())]
            if len(match_dj)==1:
                combined_ps['SN'].append(sn)
                combined_ps['logM'].append(match_dj.HOST_LOGMASS.values[0])
                combined_ps['logM_err'].append(match_dj.HOST_LOGMASS_ERR.values[0])
                combined_ps['host_source'].append('DJ')
    combined_ps = pd.DataFrame(combined_ps)
    combined_ps = combined_ps.set_index('SN')
    ps_meta = ps_meta.drop(['x_1', 'c', 'm_B'], axis=1)
    ps_meta = ps_meta.drop(['z_helio', 'z_CMB', 'Peak_MJD'], axis=1)
    combined_ps = combined_ps.merge(ps_meta, left_index=True, right_index=True)
    combined_ps['set'] = [jla.set.max()+2 for x in combined_ps.index]
    
    # Putting everything together
    combined_meta = pd.concat([jla, combined_csp, combined_ps], sort=True)
    
    # Drop duplicates
    combined_meta = combined_meta.reset_index().drop_duplicates(subset='index', keep='last').set_index('index')
    
    # Join fits (already deduped)
    data = fit_df.join(combined_meta, how='inner')
    
    # Convert c0 to mb
    data['mbstar'] = [calc_mbstar(MODEL, x['parameters'][2:], x['zhel']) for _, x in data.iterrows()]
    
    # Drop nans
    print('N_sne before NaN cut:', len(data))
    data = data.dropna(subset=['mbstar'])
    print('N_sne after NaN cut:', len(data))
                
    # Convert observed parameters into an array
    obs_data = np.hstack([np.array([[x] for x in data.mbstar.values]),
                          np.array([x[3:-2] for x in data.parameters.values]),
                          np.array([[x] for x in data['logM'].values])])
    
    # Calculate the combined covariance matrix
    obs_cov = []
    for _, sn in data.iterrows():
        cov = np.zeros((len(sn.parameters)-3, len(sn.parameters)-3))
        cov[0, 0] = sn.covariance[2, 2] * (-2.5/(np.log(10)*sn.parameters[2]))**2 # diagonal, m_b
        cov[1:-1, 0] = sn.covariance[3:, 2] * (-2.5/(np.log(10)*sn.parameters[2])) # off-diagonal, m_b x c_i
        cov[0, 1:-1] = sn.covariance[2, 3:] * (-2.5/(np.log(10)*sn.parameters[2])) # off-diagonal, c_i x m_b
        cov[1:-1, 1:-1] = sn.covariance[3:, 3:] # c_i x c_j
        cov[-1, -1] = sn['logM_err']**2
        obs_cov.append(cov)
    obs_cov = np.array(obs_cov)
    
    # Format for Stan
    stan_data = {'n_sne': len(data),
                 'names': data.index.values,
                 'n_props': n_props,
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
    
    # Dump host source attributions
    full_data_out_path = prefix + 'full_data_{}_{:02d}.csv'.format(model, err_floor_int)
    data.to_csv(full_data_out_path)
    
    print(data.set.value_counts())
    
if __name__=='__main__':
    main()