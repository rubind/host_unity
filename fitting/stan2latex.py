"""stan2latex.py -- Convert stan output pickle files to a latex table.

Currently designed specifically for table 2 in Rose, Dixon, Rubin et al. 2019.
"""

__author__ = 'Benjamin Rose <brose@stsci.edu>'
__python__ = '^3.6'

import gzip
import pickle
from pathlib import Path
import re

import numpy as np
import toml

FIL_DIR = Path(__file__).resolve().parent

# Stan parameters of interest
FILES = [FIL_DIR / 'fixed_snemo7_00_err_lt1.0_fitparams.gzip.pkl',
         FIL_DIR / 'fixed_snemo7_00_err_lt2.0_fitparams.gzip.pkl',
         FIL_DIR / 'fixed_snemo7_01_err_lt1.0_fitparams.gzip.pkl', 
         FIL_DIR / 'fixed_snemo7_01_err_lt2.0_fitparams.gzip.pkl', 
         FIL_DIR / 'fixed_snemo7_02_err_lt1.0_fitparams.gzip.pkl',
         FIL_DIR / 'fixed_snemo7_02_err_lt2.0_fitparams.gzip.pkl',
         FIL_DIR / 'salt2_00_passed_snemo7_02_fitparams.gzip.pkl',
         FIL_DIR / 'fixed_snemo2_00_err_lt2.0_fitparams.gzip.pkl',
         FIL_DIR / 'fixed_snemo2_01_err_lt2.0_fitparams.gzip.pkl',
         FIL_DIR / 'fixed_snemo2_02_err_lt2.0_fitparams.gzip.pkl']
FIT_PARAMS = ['MB', 'sigma_int', 'coeff', 'outl_frac']
TABLE_NAMES = [r'M$_B$', r'$\sigma_{\rm intrinsic}$', r'$\beta$', r'$\alpha_1$', r'$\alpha_2$', r'$\alpha_3$',
               r'$\alpha_4$', r'$\alpha_5$', r'$\alpha_6$', r'$\gamma$', r'$f^{outl}$']


def table_data(f: Path) -> tuple:
    """Get the data to be put into the LaTeX table from the UNITY output file.

    Parameters
    ----------
    f: Path
        String of the file. For example, 'pub_snemo7_mcmc_jla+csp+foundation_02_err_lt2_fitparams.gzip.pkl'.

    Returns
    -------
    MB: tuple of 3 floats
        Floats are the mean (50.0th percentile), plus uncertainty (84.1345th -
        50.0th percentile) and minus uncertainty (15.8655th - 50.0th percentile).
    sigma_int: tuple of 3 floats
        Floats are the 15.8655, 50.0, and 84.1345 percentiles of the samples.
    coeff: tuple of 3 tuples of 8 floats, size (3, 8)
        First tuple is the 8 15.8655 percentile for the 8 coeffs of this sample. The next
        tuple is for the 50th percentiles. Finally, the last tuple is for the 8 84.1345th
        percentiles.
    outl_frac: tuple of 3 floats
        Floats are the 15.8655, 50.0, and 84.1345 percentiles of the samples.
    """
    with gzip.open(f, 'rb') as stan_output:
        data = pickle.load(stan_output)

    # print(data.keys())
    # print(data['MB'].shape)
    # print([np.percentile(data[x], [15.8655, 50.0, 84.1345])[0] for x in FIT_PARAMS])
    MB = [np.percentile(data['MB'], [15.8655, 50.0, 84.1345])][0]
    sigma_int = [np.percentile(data['sigma_int'], [15.8655, 50.0, 84.1345])][0]
    coeff = [np.percentile(data['coeff'], [15.8655, 50.0, 84.1345], axis=0)][0]   # (percentile, coeff)

    MB = np.array([MB[1], MB[2] - MB[1], MB[0] - MB[1]])
    sigma_int = np.array([sigma_int[1], sigma_int[2] - sigma_int[1], sigma_int[0] - sigma_int[1]])
    coeff = np.array([coeff[1][:], coeff[2][:] - coeff[1][:],  coeff[0][:] - coeff[1][:]])

    return MB, sigma_int, coeff


def outlier_percent(f: Path) -> str:
    """Get the data to be put into the LaTeX table from the UNITY output file.

    Parameters
    ----------
    f: Path
        String of the file. For example, 'pub_snemo7_mcmc_jla+csp+foundation_02_err_lt2_fitparams.gzip.pkl'.
    """
    # go from "snemo7_00_err_lt1.0_fitparams.gzip.pkl" to "snemo7_00_err_lt1.0.txt"
    meta_data_file = f.parent / (f.name[:-19] + ".txt")
    with open(meta_data_file, 'r') as f_:
        meta_data = toml.load(f_)
    N = meta_data['count']

    # go from "snemo7_00_err_lt1.0_fitparams.gzip.pkl" to "snemo7_00_err_lt1.0_results.txt"
    results_file = f.parent / (f.name[:-18] + "results.txt")
    with open(results_file, 'r') as f_:
        results = f_.read()
    outliers = re.findall(r'outl_loglike\[\d*\]\s*-', results)
    N_out = len(outliers)

    return N, f'{N_out} ({N_out/N*100:.2}\\%)'


