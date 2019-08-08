## Commands redoing the Rose, Dixon, Rubin, et al. 2019 UNITY analysis of SNEMO.
## ====================================================================


.DEFAULT_GOAL := help

# snemoRawFiles = mw_dered_mcmc_jla+csp+ps_snemo7_00.pkl \
# mw_dered_mcmc_jla+csp+ps_snemo7_01.pkl \
# mw_dered_mcmc_jla+csp+ps_snemo7_02.pkl
# mw_dered_mcmc_jla+csp+ps_snemo7_03.pkl
# Make it expcisit because I am not sure how to do regular expression like matching and 7 is not too much
# snemoAnalysisFIles = mw_dered_mcmc_jla+csp+ps_snemo7_00_err_lt1.0.pkl \
# mw_dered_mcmc_jla+csp+ps_snemo7_00_err_lt2.0.pkl \
# mw_dered_mcmc_jla+csp+ps_snemo7_01_err_lt1.0.pkl \
# mw_dered_mcmc_jla+csp+ps_snemo7_01_err_lt2.0.pkl \
# mw_dered_mcmc_jla+csp+ps_snemo7_02_err_lt1.0.pkl \
# mw_dered_mcmc_jla+csp+ps_snemo7_02_err_lt2.0.pkl \
# salt2_00_passed_snemo7_02.pkl

init:
	@echo "init is not implimented yet"
# 	poetry update
# 	poetry version prerelease
# 	poetry install
# 	poetry run unity info

data-cut: fixed_snemo7_00_err_lt1.0.pkl fixed_snemo7_00_err_lt2.0.pkl \
fixed_snemo7_01_err_lt1.0.pkl fixed_snemo7_01_err_lt2.0.pkl \
fixed_snemo7_02_err_lt1.0.pkl fixed_snemo7_02_err_lt2.0.pkl \
fixed_snemo2_00_err_lt2.0.pkl fixed_snemo2_01_err_lt2.0.pkl \
fixed_snemo2_02_err_lt2.0.pkl fixed_snemo2_01_err_lt1.0.pkl \
salt2_00_passed_snemo7_02.pkl dataset_tab.tex ## Cut the raw data for different c_i values

fixed_snemo7_00_err_lt1.0.pkl: fixed_snemo7_00.pkl cut_JLA.py
	poetry run python cut_JLA.py $< 1 7
fixed_snemo7_00_err_lt2.0.pkl: fixed_snemo7_00.pkl cut_JLA.py
	poetry run python cut_JLA.py $< 2 7

fixed_snemo7_01_err_lt1.0.pkl: fixed_snemo7_01.pkl cut_JLA.py
	poetry run python cut_JLA.py $< 1 7
fixed_snemo7_01_err_lt2.0.pkl: fixed_snemo7_01.pkl cut_JLA.py
	poetry run python cut_JLA.py $< 2 7

fixed_snemo7_02_err_lt1.0.pkl: fixed_snemo7_02.pkl cut_JLA.py
	poetry run python cut_JLA.py $< 1 7
fixed_snemo7_02_err_lt2.0.pkl: fixed_snemo7_02.pkl cut_JLA.py
	poetry run python cut_JLA.py $< 2 7

fixed_snemo2_00_err_lt2.0.pkl: fixed_snemo2_00.pkl cut_JLA.py
	poetry run python cut_JLA.py $< 2 2
fixed_snemo2_01_err_lt2.0.pkl: fixed_snemo2_01.pkl cut_JLA.py
	poetry run python cut_JLA.py $< 2 2
fixed_snemo2_02_err_lt2.0.pkl: fixed_snemo2_02.pkl cut_JLA.py
	poetry run python cut_JLA.py $< 2 2
fixed_snemo2_01_err_lt1.0.pkl: fixed_snemo2_01.pkl cut_JLA.py
	poetry run python cut_JLA.py $< 1 2

salt2_00_passed_snemo7_02.pkl salt2_00_passed_snemo2_02.pkl: fixed_salt2_00.pkl fixed_snemo7_00_err_lt2.0.pkl fixed_snemo2_00_err_lt2.0.pkl cut_salt.py
	poetry run python cut_salt.py

