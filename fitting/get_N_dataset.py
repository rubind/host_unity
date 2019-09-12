"""get_N_dataset.py -- return the number in each data set for a list of SN.
"""

__author__ = 'Benjamin Rose <brose@stsci.edu>'
__python__ = "^3.6"

import pickle
import sys
from pathlib import Path
from collections import Counter

import numpy as np
import toml

prefix = ""
data_files = [prefix + 'snemo7_00_err_lt1.0.txt', prefix + 'snemo7_00_err_lt2.0.txt',
              prefix + 'snemo7_01_err_lt1.0.txt', prefix + 'snemo7_01_err_lt2.0.txt',
              prefix + 'snemo7_02_err_lt1.0.txt', prefix + 'snemo7_02_err_lt2.0.txt',
              prefix + 'snemo2_00_err_lt2.0.txt', prefix + 'snemo2_01_err_lt2.0.txt',
              prefix + 'snemo2_02_err_lt2.0.txt']


def get_N_dataset(meta_data, print_result=False):
    """ From a given pkl file, give the number of SN from JLA, CSP and Foundation.

    This function assumes the work flow used in Rose, Dixon, et al.
    2019. The full data sets, with all the correct values, are stored in
    :file:`snemo7_00.pkl`. :file:`snemo7_01.pkl` and
    :file:`snemo7_02.pkl` would also work. The analysis is done on data 
    stored in files of the form :file:`snemo7_0?_err_lt?.0.pkl`. This 
    function takes the SN names from these data files, and checks the
    original data file to find the original SN data set.

    Arguments
    ---------
    SN (str):
        Name of the data set used by UNITY, of the form 
        :file:`snemo7_0?_err_lt?.0.pkl`. Needs to work as an argument to
        python's :command:`open` command.
    print_result (bool):
        Function always returns result, but can optional print out the
        number of SN are from each data set.

    Returns
    -------
    tuple:
        A tuple, of length 3, with the number of SN from JLA, CSP, and
        Foundation.
    """
    # Use an unmodified data file to check `sn_set_inds`.
    # Fits with any error model should work, assuming everything passed correctly.
    data_file = Path(meta_data[:-14]+'.pkl')

    with open(data_file, 'rb') as f:
        all_data = pickle.load(f)

    with open(meta_data, 'r') as f:
        passed_lc_cuts_meta_data = toml.loads(f.read())
    sn_names_passed_lc_cuts = passed_lc_cuts_meta_data['names']

    all_sn_names = all_data['names']
    data_sets_all_data = all_data['sn_set_inds']
    data_sets_counted = Counter(data_sets_all_data)
    # print(np.where(all_sn_names==SN))
    data_sets_of_in_meta = data_sets_all_data[np.isin(all_sn_names, sn_names_passed_lc_cuts)]
    print(len(sn_names_passed_lc_cuts), len(data_sets_of_in_meta), len(data_sets_all_data))
    from_data_set = Counter(data_sets_of_in_meta)
    N_JLA = from_data_set[0] + from_data_set[1] + from_data_set[2] + from_data_set[3]
    #1 - SNLS, 2 - SDSS, 3 - low-z, 4 - Riess HST (this is 1-index)
    N_SDSS = from_data_set[1]
    N_SNLS = from_data_set[0]
    N_LOCAL = from_data_set[2] 
    N_HST = from_data_set[3]
    N_CSP = from_data_set[4]
    N_Foundation = from_data_set[5]

    if print_result:
        print(f"Summary from fits using {meta_data}.")
        print(f"Counts from Nearby: {data_sets_counted[2]}, SDSS: {data_sets_counted[1]}, ",
              f"SNLS: {data_sets_counted[0]}, HST: {data_sets_counted[3]}, ",
              f"CSP: {data_sets_counted[4]}, Foundation: {data_sets_counted[5]}")
        print(f"Number of SN from JLA: {N_JLA}")
        #0 is SNLS (05D2my), 1 (SDSS20227) is SDSS, Nearby (sn2002de) is 2, HST (Eagle) is 3.
        print(f"  sub-JLA, Nearby: {N_LOCAL}")
        print(f"  sub-JLA, SDSS: {N_SDSS}")
        print(f"  sub-JLA, SNLS: {N_SNLS}")
        print(f"  sub-JLA, HST: {N_HST}")
        print(f"Number of SN from CSP: {N_CSP}")
        print(f"Number of SN from Foundation: {N_Foundation}")
        print(f"Local SN: {np.array(sn_names_passed_lc_cuts)[np.isin(data_sets_of_in_meta, 2)]}",
              f"N: {len(np.array(sn_names_passed_lc_cuts)[np.isin(data_sets_of_in_meta, 2)])}")
        print("\n")
    return N_SDSS, N_SNLS, N_LOCAL, N_HST, N_CSP, N_Foundation

