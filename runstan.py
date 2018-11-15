""" unity.py
"""
import gzip
import pickle

import pystan
import click

MODEL = 'stan_code_simple.txt'
DATA = 'sample_obs_1000SNe'

@click.command()
@click.argument('stan_model')
@click.argument('data')
@click.option('--steps', default=1000, help='Number of greetings.')
@click.option('--chains', default=8, help='The person to greet.')
def run(stan_model, data, steps, chains):

    sm, stan_data = load(stan_model, data)

    fit = sm.sampling(data=stan_data, iter=steps, chains=chains)
    save(fit, data)
    print(fit)


def compile(stan_model):
    with open(stan_model) as f:
        s = f.read()
    sm = pystan.StanModel(file=stan_model)
    pickle.dump((sm, s), open('Unity_model.pickle.txt', 'wb'))
    return sm

def load(stan_model, data):
    try:
        sm, s = pickle.load(open('Unity_model.pickle.txt', 'rb'))
        with open(stan_model) as f:
            s_current = f.read()
        if s != s_current:
            raise RuntimeError('Updated Stan model is present.')
    except:
        sm = compile(stan_model)

    stan_data = pickle.load(open('Sample_obs_1000SNe','rb'))

    return sm, stan_data

def save(fit, name=''):
    # This object is 5*N_SNe*steps
    pickle.dump(fit, gzip.open(f'Unity_{name}_gzip_fit.pickle', 'wb'))




if __name__ == '__main__':
    
    runner = CliRunner()
    result = runner.invoke(run, [MODEL, DATA])
    # run(MODEL, DATA, steps=1000, chains=8)