# MB, sigma_int, coeff, outl_frac = table_data('pub_snemo7_mcmc_jla+csp+foundation_02_err_lt2_fitparams.gzip.pkl')
print('Calculating SNEMO7 results.')
MB_01, sigma_int_01, coeff_01 = table_data(FILES[0])
MB_02, sigma_int_02, coeff_02 = table_data(FILES[1])
MB_11, sigma_int_11, coeff_11 = table_data(FILES[2])
MB_12, sigma_int_12, coeff_12 = table_data(FILES[3])
MB_21, sigma_int_21, coeff_21 = table_data(FILES[4])
MB_22, sigma_int_22, coeff_22 = table_data(FILES[5])
MB_salt, sigma_int_salt, coeff_salt = table_data(FILES[6])
print('Calculating SNEMO2 results.')
MB_snemo2_02, sigma_int_snemo2_02, coeff_snemo2_02 = table_data(FILES[7])
MB_snemo2_12, sigma_int_snemo2_12, coeff_snemo2_12 = table_data(FILES[8])
MB_snemo2_22, sigma_int_snemo2_22, coeff_snemo2_22 = table_data(FILES[9])

print('Calculating outliers.')
N_01, outl_frac_01 = outlier_percent(FILES[0])
N_02, outl_frac_02 = outlier_percent(FILES[1])
N_11, outl_frac_11 = outlier_percent(FILES[2])
N_12, outl_frac_12 = outlier_percent(FILES[3])
N_21, outl_frac_21 = outlier_percent(FILES[4])
N_22, outl_frac_22 = outlier_percent(FILES[5])
N_salt, outl_frac_salt = outlier_percent(FILES[6])
N_snemo2_02, outl_frac_snemo2_02 = outlier_percent(FILES[7])
N_snemo2_12, outl_frac_snemo2_12 = outlier_percent(FILES[8])
N_snemo2_22, outl_frac_snemo2_22 = outlier_percent(FILES[9])


