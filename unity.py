""" unity.py - The main code to run the Unity stan model.
"""
import gzip
import pickle
from os import path, makedirs

import pystan


# todo if the datasets are stored in another directory, how do we just
# get the file name to store matching fit files?
def run(model, data, steps, chains, interactive):

    sm, stan_data = load(model, data)

    fit = sm.sampling(data=stan_data, iter=steps, chains=chains)
    print(fit)    # before all else, print to screen.
    save(fit, path.splitext(path.basename(data))[0])
    if interactive:
        import pdb; pdb.set_trace()    # noqa: E702
    return fit


def compile(stan_model):
    # todo Move to model_cashe folder
    with open(stan_model) as f:
        s = f.read()
    sm = pystan.StanModel(file=stan_model)
    pickle.dump((sm, s), open('Unity_model.pickle.txt', 'wb'))
    return sm


def load(stan_model, data):
    # todo Move to model_cashe folder
    # todo Update with https://pystan.readthedocs.io/en/latest/avoiding_recompilation.html#automatically-reusing-models
    try:
        sm, s = pickle.load(open('Unity_model.pickle.txt', 'rb'))
        with open(stan_model) as f:
            s_current = f.read()
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

    # https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
    if not path.exists('fits/'):
        try:
            makedirs('fits/')
        except OSError as exc:    # Guard against race condition
            raise exc

    # save simple first, then more and more complicated ways
    with open(f'{data_name}_results.txt', 'w') as text_file:
        print(fit, file=text_file)
    pickle.dump(fit.extract(permuted=True), gzip.open(f'{data_name}_fitparams.gzip.pkl', 'wb'))


if __name__ == '__main__':
    # note that these defaults are for debugging and not suitable for good fits.
    print('RUNINNG DEFAULT SAMPLES!\n\n')
    model = 'stan_code_simple.txt'
    data = 'sample_obs_100SNe'
    steps = 500
    chains = 4
    interactive = False
    run(model, data, steps, chains, interactive)
    print('\n\nDEFAULT TEST DATASET USED!')
