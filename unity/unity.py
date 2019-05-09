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
def run(model, data, steps, chains, interactive):
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
    fit = sm.sampling(data=stan_data, iter=steps, chains=chains)
    print(fit)    # before all else, print to screen.
    #TODO update to use pathlib
    save(fit, path.splitext(path.basename(data))[0])
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

    stan_data = pickle.load(open(data, 'rb'))

    return sm, stan_data


def save(fit, data_name=''):
    # todo Move to fits folder
    # todo Save more information, https://pystan.readthedocs.io/en/latest/api.html#stanfit4model
    # e.g. stansummary, plots, get_inits
    # This object is 5*N_SNe*steps
    # pickle.dump(fit, gzip.open(f'Unity_{name}_gzip_fit.pickle', 'wb'))
    # print('Inits: ', fit.get_inits())

    # save simple first, then more and more complicated ways
    with open(CWD/f'{data_name}_results.txt', 'w') as text_file:
        print(fit, file=text_file)
    # TODO: update to use a context manager, `with`
    pickle.dump(fit.extract(permuted=True), gzip.open(CWD/f'{data_name}_fitparams.gzip.pkl', 'wb'))


if __name__ == '__main__':
    # note that these defaults are for debugging and not suitable for good fits.
    print('RUNINNG DEFAULT DATASET!\n\n')
    model = UNITY_DIR/'stan_code_simple.txt'
    data = UNITY_DIR/'sample_obs_100SNe'
    steps = 500
    chains = 4
    interactive = False
    run(model, data, steps, chains, interactive)
    print('\n\nDEFAULT TEST DATASET USED!')
