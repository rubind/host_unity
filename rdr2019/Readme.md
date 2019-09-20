# RDR2019

This directory contains the analysis predominantly done for Rose, Dixon, Rubin et al. 2019.


## Usage

To redo the analysis, run `make` to get instructions on how to use the `makefile`. To redo the data cleaning, look at the documentation inside each [Data Manipulation Scripts](#data-manipulation-scripts).


## Files

In general, the data pickle files are named `{optional prefix}_{lc-model}_{error-model}.pkl`. Therefore, `snemo7_01.pkl` is data fit with SNEMO7 with a 1% of peak nieve error model applied, and `salt2_00.pkl` is data fit with SALT2.4 and no extra error model beyond what is already incorporated into SALT2.4.

### Raw data

* `CSP_lcparams.dat`, `PS_lcparams.dat` - Light curve information
* `gupta_host.txt` - Host galaxy information

### Manipulated data

* `*_??.pkl` - Data, in the format acceptable to UNITY, of light curve fits. These fies have the light curve fitter (salt, snemo2, snemo7) and associated added model certainty percentage (00, 01, 02) in the file names. 
* `*_err_lt?.0.pkl`, `*_err_lt?.0.txt` - **NOT in git**  Input data for UNITY, after quality cuts are applied. A summary of the pickled data is presented in the associated text file.
* `*_fitparams.gzip.pkl`, `*_results.txt` - **NOT in git** The results of the UNITY analysis. A summary of the pickled data is presented in the associated text file.

### Data Manipulation Scripts

* `collect_data.py` - Gathers the results from `mcmc_lc_*_fit.py`, finds associated host galaxy data, and prepares the `{fitter}_{error}.pkl` files for input into UNITY.
* `cut_JLA.py` - Takes `*_00.pkl` files and performs quality cuts (1 or 2) `*_err_lt*.0.pkl` files via `make data-cut`.
* `cut_salt.py` - Similar to `cut_JLA.py` but specifically for the salt2 light curve fits, `20190911_salt2_00.pkl`.
* `get_N_dataset.py` - Creates Table 1 (input data summary), using the information in `*_err_lt?.0.pkl` & `*_err_lt?.0.txt`.
* `make_scripts.py` - Generates a series of scripts to submit LC fitting jobs in an embarrassingly parallel way.
* `makefile` - Contains the scripts to cut data on quality, run UNITY, make the figures/tables for the paper, and upload the needed files to Overleaf. Get help via `make help`.
* * `mcmc_lc_*_fit.py` - Runs the MCMC light-curve fits for LCs in the JLA, CSP, and Foundation subsets; generally called by scripts output from `make_scripts.py`
* `stan2latex.py` - Converts the UNITY output files `*_fitparams.gzip.pkl` (and `*_results.txt`) to two summary tables.

### Final files

* `dataset_tab.tex` - Table 1 of Rose, Dixon, Rubin et al. 2019
* `results_tab_snemo?.tex` - Tables 2 & 3 of Rose, Dixon, Rubin et al. 2019


## Asides

If any of the input files change names or prefixes, you can need to update the `makefile` along with `cut_salt.py`, `get_N_dataset.py`, and `stan2latex.py`

* `chisq_results.ipynb` - A Jupiter notebook for some debugging.