# Build a table.
# TODO: Could I build this with a double for loop?
# Loop per line, loop per column and concatenate!
TABLE_ROW = f'''
Data set size & {N_salt} & {N_snemo2_02} & {N_snemo2_12} & {N_snemo2_22} & {N_01} & {N_02} & {N_11} & {N_12} & {N_21} & {N_22} \\\\ \\hline
{TABLE_NAMES[0]}  & ${MB_salt[0]:.1f}^{{+{MB_salt[1]:.2f}}}_{{{MB_salt[2]:.2f}}}$                      & ${MB_snemo2_02[0]:.1f}^{{+{MB_snemo2_02[1]:.2f}}}_{{{MB_snemo2_02[2]:.2f}}}$                      & ${MB_snemo2_12[0]:.1f}^{{+{MB_snemo2_12[1]:.2f}}}_{{{MB_snemo2_12[2]:.2f}}}$                      & ${MB_snemo2_22[0]:.1f}^{{+{MB_snemo2_22[1]:.2f}}}_{{{MB_snemo2_22[2]:.2f}}}$                  & ${MB_01[0]:.1f}^{{+{MB_01[1]:.2f}}}_{{{MB_01[2]:.2f}}}$ & ${MB_02[0]:.1f}^{{+{MB_02[1]:.2f}}}_{{{MB_02[2]:.2f}}}$ & ${MB_11[0]:.1f}^{{+{MB_11[1]:.2f}}}_{{{MB_11[2]:.2f}}}$ & ${MB_12[0]:.1f}^{{+{MB_12[1]:.2f}}}_{{{MB_12[2]:.2f}}}$ & ${MB_21[0]:.1f}^{{+{MB_21[1]:.2f}}}_{{{MB_21[2]:.2f}}}$ & ${MB_22[0]:.1f}^{{+{MB_22[1]:.2f}}}_{{{MB_22[2]:.2f}}}$\\\\
{TABLE_NAMES[1]}  & ${sigma_int_salt[0]:.3f}^{{+{sigma_int_salt[1]:.3f}}}_{{{sigma_int_salt[2]:.3f}}}$ & ${sigma_int_snemo2_02[0]:.3f}^{{+{sigma_int_snemo2_02[1]:.3f}}}_{{{sigma_int_snemo2_02[2]:.3f}}}$ & ${sigma_int_snemo2_12[0]:.2f}^{{+{sigma_int_snemo2_12[1]:.2}}}_{{{sigma_int_snemo2_12[2]:.2}}}$ & ${sigma_int_snemo2_22[0]:.2f}^{{+{sigma_int_snemo2_22[1]:.2}}}_{{{sigma_int_snemo2_22[2]:.2}}}$ & ${sigma_int_01[0]:.2f}^{{+{sigma_int_01[1]:.2f}}}_{{{sigma_int_01[2]:.2f}}}$ & ${sigma_int_02[0]:.2f}^{{+{sigma_int_02[1]:.2f}}}_{{{sigma_int_02[2]:.2f}}}$ & ${sigma_int_11[0]:.2f}^{{+{sigma_int_11[1]:.2f}}}_{{{sigma_int_11[2]:.2f}}}$ & ${sigma_int_12[0]:.2f}^{{+{sigma_int_12[1]:.2f}}}_{{{sigma_int_12[2]:.2f}}}$ & ${sigma_int_21[0]:.2f}^{{+{sigma_int_21[1]:.2f}}}_{{{sigma_int_21[2]:.2f}}}$ & ${sigma_int_22[0]:.2f}^{{+{sigma_int_22[1]:.2f}}}_{{{sigma_int_22[2]:.2f}}}$\\\\
{TABLE_NAMES[2]}  & ${coeff_salt[0][1]:.2f}^{{+{coeff_salt[1][1]:.2f}}}_{{{coeff_salt[2][1]:.2f}}}$  & ${coeff_snemo2_02[0][0]:.2f}^{{+{coeff_snemo2_02[1][0]:.2f}}}_{{{coeff_snemo2_02[2][0]:.2f}}}$  & ${coeff_snemo2_12[0][0]:.3f}^{{+{coeff_snemo2_12[1][0]:.3f}}}_{{{coeff_snemo2_12[2][0]:.3f}}}$  & ${coeff_snemo2_22[0][0]:.3f}^{{+{coeff_snemo2_22[1][0]:.3f}}}_{{{coeff_snemo2_22[2][1]:.3f}}}$  & ${coeff_01[0][0]:.3f}^{{+{coeff_01[1][0]:.3f}}}_{{{coeff_01[2][0]:.3f}}}$ & ${coeff_02[0][0]:.3f}^{{+{coeff_02[1][0]:.3f}}}_{{{coeff_02[2][0]:.3f}}}$ & ${coeff_11[0][0]:.3f}^{{+{coeff_11[1][0]:.3f}}}_{{{coeff_11[2][0]:.3f}}}$ & ${coeff_12[0][0]:.3f}^{{+{coeff_12[1][0]:.3f}}}_{{{coeff_12[2][0]:.3f}}}$ & ${coeff_21[0][0]:.3f}^{{+{coeff_21[1][0]:.3f}}}_{{{coeff_21[2][0]:.3f}}}$ & ${coeff_22[0][0]:.3f}^{{+{coeff_22[1][0]:.3f}}}_{{{coeff_22[2][0]:.3f}}}$\\\\
{TABLE_NAMES[3]}  & ${coeff_salt[0][0]:.3f}^{{+{coeff_salt[1][0]:.3f}}}_{{{coeff_salt[2][0]:.3f}}}$  & ${coeff_snemo2_02[0][1]:.3f}^{{+{coeff_snemo2_02[1][1]:.3f}}}_{{{coeff_snemo2_02[2][1]:.3f}}}$  & ${coeff_snemo2_12[0][1]:.3f}^{{+{coeff_snemo2_12[1][1]:.3f}}}_{{{coeff_snemo2_12[2][1]:.3f}}}$  & ${coeff_snemo2_22[0][1]:.3f}^{{+{coeff_snemo2_22[1][1]:.3f}}}_{{{coeff_snemo2_22[2][0]:.3f}}}$  & ${coeff_01[0][1]:.3f}^{{+{coeff_01[1][1]:.3f}}}_{{{coeff_01[2][1]:.3f}}}$ & ${coeff_02[0][1]:.3f}^{{+{coeff_02[1][1]:.3f}}}_{{{coeff_02[2][1]:.3f}}}$ & ${coeff_11[0][1]:.3f}^{{+{coeff_11[1][1]:.3f}}}_{{{coeff_11[2][1]:.3f}}}$ & ${coeff_12[0][1]:.3f}^{{+{coeff_12[1][1]:.3f}}}_{{{coeff_12[2][1]:.3f}}}$ & ${coeff_21[0][1]:.3f}^{{+{coeff_21[1][1]:.3f}}}_{{{coeff_21[2][1]:.3f}}}$ & ${coeff_22[0][1]:.3f}^{{+{coeff_22[1][1]:.3f}}}_{{{coeff_22[2][1]:.3f}}}$\\\\
{TABLE_NAMES[4]}  & \\nodata                                                                         & \\nodata                                                                                        & \\nodata                                                                         & \\nodata                                                                                                       & ${coeff_01[0][2]:.3f}^{{+{coeff_01[1][2]:.3f}}}_{{{coeff_01[2][2]:.3f}}}$ & ${coeff_02[0][2]:.3f}^{{+{coeff_02[1][2]:.3f}}}_{{{coeff_02[2][2]:.3f}}}$ & ${coeff_11[0][2]:.3f}^{{+{coeff_11[1][2]:.3f}}}_{{{coeff_11[2][2]:.3f}}}$ & ${coeff_12[0][2]:.3f}^{{+{coeff_12[1][2]:.3f}}}_{{{coeff_12[2][2]:.3f}}}$ & ${coeff_21[0][2]:.3f}^{{+{coeff_21[1][2]:.3f}}}_{{{coeff_21[2][2]:.3f}}}$ & ${coeff_22[0][2]:.3f}^{{+{coeff_22[1][2]:.3f}}}_{{{coeff_22[2][2]:.3f}}}$\\\\
{TABLE_NAMES[5]}  & \\nodata                                                                         & \\nodata                                                                                        & \\nodata                                                                         & \\nodata                                                                                                       & ${coeff_01[0][3]:.3f}^{{+{coeff_01[1][3]:.3f}}}_{{{coeff_01[2][3]:.3f}}}$ & ${coeff_02[0][3]:.3f}^{{+{coeff_02[1][3]:.3f}}}_{{{coeff_02[2][3]:.3f}}}$ & ${coeff_11[0][3]:.3f}^{{+{coeff_11[1][3]:.3f}}}_{{{coeff_11[2][3]:.3f}}}$ & ${coeff_12[0][3]:.3f}^{{+{coeff_12[1][3]:.3f}}}_{{{coeff_12[2][3]:.3f}}}$ & ${coeff_21[0][3]:.3f}^{{+{coeff_21[1][3]:.3f}}}_{{{coeff_21[2][3]:.3f}}}$ & ${coeff_22[0][3]:.3f}^{{+{coeff_22[1][3]:.3f}}}_{{{coeff_22[2][3]:.3f}}}$\\\\
{TABLE_NAMES[6]}  & \\nodata                                                                         & \\nodata                                                                                        & \\nodata                                                                         & \\nodata                                                                                                       & ${coeff_01[0][4]:.3f}^{{+{coeff_01[1][4]:.3f}}}_{{{coeff_01[2][4]:.3f}}}$ & ${coeff_02[0][4]:.3f}^{{+{coeff_02[1][4]:.3f}}}_{{{coeff_02[2][4]:.3f}}}$ & ${coeff_11[0][4]:.3f}^{{+{coeff_11[1][4]:.3f}}}_{{{coeff_11[2][4]:.3f}}}$ & ${coeff_12[0][4]:.3f}^{{+{coeff_12[1][4]:.3f}}}_{{{coeff_12[2][4]:.3f}}}$ & ${coeff_21[0][4]:.3f}^{{+{coeff_21[1][4]:.3f}}}_{{{coeff_21[2][4]:.3f}}}$ & ${coeff_22[0][4]:.3f}^{{+{coeff_22[1][4]:.3f}}}_{{{coeff_22[2][4]:.3f}}}$\\\\
{TABLE_NAMES[7]}  & \\nodata                                                                         & \\nodata                                                                                        & \\nodata                                                                         & \\nodata                                                                                                       & ${coeff_01[0][5]:.3f}^{{+{coeff_01[1][5]:.3f}}}_{{{coeff_01[2][5]:.3f}}}$ & ${coeff_02[0][5]:.3f}^{{+{coeff_02[1][5]:.3f}}}_{{{coeff_02[2][5]:.3f}}}$ & ${coeff_11[0][5]:.3f}^{{+{coeff_11[1][5]:.3f}}}_{{{coeff_11[2][5]:.3f}}}$ & ${coeff_12[0][5]:.3f}^{{+{coeff_12[1][5]:.3f}}}_{{{coeff_12[2][5]:.3f}}}$ & ${coeff_21[0][5]:.3f}^{{+{coeff_21[1][5]:.3f}}}_{{{coeff_21[2][5]:.3f}}}$ & ${coeff_22[0][5]:.3f}^{{+{coeff_22[1][5]:.3f}}}_{{{coeff_22[2][5]:.3f}}}$\\\\
{TABLE_NAMES[8]}  & \\nodata                                                                         & \\nodata                                                                                        & \\nodata                                                                         & \\nodata                                                                                                       & ${coeff_01[0][6]:.3f}^{{+{coeff_01[1][6]:.3f}}}_{{{coeff_01[2][6]:.3f}}}$ & ${coeff_02[0][6]:.3f}^{{+{coeff_02[1][6]:.3f}}}_{{{coeff_02[2][6]:.3f}}}$ & ${coeff_11[0][6]:.3f}^{{+{coeff_11[1][6]:.3f}}}_{{{coeff_11[2][6]:.3f}}}$ & ${coeff_12[0][6]:.3f}^{{+{coeff_12[1][6]:.3f}}}_{{{coeff_12[2][6]:.3f}}}$ & ${coeff_21[0][6]:.3f}^{{+{coeff_21[1][6]:.3f}}}_{{{coeff_21[2][6]:.3f}}}$ & ${coeff_22[0][6]:.3f}^{{+{coeff_22[1][6]:.3f}}}_{{{coeff_22[2][6]:.3f}}}$\\\\
{TABLE_NAMES[9]}  & ${coeff_salt[0][2]:.2f}^{{+{coeff_salt[1][2]:.2f}}}_{{{coeff_salt[2][2]:.2f}}}$  & ${coeff_snemo2_02[0][2]:.3f}^{{+{coeff_snemo2_02[1][2]:.3f}}}_{{{coeff_snemo2_02[2][2]:.3f}}}$  & ${coeff_snemo2_12[0][2]:.3f}^{{+{coeff_snemo2_12[1][2]:.3f}}}_{{{coeff_snemo2_12[2][2]:.3f}}}$  & ${coeff_snemo2_22[0][2]:.3f}^{{+{coeff_snemo2_22[1][2]:.3f}}}_{{{coeff_snemo2_22[2][2]:.3f}}}$  & ${coeff_01[0][7]:.3f}^{{+{coeff_01[1][7]:.3f}}}_{{{coeff_01[2][7]:.3f}}}$ & ${coeff_02[0][7]:.3f}^{{+{coeff_02[1][7]:.3f}}}_{{{coeff_02[2][7]:.3f}}}$ & ${coeff_11[0][7]:.3f}^{{+{coeff_11[1][7]:.3f}}}_{{{coeff_11[2][7]:.3f}}}$ & ${coeff_12[0][7]:.3f}^{{+{coeff_12[1][7]:.3f}}}_{{{coeff_12[2][7]:.3f}}}$ & ${coeff_21[0][7]:.3f}^{{+{coeff_21[1][7]:.3f}}}_{{{coeff_21[2][7]:.3f}}}$ & ${coeff_22[0][7]:.3f}^{{+{coeff_22[1][7]:.3f}}}_{{{coeff_22[2][7]:.3f}}}$\\\\
'''
OUT_ROW = f'''No. of outliers & {outl_frac_salt} & {outl_frac_snemo2_02} & {outl_frac_snemo2_12} & {outl_frac_snemo2_22} & {outl_frac_01} & {outl_frac_02} & {outl_frac_11} & {outl_frac_12} & {outl_frac_21} & {outl_frac_22}\\\\
'''
TABLE_ROW += OUT_ROW
# A column for each number. Using an older version of table_data()
# TABLE_ROW = f'''
# {TABLE_NAMES[0]} & ${MB_01[1]:.1f}$ & ${MB_01[2] - MB_01[1]:.2}$ & ${MB_01[1] - MB_01[0]:.2}$ & ${MB_02[1]:.1f}$ & ${MB_02[2] - MB_02[1]:.2}$ & ${MB_02[1] - MB_02[0]:.2}$ & ${MB_11[1]:.1f}$ & ${MB_11[2] - MB_11[1]:.2}$ & ${MB_11[1] - MB_11[0]:.2}$ & ${MB_12[1]:.1f}$ & ${MB_12[2] - MB_12[1]:.2}$ & ${MB_12[1] - MB_12[0]:.2}$ & \\nodata & ${MB_22[1]:.1f}$ & ${MB_22[2] - MB_22[1]:.2}$ & ${MB_22[1] - MB_22[0]:.2}$\\\\
# {TABLE_NAMES[1]} & ${sigma_int_01[1]:.2f}$ & ${sigma_int_01[2] - sigma_int_01[1]:.2f}$ & ${sigma_int_01[1] - sigma_int_01[0]:.2f}$ & ${sigma_int_02[1]:.2f}$ & ${sigma_int_02[2] - sigma_int_02[1]:.2f}$ & ${sigma_int_02[1] - sigma_int_02[0]:.2f}$ & ${sigma_int_11[1]:.2f}$ & ${sigma_int_11[2] - sigma_int_11[1]:.2f}$ & ${sigma_int_11[1] - sigma_int_11[0]:.2f}$ & ${sigma_int_12[1]:.2f}$ & ${sigma_int_12[2] - sigma_int_12[1]:.2f}$ & ${sigma_int_12[1] - sigma_int_12[0]:.2f}$ & \\nodata & ${sigma_int_22[1]:.2f}$ & ${sigma_int_22[2] - sigma_int_22[1]:.2f}$ & ${sigma_int_22[1] - sigma_int_22[0]:.2f}$\\\\
# {TABLE_NAMES[2]} & ${coeff_01[1][0]:.3f}$ & ${coeff_01[2][0] - coeff_01[1][0]:.3f}$ & ${coeff_01[1][0] - coeff_01[0][0]:.3f}$ & ${coeff_02[1][0]:.3f}$ & ${coeff_02[2][0] - coeff_02[1][0]:.3f}$ & ${coeff_02[1][0] - coeff_02[0][0]:.3f}$ & ${coeff_11[1][0]:.3f}$ & ${coeff_11[2][0] - coeff_11[1][0]:.3f}$ & ${coeff_11[1][0] - coeff_11[0][0]:.3f}$ & ${coeff_12[1][0]:.3f}$ & ${coeff_12[2][0] - coeff_12[1][0]:.3f}$ & ${coeff_12[1][0] - coeff_12[0][0]:.3f}$ & \\nodata & ${coeff_22[1][0]:.3f}$ & ${coeff_22[2][0] - coeff_22[1][0]:.3f}$ & ${coeff_22[1][0] - coeff_22[0][0]:.3f}$\\\\
# {TABLE_NAMES[3]} & ${coeff_01[1][1]:.3f}$ & ${coeff_01[2][1] - coeff_01[1][1]:.3f}$ & ${coeff_01[1][1] - coeff_01[0][1]:.3f}$ & ${coeff_02[1][1]:.3f}$ & ${coeff_02[2][1] - coeff_02[1][1]:.3f}$ & ${coeff_02[1][1] - coeff_02[0][1]:.3f}$ & ${coeff_11[1][1]:.3f}$ & ${coeff_11[2][1] - coeff_11[1][1]:.3f}$ & ${coeff_11[1][1] - coeff_11[0][1]:.3f}$ & ${coeff_12[1][1]:.3f}$ & ${coeff_12[2][1] - coeff_12[1][1]:.3f}$ & ${coeff_12[1][0] - coeff_12[0][1]:.3f}$ & \\nodata & ${coeff_22[1][1]:.3f}$ & ${coeff_22[2][1] - coeff_22[1][1]:.3f}$ & ${coeff_22[1][1] - coeff_22[0][1]:.3f}$\\\\
# {TABLE_NAMES[4]} & ${coeff_01[1][2]:.3f}$ & ${coeff_01[2][2] - coeff_01[1][2]:.3f}$ & ${coeff_01[1][2] - coeff_01[0][2]:.3f}$ & ${coeff_02[1][2]:.3f}$ & ${coeff_02[2][2] - coeff_02[1][2]:.3f}$ & ${coeff_02[1][2] - coeff_02[0][2]:.3f}$ & ${coeff_11[1][2]:.3f}$ & ${coeff_11[2][2] - coeff_11[1][2]:.3f}$ & ${coeff_11[1][2] - coeff_11[0][2]:.3f}$ & ${coeff_12[1][2]:.3f}$ & ${coeff_12[2][2] - coeff_12[1][2]:.3f}$ & ${coeff_12[1][0] - coeff_12[0][2]:.3f}$ & \\nodata & ${coeff_22[1][2]:.3f}$ & ${coeff_22[2][2] - coeff_22[1][2]:.3f}$ & ${coeff_22[1][2] - coeff_22[0][2]:.3f}$\\\\
# {TABLE_NAMES[5]} & ${coeff_01[1][3]:.3f}$ & ${coeff_01[2][3] - coeff_01[1][3]:.3f}$ & ${coeff_01[1][3] - coeff_01[0][3]:.3f}$ & ${coeff_02[1][3]:.3f}$ & ${coeff_02[2][3] - coeff_02[1][3]:.3f}$ & ${coeff_02[1][3] - coeff_02[0][3]:.3f}$ & ${coeff_11[1][3]:.3f}$ & ${coeff_11[2][3] - coeff_11[1][3]:.3f}$ & ${coeff_11[1][3] - coeff_11[0][3]:.3f}$ & ${coeff_12[1][3]:.3f}$ & ${coeff_12[2][3] - coeff_12[1][3]:.3f}$ & ${coeff_12[1][0] - coeff_12[0][3]:.3f}$ & \\nodata & ${coeff_22[1][3]:.3f}$ & ${coeff_22[2][3] - coeff_22[1][3]:.3f}$ & ${coeff_22[1][3] - coeff_22[0][3]:.3f}$\\\\
# {TABLE_NAMES[6]} & ${coeff_01[1][4]:.3f}$ & ${coeff_01[2][4] - coeff_01[1][4]:.3f}$ & ${coeff_01[1][4] - coeff_01[0][4]:.3f}$ & ${coeff_02[1][4]:.3f}$ & ${coeff_02[2][4] - coeff_02[1][4]:.3f}$ & ${coeff_02[1][4] - coeff_02[0][4]:.3f}$ & ${coeff_11[1][4]:.3f}$ & ${coeff_11[2][4] - coeff_11[1][4]:.3f}$ & ${coeff_11[1][4] - coeff_11[0][4]:.3f}$ & ${coeff_12[1][4]:.3f}$ & ${coeff_12[2][4] - coeff_12[1][4]:.3f}$ & ${coeff_12[1][0] - coeff_12[0][4]:.3f}$ & \\nodata & ${coeff_22[1][4]:.3f}$ & ${coeff_22[2][4] - coeff_22[1][4]:.3f}$ & ${coeff_22[1][4] - coeff_22[0][4]:.3f}$\\\\
# {TABLE_NAMES[7]} & ${coeff_01[1][5]:.3f}$ & ${coeff_01[2][5] - coeff_01[1][5]:.3f}$ & ${coeff_01[1][5] - coeff_01[0][5]:.3f}$ & ${coeff_02[1][5]:.3f}$ & ${coeff_02[2][5] - coeff_02[1][5]:.3f}$ & ${coeff_02[1][5] - coeff_02[0][5]:.3f}$ & ${coeff_11[1][5]:.3f}$ & ${coeff_11[2][5] - coeff_11[1][5]:.3f}$ & ${coeff_11[1][5] - coeff_11[0][5]:.3f}$ & ${coeff_12[1][5]:.3f}$ & ${coeff_12[2][5] - coeff_12[1][5]:.3f}$ & ${coeff_12[1][0] - coeff_12[0][5]:.3f}$ & \\nodata & ${coeff_22[1][5]:.3f}$ & ${coeff_22[2][5] - coeff_22[1][5]:.3f}$ & ${coeff_22[1][5] - coeff_22[0][5]:.3f}$\\\\
# {TABLE_NAMES[8]} & ${coeff_01[1][6]:.3f}$ & ${coeff_01[2][6] - coeff_01[1][6]:.3f}$ & ${coeff_01[1][6] - coeff_01[0][6]:.3f}$ & ${coeff_02[1][6]:.3f}$ & ${coeff_02[2][6] - coeff_02[1][6]:.3f}$ & ${coeff_02[1][6] - coeff_02[0][6]:.3f}$ & ${coeff_11[1][6]:.3f}$ & ${coeff_11[2][6] - coeff_11[1][6]:.3f}$ & ${coeff_11[1][6] - coeff_11[0][6]:.3f}$ & ${coeff_12[1][6]:.3f}$ & ${coeff_12[2][6] - coeff_12[1][6]:.3f}$ & ${coeff_12[1][0] - coeff_12[0][6]:.3f}$ & \\nodata & ${coeff_22[1][6]:.3f}$ & ${coeff_22[2][6] - coeff_22[1][6]:.3f}$ & ${coeff_22[1][6] - coeff_22[0][6]:.3f}$\\\\
# {TABLE_NAMES[9]} & ${coeff_01[1][7]:.3f}$ & ${coeff_01[2][7] - coeff_01[1][7]:.3f}$ & ${coeff_01[1][7] - coeff_01[0][7]:.3f}$ & ${coeff_02[1][7]:.3f}$ & ${coeff_02[2][7] - coeff_02[1][7]:.3f}$ & ${coeff_02[1][7] - coeff_02[0][7]:.3f}$ & ${coeff_11[1][7]:.3f}$ & ${coeff_11[2][7] - coeff_11[1][7]:.3f}$ & ${coeff_11[1][7] - coeff_11[0][7]:.3f}$ & ${coeff_12[1][7]:.3f}$ & ${coeff_12[2][7] - coeff_12[1][7]:.3f}$ & ${coeff_12[1][0] - coeff_12[0][7]:.3f}$ & \\nodata & ${coeff_22[1][7]:.3f}$ & ${coeff_22[2][7] - coeff_22[1][7]:.3f}$ & ${coeff_22[1][7] - coeff_22[0][7]:.3f}$\\\\
# {TABLE_NAMES[10]} & ${outl_frac_01[1]:.3f}$ & ${outl_frac_01[2] - outl_frac_01[1]:.3f}$ & ${outl_frac_01[1] - outl_frac_01[0]:.3f}$ & ${outl_frac_02[1]:.3f}$ & ${outl_frac_02[2] - outl_frac_02[1]:.3f}$ & ${outl_frac_02[1] - outl_frac_02[0]:.3f}$ & ${outl_frac_11[1]:.3f}$ & ${outl_frac_11[2] - outl_frac_11[1]:.3f}$ & ${outl_frac_11[1] - outl_frac_11[0]:.3f}$ & ${outl_frac_12[1]:.3f}$ & ${outl_frac_12[2] - outl_frac_12[1]:.3f}$ & ${outl_frac_12[1] - outl_frac_12[0]:.3f}$ & \\nodata & ${outl_frac_22[1]:.3f}$ & ${outl_frac_22[2] - outl_frac_22[1]:.3f}$ & ${outl_frac_22[1] - outl_frac_22[0]:.3f}$\\\\
# '''

