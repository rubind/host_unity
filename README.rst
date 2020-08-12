#################################
Unity with Host Galaxy Properties
#################################

This project is an adaption of UNITY_ that allows for standardization of Type Ia supernovae with the addition of a full treatment of host properties.

.. _UNITY: https://github.com/rubind/UNITY_v1


Installing UNITY
================

Installation is poorly tested and documented after one reinstall. Bellow there be errors.

With the repo downloaded and a `conda` installation working, from inside the root directory of UNITY:

.. code-block:: shell

    conda env create -f unity.yaml
    conda activate unity
    pip install .

The full list of pinned dependencies can be found in ``unity-lock.yaml``. Installing `unity` can also be done in editable mode: `` pip install -e .``. Currently only the `unity` application is supported; it is not accessible as an importable module.

Previous and still possible installation instructions, if if you change the ``pyproject.toml`` and ``setup.py`` files :

This application was maintained via via Poetry_ and the ``pyproject.toml`` file. Its depends on Python 3 (tested with 3.7) and most of the typical scientific software stack_.

.. _Poetry: https://poetry.eustace.io
.. _stack: https://github.com/rubind/host_unity/blob/master/pyproject.toml#L18

The latest instructions to Install Poetry are avaialble via its documentation_. It should be something like ``curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python``

.. _documentation: https://poetry.eustace.io/docs/

With this package on your computer (latest from GitHub_), Poetry installed, and any desired virtual environments activated, install UNITY via 
:command:``poetry install``. By default, this will also include the development dependencies.

.. _GitHub: https://github.com/rubind/host_unity/archive/master.zip
.. https://github.com/sdispater/poetry/issues/366

If there is a ``ImportError: Python is not installed as a framework.`` error, this is likely fixed by creating a file ``~/.matplotlib/matplotlibrc`` containing: ``backend: TkAgg``


How to use it
=============

Information can be found via ``unity --help`` (or ``poetry run unity --help`` if installed inside a Poetry virtual environment). Examples of using UNITY can be see in some of the associated analysis scripts_. 

.. _scripts: https://github.com/rubind/host_unity/blob/master/fitting/makefile 

From a pre-compiled model, with 1000 SNe, it takes ~ 45 mins. For 100 SNe it takes 10-20 mins. This assumes a chain does not get stuck, then it can take hours. This was with 8 chains, 1000 iterations, on an 8 core Intel Xeon 2018 iMac Pro.

Data
----

The data input files need to be a pickled dictionary containing all the expected UNITY variables. This file will be better documented, but for now, you can find some information in the docs_input_data.rst_ file. As an example, ``build_test_dataset.py``_ builds and saves this python object in a ``pickle.dump()`` command at the end of the file.

.. _docs_input_data.rst: https://github.com/rubind/host_unity/blob/master/docs/source/docs_input_data.rst
.. _``build_test_dataset.py``: https://github.com/rubind/host_unity/blob/master/unity/build_test_dataset.py

A full documentation of these values is to come.


Development & Contributing Instructions
=======================================

This is mostly used for our scientific research as such we will only passively maintain this project. You may submit and issue or a pull request, but a response from us will be dependent on our availability and how closely your issue/PR relates to our own research. We are not currently looking to maintain the next great open source project.

More detailed contribution instructions will be published soon, but are currently available upon request.

.. Pre-commit and CI tests and de-linters
.. ---------------------------------------

Code of Conduct
---------------

If you do wish to contribute then we ask you to follow the `Astropy Community Code of Conduct`_.

.. _Astropy Community Code of Conduct: http://www.astropy.org/code_of_conduct.html

Licensing
---------

This code is released under the MIT license as documented in the :file:``LICENSE`` file.

Maintainers
===========

* David Rubin, @rubind
* Benjamin Rose, @benjaminrose
* Sam Dixon, @sam-dixon