N_SDSS_01, N_SNLS_01, N_LOCAL_01, N_HST_01, N_CSP_01, N_Foundation_01 = get_N_dataset(data_files[0], print_result=True)
N_SDSS_02, N_SNLS_02, N_LOCAL_02, N_HST_02, N_CSP_02, N_Foundation_02 = get_N_dataset(data_files[1], print_result=True)
N_SDSS_11, N_SNLS_11, N_LOCAL_11, N_HST_11, N_CSP_11, N_Foundation_11 = get_N_dataset(data_files[2], print_result=True)
N_SDSS_12, N_SNLS_12, N_LOCAL_12, N_HST_12, N_CSP_12, N_Foundation_12 = get_N_dataset(data_files[3], print_result=True)
N_SDSS_21, N_SNLS_21, N_LOCAL_21, N_HST_21, N_CSP_21, N_Foundation_21 = get_N_dataset(data_files[4], print_result=True)
N_SDSS_22, N_SNLS_22, N_LOCAL_22, N_HST_22, N_CSP_22, N_Foundation_22 = get_N_dataset(data_files[5], print_result=True)
N_SDSS_s02, N_SNLS_s02, N_LOCAL_s02, N_HST_s02, N_CSP_s02, N_Foundation_s02 = get_N_dataset(data_files[6], print_result=True)
N_SDSS_s12, N_SNLS_s12, N_LOCAL_s12, N_HST_s12, N_CSP_s12, N_Foundation_s12 = get_N_dataset(data_files[7], print_result=True)
N_SDSS_s22, N_SNLS_s22, N_LOCAL_s22, N_HST_s22, N_CSP_s22, N_Foundation_s22 = get_N_dataset(data_files[8], print_result=True)


