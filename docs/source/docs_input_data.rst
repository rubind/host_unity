Requirements of the input data set
==================================

Unity expects to be given a [pickle]() file of the appropriate python objects. You can read, in the [data section]() of `stan_code_simple.txt` all the expected input parameters. Follows is an explanation. 

General Properties
------------------

* ``n_sne``: How many supernovae are you fitting? Needs to be an integer >=1.
* ``n_props``: How many properties are you following. SALT2 follows 3, M_B, x_1 & c. If you are also giving host mass and age, this value should be 5. Needs to be an integer >=2.
* ``n_non_gaus_pros``: How many properties are described in a non-Gaussian way? Is your age an Gaussian mixture?. Needs to be an integer >=0.
* ``n_sn_set``: How many SNe data sets do you have?. Needs to be an integer >=1.
* ``sn_set_inds``: What data set does this SN belong to? Needs to be a array of integers of length ``s_sne``, uses python-like indexing that starts at 0.

Redshifts
---------

Why two redshifts? IDK.

* ``z_helio``: Helio-centric redshift. Needs to be a array of integers of length `s_sne`.
* ``z_CMB``: CMB-centric redshift. Needs to be a array of integers of length ``s_sne``.

Gaussian Properties
-------------------

* ``obs_mBx1c``: Observational values that can be defined as a Gaussian. For SALT2 this is just M_B, x_1, and c. Needs to be an array of shape (``n_sne``, ``n_props`` - ``n_non_gaus_props``).
* ``obs_mBx1c_cov``: Covariance matrix for the Gaussian defined observations. Needs to be an array of shape (``n_sne``, ``n_props`` - ``n_non_gaus_props``, ``n_props`` - ``n_non_gaus_props``).

Non-Gaussian Properties
-----------------------

We represented age as a mixture of Gaussians. You can represent any number of non-Gaussian parameters a a Gaussian mixture. If ``n_non_gaus_pros`` is zero, then these variable can just hold dumpy numbers.

example if ``n_age_mix`` is zero: ``data['age_gaus_mean'] = np.zeros((0, n_sne, 0), np.float64)``

* ``n_age_mix``: How many Gaussians are in your mix. Needs to be an integer >=0. Only set to zero if ``n_non_gaus_props`` is zero.
* ``age_gaus_mean``: What are the mean of these Gaussians. Needs to be an array of shape (``n_non_gaus_props``, ``n_sne``, ``n_age_mix``).
* ``age_gaus_std``: What are the standard deviation of these Gaussians. Needs to be an array of shape (`n_non_gaus_props`, `n_sne`, ``n_age_mix``).
* ``age_gaus_A``: What are the amplitudes of these Gaussians. Needs to be an array of shape (``n_non_gaus_props``, ``n_sne``, ``n_age_mix``).

Other stuff
-----------

I am not sure about these, but David says to just use:

.. code-block:: python

   do_fullDint=0
   outl_frac_prior_lnmean=-4.6
   outl_frac_prior_lnwidth=1
   lognormal_intr_prior=0

* ``allow_alpha_S_N`` important when we model the populations as mutli-demention skew normals. Not as relevant for linear models. Set 0 to off and 1 for on.


An example snippet of code that builds the needed pickle file. 

.. code-block:: python

   pickle.dump(dict(     # general properties
                    n_sne=N_SNE, n_props=5, n_non_gaus_props=1, n_sn_set=1,
                    sn_set_inds=[0]*N_SNE,
                         # redshifts
                    z_helio=[0.1]*N_SNE, z_CMB=[0.1]*N_SNE,
                         # Gaussian defined properties
                    obs_mBx1c=[[m_b[i], lc_data['X1'].iloc[i], lc_data['COLOR'].iloc[i], 
                                mass['stellarmass'].iloc[i]] for i in range(N_SNE)],
                    obs_mBx1c_cov=cov,
                         # Non-Gaussian properties, aka age
                    n_age_mix=N_AGE_MIX, age_gaus_mean=np.expand_dims(means, 0), 
                    age_gaus_std=np.expand_dims(stds, 0), age_gaus_A=np.expand_dims(amplitudes, 0),
                         # Other stuff that does not really need to change
                    do_fullDint=0, outl_frac_prior_lnmean=-4.6, outl_frac_prior_lnwidth=1,
                    lognormal_intr_prior=0, allow_alpha_S_N=0),
               open('forUnity.pickle', 'wb'))