with open('results_tab.tex', 'w') as f:
    print(r"""\begin{deluxetable*}{c||c||ccc||cc|cc|cc}[t]
\tablecolumns{11}
\rotate
% \tabletypesize{\large}   %1 size larger
\tabletypesize{\footnotesize}  %1 size smaller
\tablewidth{0pt}
\tablecaption{Parameter estimation results from \unity.\label{tab:results}} %really a title
\tablehead{
    \colhead{} &
    \colhead{\salt} &
    \multicolumn{3}{c}{\snemotwo} & 
    \multicolumn{6}{c}{\snemoseven}
    \\ 
    \cline{4-4} \cline{7-10}
    \colhead{\% Error Model}
    & \colhead{} &
    \colhead{0} & \colhead{1} & \colhead{2} &
    \colhead{0}  & \colhead{0}
    &
    \colhead{1} & \colhead{1}
    & 
    \colhead{2} & \colhead{2}
    \\ 
    \colhead{$\sigma_i \leq$}
    & \colhead{} &
    \colhead{2} & \colhead{2} & \colhead{2} &
    \colhead{1} &  \colhead{2}
    &
    \colhead{1} &  \colhead{2} 
    & 
    \colhead{1}  & \colhead{2}
    }
\startdata""", file=f, end='')
    print(TABLE_ROW, file=f, end='')
    print(r"""\enddata
\tablecomments{The \sn used in the \salt analysis are the ones that passed the $\sigma_i \leq 2$ for \snemoseven with no error model. The ``No. of outliers'' is reported both as an absolute number and a percent of the data set.}
\end{deluxetable*}""", file=f)

