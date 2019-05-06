# Makefile for host UNITY and the papers that use it.
# works on what systems?
# http://makefiletutorial.com/
# https://www.kennethreitz.org/essays/repository-structure-and-python
# https://krzysztofzuraw.com/blog/2016/makefiles-in-python-projects.html
# Self-documenting a makefile, make help: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
# .PHONY tells make that this is a command not a file


# SETUP EVIRONEMNT WITH:
# source .venv/bin/activate

.DEFAULT_GOAL := help

help:  ## Displays this message.
#	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'
.PHONY: help


## Development commands
## ====================

init: ## A failing attempt to automake installion from source.
	pip install -r requirements.txt
	pip install -e .
	conda install python.app

init-dev: init
	pip install -r requirements-dev.txt

init-conda:
	conda env create -f requirements.yml python=3.7

# init-conda-dev:
# 	conda env create unity-dev python=3.7
# 	conda install --name unity-dev --file requirements.yml
#   conda install --name unity-dev --file requirements-dev.yml

lint: 
	flake8 ./unity ./tests
	mypy .

# test: lint clean-pyc
test: ## Run the full test suite with code coverage
# verbose, more details on xfail, run pytest-cov via config settings
	pytest -v -rx --cov-config=.coveragerc --cov

.PHONY: init lint test




# ## Commands for Rose, Rubin, Dixon, et al. 2019 UNITY analysis of SNEMO
# ## ====================================================================

# snemoRawFiles = fitting/mw_dered_mcmc_jla+csp+ps_snemo7_00.pkl \
# fitting/mw_dered_mcmc_jla+csp+ps_snemo7_01.pkl \
# fitting/mw_dered_mcmc_jla+csp+ps_snemo7_02.pkl
# # fitting/mw_dered_mcmc_jla+csp+ps_snemo7_03.pkl

# # snemo-data-cut: $(snemoAnalysisFIles) ## Cut the raw data for different c_i values, requires GNU Make
# snemo-data-cut: $(snemoRawFiles) ## Cut the raw data for different c_i values, requires GNU Make
# 	$(foreach f,$^, python fitting/cut_JLA.py $(f) 1;)
# 	$(foreach f,$^, python fitting/cut_JLA.py $(f) 2;)


# snemoAnalysisFIles = fitting/mw_dered_mcmc_jla+csp+ps_snemo7_00_err_lt1.0.pkl \
# fitting/mw_dered_mcmc_jla+csp+ps_snemo7_00_err_lt2.0.pkl \
# fitting/mw_dered_mcmc_jla+csp+ps_snemo7_01_err_lt1.0.pkl \
# fitting/mw_dered_mcmc_jla+csp+ps_snemo7_01_err_lt2.0.pkl \
# fitting/mw_dered_mcmc_jla+csp+ps_snemo7_02_err_lt1.0.pkl \
# fitting/mw_dered_mcmc_jla+csp+ps_snemo7_02_err_lt2.0.pkl

# # Does not use all 8 cores, but runs 4 chains at a time
# # Will rerun all models, not just the updated files
# snemo-run: $(snemoAnalysisFIles) ## Runs UNITY on Rose, Rubin, et. al. 2019 data.
# 	$(foreach f,$^. unity run --chains=4 --steps=5000 $(f);)

# snemo-paper:  ## Rebuild the figures and tables used in Rose, Rubin, Dixon, et al. 2019.
# # nees to be in the correct vitural enviornment
# # remake & rename figures
# 	unity plot unity/data_jla+/pub_snemo7_mcmc_jla+csp+foundation_02_err_lt2_fitparams.gzip.pkl unity/data_jla+/pub_snemo7_mcmc_jla+csp+foundation_01_err_lt2_fitparams.gzip.pkl unity/data_jla+/pub_snemo7_mcmc_jla+csp+foundation_err_lt2_fitparams.gzip.pkl
# 	mv '().pdf' 'unity/data_jla+/FIG_JLA_error_floor_0-2_sigma2.pdf'
# 	unity plot unity/data_jla+/pub_snemo7_mcmc_jla+csp+foundation_01_err_lt2_fitparams.gzip.pkl unity/data_jla+/pub_snemo7_mcmc_jla+csp+foundation_01_err_lt1_fitparams.gzip.pkl
# 	mv '().pdf' 'unity/data_jla+/FIG_JLA_error_floor_1_sigma1-2.pdf'
# 	unity plot fitting/satl2_jla+csp+ps_SNEMO7_02_passed_fitparams.gzip.pkl --params=salt+m
# # remake table
# 	python unity/data_jla+/stan2latex.py

# snemo-upload:  ## Copy some of the files to Rose, Rubin, Dixon, et al. 2019 dropbox folder.
# 	cp unity/data_jla+/FIG_JLA_error_floor_0-2_sigma2.pdf ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/FIG_JLA_error_floor_0-2_sigma2.pdf
# 	cp unity/data_jla+/FIG_JLA_error_floor_1_sigma1-2.pdf ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/FIG_JLA_error_floor_1_sigma1-2.pdf
# 	cp fitting/satl2_jla+csp+ps_SNEMO7_02_passed_fitparams.pdf ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/satl2_jla+csp+ps_SNEMO7_02_passed_fitparams.pdf

# snemo-run-all: snemo-data-cut snemo-run snemo-paper snemo-upload  ## A full rerun of the snemo analysis: snemo-*

# .PHONY: snemo-data-cut snemo-run snemo-paper snemo-upload snemo-run-all







## Commands for Rose & Rubin 2019 UNITY analsysi of Sako SDSS data
## ===============================================================

sako-paper:
	@echo "not implemented"

.PHONY: sako-paper