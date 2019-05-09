## Commands for Rose, Rubin, Dixon, et al. 2019 UNITY analysis of SNEMO
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


snemo-data-cut: snemo7_00_err_lt1.0.pkl snemo7_00_err_lt2.0.pkl snemo7_01_err_lt1.0.pkl snemo7_01_err_lt2.0.pkl snemo7_02_err_lt1.0.pkl snemo7_02_err_lt2.0.pkl salt2_00_passed_snemo7_02.pkl ## Cut the raw data for different c_i values

snemo7_00_err_lt1.0.pkl: snemo7_00.pkl cut_JLA.py
	python cut_JLA.py $< 1
snemo7_00_err_lt2.0.pkl: snemo7_00.pkl cut_JLA.py
	python cut_JLA.py $< 2

snemo7_01_err_lt1.0.pkl: snemo7_01.pkl cut_JLA.py
	python cut_JLA.py $< 1
snemo7_01_err_lt2.0.pkl: snemo7_01.pkl cut_JLA.py
	python cut_JLA.py $< 2

snemo7_02_err_lt1.0.pkl: snemo7_02.pkl cut_JLA.py
	python cut_JLA.py $< 1
snemo7_02_err_lt2.0.pkl: snemo7_02.pkl cut_JLA.py
	python cut_JLA.py $< 2

salt2_00_passed_snemo7_02.pkl: salt2_00.pkl snemo7_00_err_lt2.0.txt cut_salt.py
	python cut_salt.py salt2_00.pkl


# Does not use all 8 cores, but runs 4 chains at a time
# Will rerun all models, not just the updated files
snemo-run: snemo7_00_err_lt1.0_fitparams.gzip.pkl snemo7_00_err_lt2.0_fitparams.gzip.pkl snemo7_01_err_lt1.0_fitparams.gzip.pkl snemo7_01_err_lt2.0_fitparams.gzip.pkl snemo7_02_err_lt1.0_fitparams.gzip.pkl snemo7_02_err_lt2.0_fitparams.gzip.pkl salt2_00_passed_snemo7_02_fitparams.gzip.pkl ## Runs UNITY on Rose, Rubin, et. al. 2019 data.

snemo7_00_err_lt1.0_fitparams.gzip.pkl: snemo7_00_err_lt1.0.pkl
	unity run --chains=4 --steps=5000 $<
snemo7_00_err_lt2.0_fitparams.gzip.pkl: snemo7_00_err_lt2.0.pkl
	unity run --chains=4 --steps=5000 $<

snemo7_01_err_lt1.0_fitparams.gzip.pkl: snemo7_01_err_lt1.0.pkl
	unity run --chains=4 --steps=5000 $<
snemo7_01_err_lt2.0_fitparams.gzip.pkl: snemo7_01_err_lt2.0.pkl
	unity run --chains=4 --steps=5000 $<

snemo7_02_err_lt1.0_fitparams.gzip.pkl: snemo7_02_err_lt1.0.pkl
	unity run --chains=4 --steps=5000 $<
snemo7_02_err_lt2.0_fitparams.gzip.pkl: snemo7_02_err_lt2.0.pkl
	unity run --chains=4 --steps=5000 $<

salt2_00_passed_snemo7_02_fitparams.gzip.pkl: salt2_00_passed_snemo7_02.pkl
	unity run --chains=4 --steps=5000 $<


snemo-paper: FIG_JLA_error_floor_0-2_sigma2.pdf FIG_JLA_error_floor_1_sigma1-2.pdf salt2_00_passed_snemo7_02_fitparams.pdf results_tab.tex## Rebuild the figures and tables used in Rose, Rubin, Dixon, et al. 2019.
# remake table
# 	python stan2latex.py

# remake & rename figures
FIG_JLA_error_floor_0-2_sigma2.pdf: snemo7_02_err_lt2.0_fitparams.gzip.pkl snemo7_01_err_lt2.0_fitparams.gzip.pkl snemo7_00_err_lt2.0_fitparams.gzip.pkl
	unity plot snemo7_02_err_lt2.0_fitparams.gzip.pkl snemo7_01_err_lt2.0_fitparams.gzip.pkl snemo7_00_err_lt2.0_fitparams.gzip.pkl
	mv 'snemo7_02_err_lt2.0_fitparams_and_others.pdf' 'FIG_JLA_error_floor_0-2_sigma2.pdf'

FIG_JLA_error_floor_1_sigma1-2.pdf: snemo7_02_err_lt2.0_fitparams.gzip.pkl snemo7_01_err_lt2.0_fitparams.gzip.pkl snemo7_00_err_lt2.0_fitparams.gzip.pkl
	unity plot snemo7_01_err_lt2.0_fitparams.gzip.pkl snemo7_01_err_lt1.0_fitparams.gzip.pkl
	mv 'snemo7_01_err_lt2.0_fitparams_and_others.pdf' 'FIG_JLA_error_floor_1_sigma1-2.pdf'

salt2_00_passed_snemo7_02_fitparams.pdf: salt2_00_passed_snemo7_02_fitparams.gzip.pkl
	unity plot --params=salt+m salt2_00_passed_snemo7_02_fitparams.gzip.pkl

# does not, currently need an update to salt2_00_passed_snemo7_02_fitparams.gzip.pkl
results_tab.tex: stan2latex.py snemo-run
	python stan2latex.py

snemo-upload:  ## Copy some of the files to Rose, Rubin, Dixon, et al. 2019 dropbox folder.
	cp FIG_JLA_error_floor_0-2_sigma2.pdf ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/FIG_JLA_error_floor_0-2_sigma2.pdf
	cp FIG_JLA_error_floor_1_sigma1-2.pdf ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/FIG_JLA_error_floor_1_sigma1-2.pdf
	cp salt2_00_passed_snemo7_02_fitparams.pdf ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/salt2_00_passed_snemo7_02_fitparams.pdf
	cp results_tab.tex ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/results_tab.tex

snemo-run-all: snemo-data-cut snemo-run snemo-paper snemo-upload  ## A full rerun of the snemo analysis: snemo-*


clean-cut: ## Removes the quality cut files
	rm mw_dered_mcmc_jla+csp+ps_snemo7_0?_err_lt?.0.txt
	rm mw_dered_mcmc_jla+csp+ps_snemo7_0?_err_lt?.0.pkl

clean-run: ## Removes the UNITY result files
	@echo "clean-run is not implimented yet"

clean: clean-cut ## Removes ALL unity created files

.PHONY: snemo-data-cut snemo-run snemo-paper snemo-upload snemo-run-all clean


# https://stackoverflow.com/questions/816370/how-do-you-force-a-makefile-to-rebuild-a-target
help:  ## Displays this message.
	@echo "Use -j2 to run two commands (likely two four chain UNITY fits) at once."
	@echo "Use -B or --always-make to force a all depdance to rerun."
#	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'
.PHONY: help