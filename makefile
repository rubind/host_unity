# works on what systems?
# http://makefiletutorial.com/
# https://www.kennethreitz.org/essays/repository-structure-and-python
# https://krzysztofzuraw.com/blog/2016/makefiles-in-python-projects.html
# Self-documenting a makefile, make help: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
# .PHONY tells make that this is a command not a file

.DEFAULT_GOAL := help

init: ## An attempt to automake installion from source
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

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	name '*~' -exec rm --force  {} 

lint: 
	flake8 ./unity ./tests
	mypy .

# test: lint, clean-pyc
test: ## The
	# verbose, more details on xfail, run pytest-cov in unity folder
	pytest -v -rx --cov=unity
	#  pytest -v -rx --cov-config=.coveragerc --cov --runxfail --runslow

snemo-paper:  ## Rebuild the figures and tables used in Rose, Rubin, Dixon, et al. 2019.
# nees to be in the correct vitural enviornment
# remake & rename figures
	unity plot unity/data_jla+/pub_snemo7_mcmc_jla+csp+foundation_02_err_lt2_fitparams.gzip.pkl unity/data_jla+/pub_snemo7_mcmc_jla+csp+foundation_01_err_lt2_fitparams.gzip.pkl unity/data_jla+/pub_snemo7_mcmc_jla+csp+foundation_err_lt2_fitparams.gzip.pkl
	mv '().pdf' 'unity/data_jla+/FIG_JLA_error_floor_0-2_sigma2.pdf'
	unity plot unity/data_jla+/pub_snemo7_mcmc_jla+csp+foundation_01_err_lt2_fitparams.gzip.pkl unity/data_jla+/pub_snemo7_mcmc_jla+csp+foundation_01_err_lt1_fitparams.gzip.pkl
	mv '().pdf' 'unity/data_jla+/FIG_JLA_error_floor_1_sigma1-2.pdf'
# remake table
	python unity/data_jla+/stan2latex.py

upload-snemo:  ## Copy some of the files to Rose, Rubin, Dixon, et al. 2019 dropbox folder.
	cp unity/data_jla+/FIG_JLA_error_floor_0-2_sigma2.pdf ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/FIG_JLA_error_floor_0-2_sigma2.pdf
	cp unity/data_jla+/FIG_JLA_error_floor_1_sigma1-2.pdf ~/Dropbox/Apps/ShareLaTeX/SNEMO\ and\ Unity/FIG_JLA_error_floor_1_sigma1-2.pdf

sako-paper:
	@echo "not implemented"

help:  ## Display this message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'
.PHONY: help

.PHONY: clean, init, init-dev