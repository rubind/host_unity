Getting Started
===============

Written Mar 16, 2021

Environment
-----------

Previous UNITY documentation use non-``conda`` environments. The scientific community is standardizing on ``conda`` and so should UNITY.

Create a UNITY ``conda`` environment by use unity.yml (found in the root directory of the UNITY project): ``conda env create -f unity.yaml``.

Activate the environnement, then add the UNITY cli, by running ``pip install .`` in repo's top level directory.


Test that things are working
----------------------------

To ensure things are working correctly. Run ``simple_test_dataset.py`` (again found in ``docs/source/``) to create the ``test_simple_300_obs.pkl`` test data set. Run this through the UNITY cli with ``unity run --model=stan_code_simple_debug.txt --steps=100 --max_cores=1 ./path-to/test_simple_300_obs.pkl``.


Your data
---------

I recommend adapting ``./simple_test_dataset.py`` to read in your SALT2 fits and redshifts. A more complete description of each parameter of the data pickle file can be found at ./docs_input_data.rst.