# updates on get_N_datasets.py and data-cut
dataset_tab.tex: get_N_dataset.py \
fixed_snemo7_00_err_lt1.0.pkl fixed_snemo7_00_err_lt2.0.pkl \
fixed_snemo7_01_err_lt1.0.pkl fixed_snemo7_01_err_lt2.0.pkl \
fixed_snemo7_02_err_lt1.0.pkl fixed_snemo7_02_err_lt2.0.pkl \
fixed_snemo2_00_err_lt2.0.pkl fixed_snemo2_01_err_lt2.0.pkl \
fixed_snemo2_02_err_lt2.0.pkl \
salt2_00_passed_snemo7_02.pkl
	poetry run python get_N_dataset.py


# Does not use all 8 cores, but runs 4 chains/cores at a time
# Will rerun all models, not just the updated files
run: fixed_snemo7_00_err_lt1.0_fitparams.gzip.pkl fixed_snemo7_00_err_lt2.0_fitparams.gzip.pkl \
fixed_snemo7_01_err_lt1.0_fitparams.gzip.pkl fixed_snemo7_01_err_lt2.0_fitparams.gzip.pkl \
fixed_snemo7_02_err_lt1.0_fitparams.gzip.pkl fixed_snemo7_02_err_lt2.0_fitparams.gzip.pkl \
salt2_00_passed_snemo7_02_fitparams.gzip.pkl salt2_00_passed_snemo2_02_fitparams.gzip.pkl \
fixed_snemo2_00_err_lt2.0_fitparams.gzip.pkl fixed_snemo2_01_err_lt2.0_fitparams.gzip.pkl \
fixed_snemo2_02_err_lt2.0_fitparams.gzip.pkl fixed_snemo2_01_err_lt1.0_fitparams.gzip.pkl ## Runs UNITY on data.

nsteps = 20000

fixed_snemo7_00_err_lt1.0_fitparams.gzip.pkl: fixed_snemo7_00_err_lt1.0.pkl
	poetry run unity run --chains=4 --steps=$(nsteps) --model=stan_code_simple_debug.txt $<
fixed_snemo7_00_err_lt2.0_fitparams.gzip.pkl: fixed_snemo7_00_err_lt2.0.pkl
	poetry run unity run --chains=4 --steps=$(nsteps) --model=stan_code_simple_debug.txt $<

fixed_snemo7_01_err_lt1.0_fitparams.gzip.pkl: fixed_snemo7_01_err_lt1.0.pkl
	poetry run unity run --chains=4 --steps=$(nsteps) --model=stan_code_simple_debug.txt $<
fixed_snemo7_01_err_lt2.0_fitparams.gzip.pkl: fixed_snemo7_01_err_lt2.0.pkl
	poetry run unity run --chains=4 --steps=$(nsteps) --model=stan_code_simple_debug.txt $<

fixed_snemo7_02_err_lt1.0_fitparams.gzip.pkl: fixed_snemo7_02_err_lt1.0.pkl
	poetry run unity run --chains=4 --steps=$(nsteps) --model=stan_code_simple_debug.txt $<
fixed_snemo7_02_err_lt2.0_fitparams.gzip.pkl: fixed_snemo7_02_err_lt2.0.pkl
	poetry run unity run --chains=4 --steps=$(nsteps) --model=stan_code_simple_debug.txt $<

salt2_00_passed_snemo7_02_fitparams.gzip.pkl: salt2_00_passed_snemo7_02.pkl
	poetry run unity run --chains=4 --steps=$(nsteps) --model=stan_code_simple_debug.txt $<
salt2_00_passed_snemo2_02_fitparams.gzip.pkl: salt2_00_passed_snemo2_02.pkl
	poetry run unity run --chains=4 --steps=$(nsteps) --model=stan_code_simple_debug.txt $<

# These appear to converge with nsteps = 8000.
fixed_snemo2_00_err_lt2.0_fitparams.gzip.pkl: fixed_snemo2_00_err_lt2.0.pkl
	poetry run unity run --chains=4 --steps=$(nsteps) --model=stan_code_simple_debug.txt $<
fixed_snemo2_01_err_lt2.0_fitparams.gzip.pkl: fixed_snemo2_01_err_lt2.0.pkl
	poetry run unity run --chains=4 --steps=$(nsteps) --model=stan_code_simple_debug.txt $<
