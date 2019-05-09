# The fitting directory

This directory contains the analysis predominantly done for Rose, Dixon, Rubin et al. 2019.

## Usage

## Naming convention

The lightcurve fits are stored in [UNITY input dictionaries][^1], stored as pickle files on disk. The files are named `{lc-model}_{error-model}.pkl`. Therefore, `snemo7_02.pkl` is data fit with SNEMO7 with a 2% of peak nieve error model applied, and `salt2_00.pkl` is data fit with SALT2.4 and no extra error model beyond what is already incorporated into SALT2.4.

[^1]: Currently the documentation is not online, but found in `../docs/source/docs_input_data.rst`. This file is checked in on [Github](https://github.com/rubind/host_unity/blob/master/docs/source/docs_input_data.rst).