print(TABLE_ROW)


##########################################################################
# If I read in the Stan output file, this is not the correct percentiles
# This also as a reference for needing to read any fixed width data file
##########################################################################

# import pandas as pd

# # Ignore Stan's header, since it does not label the variable names.
# # Pandas is not ok with the data having a different length than the header row.
# # data = pd.read_csv('pub_snemo7_mcmc_jla+csp+foundation_02_err_lt2_results.txt',
#                 # delim_whitespace=True, header=None, skiprows=5, skipfooter=5,
#                 # engine='python',    # cause `skipfooter` needs this.
#                 # names=['name', 'mean', 'se_mean', 'sd', '2.5%', '25%', '50%', '75%', '97.5%', 'n_eff', 'Rhat'],
#                 # index_col='name',
#                 # # make sure the columns we care about are the correct types
#                 # dtype={'mean': float, '2.5%': float, '97.5%': float}
#                 # )
# data = pd.read_fwf('pub_snemo7_mcmc_jla+csp+foundation_02_err_lt2_results.txt',
#                    widths=[23, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7], # infer_nrows=500,
#                    skiprows=5, skipfooter=5,
#                    names=['name', 'mean', 'se_mean', 'sd', '2.5%', '25%', '50%', '75%', '97.5%', 'n_eff', 'Rhat'],
#                    index_col='name')