# Table_heaer = r'''\begin{table}
# \centering
# \caption{The number of \sn analyzed, for various SNEMO7 light-curve fits and quality cuts.}
# \begin{tabular}{l|ccc|c}
# \hline\hline
# & JLA & CSP & Foundation & Total\\\hline
# Total SNe & 740 & 134 & 223 & 1097\\
# Host mass avail. & 740 & 99 & 98 & 937\\\hline
# \textbf{No Error Model} & & & & \\
# '''
Table_heaer = r'''\begin{deluxetable*}{l|cccccc|c}[t]
\tablecolumns{7}
% \tabletypesize{\large}   %1 size larger
\tabletypesize{\footnotesize}  %1 size smaller
% \tablewidth{0pt}
\tablewidth{3in}
\tablecaption{Number of \sn passing quality cuts from various SNEMO models.\label{tab:LcFitData}} %really a title
\tablehead{
    \colhead{} &
    \colhead{CSP} & \colhead{Foundation} & \colhead{CfA} &
    \colhead{SDSS} & \colhead{SNLS} & \colhead{HST} &
    \colhead{Total}
    }
\startdata
Total SNe & 134 & 223 & 97 & 371 & 239 & 9 & 1097\\
Host mass avail. & 99 & 100 & 97 & 371 & 239 & 9 & 937\\
\hline
& & \multicolumn{4}{c}{\hspace{1em}\snemotwo} & & \\
\textbf{No Error Model} & & & & & & \\
''' # Total JLA SNe from jla_lcparams.txt file. SNLS: 239, SDSS: 374, low-z: 118, Riess HST: 9 = 740
# After the removal of all CSP -> SNLS: 239, SDSS: 371, CfA: 97
Table_data = f'''\\hspace{{1em}}$\\sigma_i \\leq 2$ & {N_CSP_s02} &  {N_Foundation_s02} & {N_LOCAL_s02} & {N_SDSS_s02} & {N_SNLS_s02} & {N_HST_s02} & {N_SDSS_s02 + N_SNLS_s02 + N_LOCAL_s02 + N_HST_s02 + N_CSP_s02 + N_Foundation_s02}\\\\
\\textbf{{1\\% Error Model}} & & & & & & \\\\
\\hspace{{1em}}$\\sigma_i \\leq 2$ & {N_CSP_s12} &  {N_Foundation_s12} & {N_LOCAL_s12} & {N_SDSS_s12} & {N_SNLS_s12} & {N_HST_s12} & {N_SDSS_s12 + N_SNLS_s12 + N_LOCAL_s12 + N_HST_s12 + N_CSP_s12 + N_Foundation_s12}\\\\
\\textbf{{2\\% Error Model}} & & & & & & \\\\
\\hspace{{1em}}$\\sigma_i \\leq 2$ & {N_CSP_s22} & {N_Foundation_s22} & {N_LOCAL_s22} & {N_SDSS_s22} & {N_SNLS_s22} & {N_HST_s22} & {N_SDSS_s22 + N_SNLS_s22 + N_LOCAL_s22 + N_HST_s22 + N_CSP_s22 + N_Foundation_s22}\\\\
\\hline
& & \\multicolumn{{4}}{{c}}{{\\hspace{{1em}}\\snemoseven}} & & \\\\
\\textbf{{No Error Model}} & & & & & & \\\\
\\hspace{{1em}}$\\sigma_i \\leq 1$ & {N_CSP_01} &  {N_Foundation_01} & {N_LOCAL_01} & {N_SDSS_01} & {N_SNLS_01} & {N_HST_01} & {N_SDSS_01 + N_SNLS_01 + N_LOCAL_01 + N_HST_01 + N_CSP_01 + N_Foundation_01}\\\\
\\hspace{{1em}}$\\sigma_i \\leq 2$ & {N_CSP_02} &  {N_Foundation_02} & {N_LOCAL_02} & {N_SDSS_02} & {N_SNLS_02} & {N_HST_02} & {N_SDSS_02 + N_SNLS_02 + N_LOCAL_02 + N_HST_02 + N_CSP_02 + N_Foundation_02}\\\\
\\textbf{{1\\% Error Model}} & & & & & & \\\\
\\hspace{{1em}}$\\sigma_i \\leq 1$ & {N_CSP_11} &  {N_Foundation_11} & {N_LOCAL_11} & {N_SDSS_11} & {N_SNLS_11} & {N_HST_11} & {N_SDSS_11 + N_SNLS_11 + N_LOCAL_11 + N_HST_11 + N_CSP_11 + N_Foundation_11}\\\\
\\hspace{{1em}}$\\sigma_i \\leq 2$ & {N_CSP_12} &  {N_Foundation_12} & {N_LOCAL_12} & {N_SDSS_12} & {N_SNLS_12} & {N_HST_12} & {N_SDSS_12 + N_SNLS_12 + N_LOCAL_12 + N_HST_12 + N_CSP_12 + N_Foundation_12}\\\\
\\textbf{{2\\% Error Model}} & & & & & & \\\\
\\hspace{{1em}}$\\sigma_i \\leq 1$ & {N_CSP_21} &  {N_Foundation_21} & {N_LOCAL_21} & {N_SDSS_21} & {N_SNLS_21} & {N_HST_21} & {N_SDSS_21 + N_SNLS_21 + N_LOCAL_21 + N_HST_21 + N_CSP_21 + N_Foundation_21}\\\\
\\hspace{{1em}}$\\sigma_i \\leq 2$ & {N_CSP_22} &  {N_Foundation_22} & {N_LOCAL_22} & {N_SDSS_22} & {N_SNLS_22} & {N_HST_22} & {N_SDSS_22 + N_SNLS_22 + N_LOCAL_22 + N_HST_22 + N_CSP_22 + N_Foundation_22}\\\\
'''
# Table_footer = r'''\hline
# \end{tabular}
# \label{tab:LcFitData}
# \end{table}
# '''
Table_footer = r'''\enddata
% \tablenotetext{1}{$\sigma_i$ is the uncertainty on each fit eigenvector. When $\sigma_i=1$, the uncertainty is approximately the $1\sigma$ dispersion in the population.}
\tablecomments{$\sigma_i$ is the uncertainty on each fit eigenvector. When $\sigma_i=1$, the uncertainty is approximately the $1\sigma$ dispersion in the population. The data from the CfA, SDSS, SNLS, and HST surveys were obtained via the JLA compilation \citep{Betoule2014}.}
\end{deluxetable*}
'''
with open('dataset_tab.tex', 'w') as f:
    print(Table_heaer+Table_data+Table_footer, file=f)
print(Table_heaer+Table_data+Table_footer)