fixed_snemo2_02_err_lt2.0_fitparams.gzip.pkl: fixed_snemo2_02_err_lt2.0.pkl
	poetry run unity run --chains=4 --steps=$(nsteps) --model=stan_code_simple_debug.txt $<
fixed_snemo2_01_err_lt1.0_fitparams.gzip.pkl: fixed_snemo2_01_err_lt1.0.pkl
	poetry run unity run --chains=4 --steps=$(nsteps) --model=stan_code_simple_debug.txt $<


paper: FIG_JLA_error_floor_0-2_sigma2.pdf FIG_JLA_error_floor_1_sigma1-2.pdf salt2_00_passed_snemo7_02_fitparams.pdf FIG_SNEMO2_error_floor_0-2_sigma2.pdf salt2_00_passed_snemo2_02_fitparams.pdf results_tab.tex dataset_tab.tex ## Rebuild all the figures and tables.
# remake table
# 	poetry run python stan2latex.py

# remake & rename figures
FIG_JLA_error_floor_0-2_sigma2.pdf: fixed_snemo7_02_err_lt2.0_fitparams.gzip.pkl \
fixed_snemo7_01_err_lt2.0_fitparams.gzip.pkl fixed_snemo7_00_err_lt2.0_fitparams.gzip.pkl
	poetry run unity plot \
		--axlimits='-20.05 -18.95 0.03 0.21 -0.1 2.1 -0.55 0.55 -0.55 0.55 -0.55 0.55 -0.55 0.55 -0.55 0.55 -0.55 0.55 -0.55 0.55' \
		fixed_snemo7_02_err_lt2.0_fitparams.gzip.pkl fixed_snemo7_01_err_lt2.0_fitparams.gzip.pkl \
		fixed_snemo7_00_err_lt2.0_fitparams.gzip.pkl
	mv 'fixed_snemo7_02_err_lt2.0_fitparams_and_others.pdf' 'FIG_JLA_error_floor_0-2_sigma2.pdf'

FIG_JLA_error_floor_1_sigma1-2.pdf: fixed_snemo7_01_err_lt2.0_fitparams.gzip.pkl \
fixed_snemo7_01_err_lt1.0_fitparams.gzip.pkl
	poetry run unity plot \
	--axlimits='-20.05 -18.95 0.03 0.21 -0.1 2.1 -0.55 0.55 -0.55 0.55 -0.55 0.55 -0.55 0.55 -0.55 0.55 -0.55 0.55 -0.55 0.55' \
	fixed_snemo7_01_err_lt2.0_fitparams.gzip.pkl fixed_snemo7_01_err_lt1.0_fitparams.gzip.pkl
	mv 'fixed_snemo7_01_err_lt2.0_fitparams_and_others.pdf' 'FIG_JLA_error_floor_1_sigma1-2.pdf'

salt2_00_passed_snemo7_02_fitparams.pdf: salt2_00_passed_snemo7_02_fitparams.gzip.pkl
	poetry run unity plot --params=salt+m \
		--axlimits='-19.24 -19.15 0.1 0.18 -0.17 -0.085 2.6 3.4 -0.155 0.08' \
		salt2_00_passed_snemo7_02_fitparams.gzip.pkl

salt2_00_passed_snemo2_02_fitparams.pdf: salt2_00_passed_snemo2_02_fitparams.gzip.pkl
	poetry run unity plot --params=salt+m \
		--axlimits='-19.24 -19.15 0.1 0.18 -0.17 -0.085 2.6 3.4 -0.155 0.08' \
		salt2_00_passed_snemo2_02_fitparams.gzip.pkl

FIG_SNEMO2_error_floor_0-2_sigma2.pdf: fixed_snemo2_02_err_lt2.0_fitparams.gzip.pkl \
fixed_snemo2_01_err_lt2.0_fitparams.gzip.pkl fixed_snemo2_00_err_lt2.0_fitparams.gzip.pkl
	poetry run unity plot --params=snemo2+m \
		--axlimits='-19.51 -19.39 0.06 0.16 0.7 1.1 0.01 0.09 -0.15 0.02' \
		fixed_snemo2_02_err_lt2.0_fitparams.gzip.pkl fixed_snemo2_01_err_lt2.0_fitparams.gzip.pkl \
		fixed_snemo2_00_err_lt2.0_fitparams.gzip.pkl
	mv 'fixed_snemo2_02_err_lt2.0_fitparams_and_others.pdf' 'FIG_SNEMO2_error_floor_0-2_sigma2.pdf'


