## Commands redoing the Rose, Rubin, Strolger, & Garnavich 2020 UNITY analysis of SDSS.
## ====================================================================

.DEFAULT_GOAL := help

param_sets = mass_local_global.pkl mass_local.pkl mass_global.pkl mass.pkl
unity_sets = $(param_sets:.pkl=_fitparams.gzip.pkl)

clean-data: $(param_sets)  ## Clean and prepare UNITY input data

mass_local_global.pkl mass_local.pkl mass_global.pkl mass.pkl local.pkl global.pkl low_mass_age_only.pkl high_mass_age_only.pkl low_mass.pkl high_mass.pkl: results-summary.csv SDSS_Photometric_SNe_Ia.fits cleandata.py
	poetry run python cleandata.py
# this is missing some options.


# run: mass_local_global_fitparams.gzip.pkl mass_local_fitparams.gzip.pkl mass_global_fitparams.gzip.pkl mass_fitparams.gzip.pkl  ## Rerun UNITY analysis
run: *fitparams.gzip.pkl  ## Rerun UNITY analysis

steps = 40000# UNITY deafult is 1000
chains = 4# UNITY deafult is 4
model = stan_code_simple_debug.txt# Output outlier flags
cores = 4# UNITY deafult is 1, not useful for cores > chains
# poetry run unity run --model=$(model) --chains=$(chains) --steps=$(steps) --max_cores=$(cores) $<
# poetry run unity run --model=stan_code_simple_debug.txt --chains=4 --steps=40000 --max_cores=4

salt_fitparams.gzip.pkl: salt.pkl
	poetry run unity run --model=$(model) --steps=$(steps) --max_cores=$(cores) $<
mass_local_global_fitparams.gzip.pkl: mass_local_global.pkl
	poetry run unity run --model=$(model) --steps=$(steps) --max_cores=$(cores) $<
mass_local_fitparams.gzip.pkl: mass_local.pkl
	poetry run unity run --model=$(model) --steps=$(steps) --max_cores=$(cores) $<
mass_global_fitparams.gzip.pkl: mass_global.pkl
	poetry run unity run --model=$(model) --steps=$(steps) --max_cores=$(cores) $<
local_global_fitparams.gzip.pkl: local_global.pkl
	poetry run unity run --model=$(model) --steps=$(steps) --max_cores=$(cores) $<
mass_fitparams.gzip.pkl: mass.pkl
	poetry run unity run --model=$(model) --steps=$(steps) --max_cores=$(cores) $<
local_fitparams.gzip.pkl: local.pkl
	poetry run unity run --model=$(model) --steps=$(steps) --max_cores=$(cores) $<
global_fitparams.gzip.pkl: global.pkl
	poetry run unity run --model=$(model) --steps=$(steps) --max_cores=$(cores) $<
low_mass_age_only_fitparams.gzip.pkl: low_mass_age_only.pkl
	poetry run unity run --model=$(model) --steps=$(steps) --max_cores=$(cores) $<
high_mass_age_only_fitparams.gzip.pkl: high_mass_age_only.pkl
	poetry run unity run --model=$(model) --steps=$(steps) --max_cores=$(cores) $<
low_mass_fitparams.gzip.pkl: low_mass.pkl
	poetry run unity run --model=$(model) --steps=$(steps) --max_cores=$(cores) $<
high_mass_fitparams.gzip.pkl: high_mass.pkl
	poetry run unity run --model=$(model) --steps=$(steps) --max_cores=$(cores) $<


paper: fig_*.pdf## Make the figures for RRSG 2020

fig_salt.pdf: salt_fitparams.gzip.pkl
	poetry run unity plot $< --params=salt
	mv salt_fitparams.pdf fig_salt.pdf

fig_mass_local_gobal.pdf: mass_local_global_fitparams.gzip.pkl
	poetry run unity plot $< --params=mass_local_global
	mv mass_local_global_fitparams.pdf fig_mass_local_gobal.pdf

fig_mass_local.pdf: mass_local_fitparams.gzip.pkl
	poetry run unity plot $< --params=mass_local
	mv mass_local_fitparams.pdf fig_mass_local.pdf

fig_mass_global.pdf: mass_global_fitparams.gzip.pkl
	poetry run unity plot $< --params=mass_global
	mv mass_global_fitparams.pdf fig_mass_global.pdf

fig_local_global.pdf: local_global_fitparams.gzip.pkl
	poetry run unity plot $< --params=local_global
	mv local_global_fitparams.pdf fig_local_global.pdf

fig_mass.pdf: mass_fitparams.gzip.pkl
	poetry run unity plot $< --params=mass
	mv mass_fitparams.pdf fig_mass.pdf

fig_local.pdf: local_fitparams.gzip.pkl
	poetry run unity plot $< --params=local
	mv local_fitparams.pdf fig_local.pdf

fig_global.pdf: global_fitparams.gzip.pkl
	poetry run unity plot $< --params=global
	mv global_fitparams.pdf fig_global.pdf

#Maybe we only need the combined figure.
fig_low_mass_age_only.pdf: low_mass_age_only_fitparams.gzip.pkl
	poetry run unity plot $< --params=mass_local
	mv low_mass_age_only_fitparams.pdf fig_low_mass_age_only.pdf
fig_high_mass_age_only.pdf: high_mass_age_only_fitparams.gzip.pkl
	poetry run unity plot $< --params=mass_local
	mv high_mass_age_only_fitparams.pdf fig_high_mass_age_only.pdf
fig_mass_split.pdf: low_mass_age_only_fitparams.gzip.pkl high_mass_age_only_fitparams.gzip.pkl
	poetry run unity plot low_mass_age_only_fitparams.gzip.pkl high_mass_age_only_fitparams.gzip.pkl --params=high_and_low_mass
	mv low_mass_age_only_fitparams_and_others.pdf fig_mass_with_age_split.pdf
fig_low_mass.pdf: low_mass_fitparams.gzip.pkl
	poetry run unity plot $< --params=salt
	mv low_mass_fitparams.pdf fig_low_mass.pdf
fig_high_mass.pdf: high_mass_fitparams.gzip.pkl
	poetry run unity plot $< --params=salt
	mv high_mass_fitparams.pdf fig_high_mass.pdf
fig_mass_split.pdf: low_mass_fitparams.gzip.pkl high_mass_fitparams.gzip.pkl
	poetry run unity plot low_mass_fitparams.gzip.pkl high_mass_fitparams.gzip.pkl --params=salt
	mv low_mass_fitparams_and_others.pdf fig_mass_split.pdf


help:  ## Displays this message
	@echo "Commands for Rose, Rubin, Strolger, & Garnavich 2020 UNITY re-analysis of Rose, Garnavich, Berg 2019"
	@echo " "
	@echo "This assumes UNITY is installed via `poetry update` and `poertry install`."
	@echo "Check installation via `poertry run unity`."
	@echo " "
	@echo "Use -B or --always-make to force all depdancies to rerun."
	@echo " "
	@echo "`make run` deafults to using 4 cores per job, to run two jobs at once use -j2."
	@echo "When running parallel jobs do not move on till previous step is done:"
	@echo "To (re-)make all on 8 cores, use 'make (-B) -j2 clean_data && make -j2 run && make -j8 paper'."
#	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

.PHONY: help clean_data run