# print(data.shape) #(1109, 11)
# print(data.head())
# print(data.iloc[-1])
# print(data.columns)

# # Get only the parameters we want
# data = data.loc[STAN_PARAMS, ['mean', '2.5%', '97.5%']]
# print(data)

# # Calculate the columns we want: mean, +(97.5% - mean), -(mean - 2.5%)
# data['pos_uncert'] = data['97.5%'] - data['mean']
# print(data)

# data['neg_uncert'] = data['mean'] - data['2.5%']

# print(data[['mean', 'pos_uncert', 'neg_uncert']])

# TABLE =f'''
# {TABLE_NAMES[0]}  & & & & & & {data.loc[STAN_PARAMS[0], 'mean']:.3}^{{{+data.loc[STAN_PARAMS[0], 'pos_uncert']:.2}}}_{{{-data.loc[STAN_PARAMS[0], 'neg_uncert']:.2}}}\\\\
# {TABLE_NAMES[1]}  & & & & & & {data.loc[STAN_PARAMS[1], 'mean']:.2}^{{{+data.loc[STAN_PARAMS[1], 'pos_uncert']:.2}}}_{{{-data.loc[STAN_PARAMS[1], 'neg_uncert']:.2}}}\\\\
# {TABLE_NAMES[2]}  & & & & & & {data.loc[STAN_PARAMS[2], 'mean']:.2}^{{{+data.loc[STAN_PARAMS[2], 'pos_uncert']:.2}}}_{{{-data.loc[STAN_PARAMS[2], 'neg_uncert']:.2}}}\\\\
# {TABLE_NAMES[3]}  & & & & & & {data.loc[STAN_PARAMS[3], 'mean']:.2}^{{{+data.loc[STAN_PARAMS[3], 'pos_uncert']:.2}}}_{{{-data.loc[STAN_PARAMS[3], 'neg_uncert']:.2}}}\\\\
# {TABLE_NAMES[4]}  & & & & & & {data.loc[STAN_PARAMS[4], 'mean']:.2}^{{{+data.loc[STAN_PARAMS[4], 'pos_uncert']:.2}}}_{{{-data.loc[STAN_PARAMS[4], 'neg_uncert']:.2}}}\\\\
# {TABLE_NAMES[5]}  & & & & & & {data.loc[STAN_PARAMS[5], 'mean']:.2}^{{{+data.loc[STAN_PARAMS[5], 'pos_uncert']:.2}}}_{{{-data.loc[STAN_PARAMS[5], 'neg_uncert']:.2}}}\\\\
# {TABLE_NAMES[6]}  & & & & & & {data.loc[STAN_PARAMS[6], 'mean']:.2}^{{{+data.loc[STAN_PARAMS[6], 'pos_uncert']:.2}}}_{{{-data.loc[STAN_PARAMS[6], 'neg_uncert']:.2}}}\\\\
# {TABLE_NAMES[7]}  & & & & & & {data.loc[STAN_PARAMS[7], 'mean']:.2}^{{{+data.loc[STAN_PARAMS[7], 'pos_uncert']:.2}}}_{{{-data.loc[STAN_PARAMS[7], 'neg_uncert']:.2}}}\\\\
# {TABLE_NAMES[8]}  & & & & & & {data.loc[STAN_PARAMS[8], 'mean']:.2}^{{{+data.loc[STAN_PARAMS[8], 'pos_uncert']:.2}}}_{{{-data.loc[STAN_PARAMS[8], 'neg_uncert']:.2}}}\\\\
# {TABLE_NAMES[9]}  & & & & & & {data.loc[STAN_PARAMS[9], 'mean']:.2}^{{{+data.loc[STAN_PARAMS[9], 'pos_uncert']:.2}}}_{{{-data.loc[STAN_PARAMS[9], 'neg_uncert']:.2}}}\\\\
# {TABLE_NAMES[10]} & & & & & & {data.loc[STAN_PARAMS[10], 'mean']:.2}^{{{+data.loc[STAN_PARAMS[10], 'pos_uncert']:.2}}}_{{{-data.loc[STAN_PARAMS[10], 'neg_uncert']:.2}}}\\\\
# '''
# print(TABLE)