# updates on stan2latex.py and run
results_tab.tex: stan2latex.py \
fixed_snemo7_00_err_lt1.0_fitparams.gzip.pkl fixed_snemo7_00_err_lt2.0_fitparams.gzip.pkl \
fixed_snemo7_01_err_lt1.0_fitparams.gzip.pkl fixed_snemo7_01_err_lt2.0_fitparams.gzip.pkl \
fixed_snemo7_02_err_lt1.0_fitparams.gzip.pkl fixed_snemo7_02_err_lt2.0_fitparams.gzip.pkl \
salt2_00_passed_snemo7_02_fitparams.gzip.pkl \
fixed_snemo2_00_err_lt2.0_fitparams.gzip.pkl fixed_snemo2_01_err_lt2.0_fitparams.gzip.pkl \
fixed_snemo2_02_err_lt2.0_fitparams.gzip.pkl fixed_snemo2_01_err_lt1.0_fitparams.gzip.pkl
	poetry run python stan2latex.py

upload: paper  ## Copy some of the files to Dropbox folder for Overleaf.
	cp FIG_JLA_error_floor_0-2_sigma2.pdf ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/FIG_JLA_error_floor_0-2_sigma2.pdf
	cp FIG_JLA_error_floor_1_sigma1-2.pdf ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/FIG_JLA_error_floor_1_sigma1-2.pdf
	cp salt2_00_passed_snemo7_02_fitparams.pdf ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/salt2_00_passed_snemo7_02_fitparams.pdf
	cp salt2_00_passed_snemo2_02_fitparams.pdf ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/salt2_00_passed_snemo2_02_fitparams.pdf
	cp FIG_SNEMO2_error_floor_0-2_sigma2.pdf ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/FIG_SNEMO2_error_floor_0-2_sigma2.pdf
	cp results_tab.tex ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/results_tab.tex
	cp dataset_tab.tex ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/dataset_tab.tex


clean-cut:
	@echo "clean-cut is not implimented yet"
# 	rm mw_dered_mcmc_jla+csp+ps_snemo7_0?_err_lt?.0.txt

clean-run:
	@echo "clean-run is not implimented yet"

clean: clean-cut

.PHONY: init data-cut run paper upload clean


# https://stackoverflow.com/questions/816370/how-do-you-force-a-makefile-to-rebuild-a-target
help:  ## Displays this message.
	@echo "Commands for Rose, Dixon, Rubin, et al. 2019 UNITY analysis of SNEMO."
	@echo " "
	@echo "This assumes UNITY is installed via 'poetry update' and 'poertry install'."
	@echo "Check installation via 'poertry run unity'."
	@echo " "
# 	@echo "Use -j4 to run four commands at in parrallel."
	@echo "Use -B or --always-make to force a all depdance to rerun."
	@echo " "
	@echo "When running parallel jobs do not move on till previous step is done:"
	@echo "To (re-)make all on 8 cores, use 'make (-B) -j8 data-cut && make -j8 run && make -j8 paper'."
#	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'
.PHONY: help

# Currently running with python 3.7.2 set by pyenv local (saved as host_unity/.python-version)
# Poetry should be /Users/brose/.poetry/bin/poetry
# FYI, pyenv-virtaulenv was used at somepoint as well, but I am not sure what it is currently responsible for.
# Poetry is using the local virtural enviornment (host_unity/.venv/)
# Can either activate venv ('source .venv/bin/activate') or use 'poetry run' to access and installed unity
#     and its dependancies. It looks like 'poetry run' acts like an editiable install of unity.

debug:
# 	pyenv
# 	pyenv versions
	@echo $(PATH)
	which poetry
	/Users/brose/.poetry/bin/poetry --version
	poetry run unity info
	/Users/brose/.poetry/bin/poetry run unity --help

.PHONY: debug