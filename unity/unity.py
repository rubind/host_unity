""" unity.py - The main code to run the Unity stan model.
"""
import gzip
import pickle
#TODO transition from os.path fully to pathlib
from os import path, makedirs, sys
from pathlib import Path
from hashlib import sha1

import pystan
import numpy as np

CWD = Path.cwd()
UNITY_DIR = Path(__file__).resolve().parent

# todo if the datasets are stored in another directory, how do we just
# get the file name to store matching fit files?
#TODO type annotate and add doc strings
def run(model, data, steps, chains, interactive, max_cores=1):
    """
    Parameters:
        model (str):
            A string represintation of the relative path of the stan model from the Unity directory.
        
        data (str):
            A string representation of the relative path of the data pickel file from the cwd.
            
        steps (int):
        
        chains (int):
    
        interactive (bool):
            A flag to determing if you should jump into a pdb debugging sessions to
            interactively explore the space after the model has been fit.

        max_cores (int):
        
    Returns:
    """

    sm, stan_data = load(UNITY_DIR/model, CWD/data)
    
    # todo protect the user by filtering keys in stan_data. Remove any unneaded? Romove any with sting data? Any other tests?
    stan_vars = ['n_sne', 'n_props', 'n_non_gaus_props', 'n_sn_set', 'sn_set_inds',
                 'z_helio', 'z_CMB', 'obs_mBx1c', 'obs_mBx1c_cov', 'n_age_mix', 'age_gaus_mean',
                 'age_gaus_std', 'age_gaus_A', 'do_fullDint', 'outl_frac_prior_lnmean',
                 'outl_frac_prior_lnwidth', 'lognormal_intr_prior', 'allow_alpha_S_N']
    stan_data = dict((i, stan_data[i]) for i in stan_vars)
    for key in stan_data:
        if np.isnan(stan_data[key]).any() or np.isinf(stan_data[key]).any():
            sys.exit(f"{key} contains an infinity or NaN value.")
    # Why these setting?
    #
    # * Using `n_jobs=1` so that the chains run in series not parallel.
    # There is a bug in multiprocess and/or pickle. There is a signed integer 32-bit array limit
    # Looks like Python 3.8 might have a patch for this.
    # Other patches could be Python 3.9 where they are changing pickle, multiprocessing and the GIL more
    # Or pystan could check before sampling if they will get an array that is too long.
    # This is currently not done in pystan 2.19.0.0.
    # Failures occur with `stan_code_simple_debug.txt` and N_SN = 142. Seems to work with N < 100
    # CHANGE! when Python fixes limit.
    #
    # * Using `par` to only save the data we need for the paper.
    # This is because with N > 194 (was ok with N = 142) the file size is too large for pickle. Maybe?
    # Todo(make pars be user definable, but default to what is below.)
    fit = sm.sampling(data=stan_data, iter=steps, chains=chains, n_jobs=max_cores,
                      pars=['MB', 'coeff_angles', 'sigma_int', 'outl_frac', 'coeff', 'outl_loglike'])
    #TODO update to use pathlib
    save(fit, path.splitext(path.basename(data))[0])

    # Got a strange error: multiprocessing.pool.MaybeEncodingError: Error sending result: '[(0, <stanfit4anon_model_5d703b856fa2f28cab8159e4abe012f4_8855281629809236605.PyStanHolder object at 0x1320cb730>)]'. Reason: 'error("'i' format requires -2147483648 <= number <= 2147483647")'
    # now changing it to a warning and skipping printing summary.
    try:
        print(fit)    # before all else, print to screen.
    except MaybeEncodingError as e:
        print("An error occurred.\n", e, "\n\nNo summary available.")

    if interactive:
        import pdb; pdb.set_trace()    # noqa: E702
    return fit


def compile(stan_model: Path) -> pystan.StanModel:
    """Compiles, and saves a cache, of a given stan model path.
    stan_model: pathlib.Path
        The path to the stan model.


    """
    with open(stan_model) as f:
        s = f.read()
    
    # Use SHA1 to get a 7 digit UUID for a specific stan model.
    # This is not secure, but should not clash for our few expected models
    UUID = sha1(s.encode('utf8')).hexdigest()[:7]
    sm = pystan.StanModel(file=str(stan_model))

    cache_file = UNITY_DIR/'model_cache'/f'Unity_model{UUID}.pickle.txt'
    if not cache_file.parent.exists():
        cache_file.parent.mkdir()
    with open(cache_file, 'wb') as cache:
        pickle.dump((sm, s), cache)
    return sm


def load(stan_model: Path, data: Path) -> (pystan.StanModel, dict):
    """
        stan_model (pathlib.Path):
        data (pathlib.PATH):
    """
    with open(stan_model) as f:
        s_current = f.read()
    UUID = sha1(s_current.encode('utf8')).hexdigest()[:7]
    try:
        # Will fail if there is no cache file for this UUID.
        with open(UNITY_DIR/'model_cache'/f'Unity_model{UUID}.pickle.txt', 'rb') as cache:
            sm, s = pickle.load(cache)
        # This should catch if there was a SHA1 collision.
        if s != s_current:
            raise RuntimeError('Updated Stan model is present.')
    # No matter what failed, just compile again.
    except:    # noqa: E722
        sm = compile(stan_model)

    with open(data, 'rb') as f:
        stan_data = pickle.load(f)

    return sm, stan_data


def save(fit, data_name=''):
    # todo Move to fits folder
    # todo Save more information, https://pystan.readthedocs.io/en/latest/api.html#stanfit4model
    # e.g. stansummary, plots, get_inits
    # This object is 5*N_SNe*steps
    # pickle.dump(fit, gzip.open(f'Unity_{name}_gzip_fit.pickle', 'wb'))
    # print('Inits: ', fit.get_inits())

    # SAVE RAW DATA FIRST! It takes less processing and less possibilities to fail.
    # TODO: update to use a context manager, `with`
    pickle.dump(fit.extract(permuted=True), gzip.open(CWD/f'{data_name}_fitparams.gzip.pkl', 'wb'))
    with open(CWD/f'{data_name}_results.txt', 'w') as text_file:
        try:
            print(fit, file=text_file)
        except MaybeEncodingError as e:
            print("An error occurred.\n", e, "\n\nNo summary available.", file=text_file)
