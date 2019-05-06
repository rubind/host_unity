#################################
Unity with Host Galaxy Properties
#################################

This project is an adaption of UNITY_ to standardize Type Ia supernovae with the addition of a full treatment of host properties as seen is needed in Rose et al. 2019.

.. _UNITY: https://github.com/rubind/UNITY_v1

How to install the project
==========================

I can't run it either so don't feel bad, but it will run with Python 3!

With the package on your computer, download latest from Github here, install from that directory with 
:command:`pip install .`

If you are wanting to adapt the model yourself, you may want to install with the ``-e`` flag.

if there is a ``ImportError: Python is not installed as a framework.`` error, this is likely fixed by creating a ``file ~/.matplotlib/matplotlibrc`` there and add the following code: ``backend: TkAgg``


How to use it
============

Ask David. Maybe we will get some documentation at some point.

Then you can run ``unity [OPTIONS] DATA`` where the data is your picked data, defined next. Use ``unity --help`` for more details about the options. Currently only works if run from the within the Unity folder (where ``stan_code_simple.txt`` is in your working directory).

From a pre-compiled model, with 1000 SNe, it takes ~ 45 mins. For 100 SNe it takes 10-20 mins. This is unless a chain gets stuck, then it can take 2.5 hours or ??? respectively. This was with 8 chains, 1000 iterations, on an 8 core Intel Xeon 2018 iMac Pro.

Data
----

The data file needs to be a pickled dictionary containing the needed data variables as defined in the data section of the stan code [link]. As an example, ``build_test_dataset.py`` builds and saves this python object in a ``pickle.dump()`` command at the end of the file.

A full documentation of these values is to come.


Development Instructions
========================

Dependencies and packaging are maintained by ``poetry``.

BR manages his python version via `pyenv` and the project's virtual environment as the one set up via ``poetry`` via :command:`poetry config settings.virtualenvs.in-project true`. This virtual can be activated by :command:`source .venv/bin/activate`. Since the :file:`.venv/` folder is not in the git repo, any developer can use their preferred environment management tool, just note that development should use an appropriate `python version`_.

.. _python version: https://github.com/rubind/host_unity/blob/master/pyproject.toml#L19

I may just use:

.. code-block:: bash
	
	pyenv install 2.7.15
	pyenv local 2.7.15  # Activate Python 2.7 for the current project
	poetry install


-----------

Notes on possible directory structure:

``dataset.pkl`` - real data, just a name.
``testdataset.pkl`` - for test simulated data sets. Names start with test and may be followed by a number to reference an alternative seed for that random dataset.
``testdataset_true.pkl`` - a pickle file of the true values used to create the simulated data set.
``dataset_fitparams.gzip.pkl`` - a gziped pickle files of the fit params for a simulated or real data set.
``dataset_results.txt`` - a text file of the output summary of the fits.

Do we want repeatable, or overwrite? Each data set is unique, but for anyone data set? I am leaning towards just overwrite. We loose same data set with different numbers of samples, but we gain less disk space usage and overwriting of previous bad run results.

-----------

What does it do
===============

To be documented.

Maintainers
===========

David Rubin, @rubind
Benjamin Rose, @benjaminrose

Contributing
============

This is mostly used for our scientific research as such we will only passively maintain this project. You may submit and issue or a pull request, but a response from us will be dependent on our availability and how closely your issue/PR relates to our own research. We are not currently looking to maintain the next great open source project.

Pre-commit and CI tests and de-linters
---------------------------------------

Code of Conduct
---------------

If you do wish to contribute then we ask you to follow the `Astropy Community Code of Conduct`_.

.. _Astropy Community Code of Conduct: http://www.astropy.org/code_of_conduct.html

Licensing
---------

This code is released under the MIT license as documented in the LICENSE file.