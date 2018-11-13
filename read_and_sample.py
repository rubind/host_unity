from matplotlib import use
use("PDF")
import pickle
from copy import deepcopy
from numpy import *
import pystan
import corner
import sys
import os
from string import strip
import matplotlib.pyplot as plt
from scipy.stats import scoreatpercentile
from scipy.interpolate import interp1d
import time
import argparse
from permuter import permute
import gzip



################################################# Init FN ###################################################

def init_fn(stan_data):
    n_sne = stan_data["n_sne"]
    n_set = stan_data["n_sn_set"]
    n_Uprops = stan_data["n_Uprops"]
    print "n_sne n_Uprops ", n_sne, n_Uprops

    x1cU_Lmat = zeros([n_Uprops + 2]*2, dtype=float64)
    x1cU_Lmat[0,0] = 1.0

    for i in range(1, n_Uprops+2):
        for j in range(i + 1):
            x1cU_Lmat[i,j] = random.random()*0.02 + 0.02 + 0.5*(i == j)

    print x1cU_Lmat
    
            
    return {"MB": random.random(size = n_set)*0.2 - 29.1,
            "alpha_angle_low": arctan(random.random()*0.2),
            "alpha_angle_high": arctan(random.random()*0.2),
            "beta_angle_blue": arctan(random.random()*0.5 + 2.5),
            "beta_angle_red": arctan(random.random()*0.5 + 2.5),
            "delta": random.normal()*0.02,
            "delta_pd": random.normal()*0.02,

            "gamma_angle": random.normal(size = n_Uprops)*0.05,

            "log10_sigma_int": log10(random.random(size = n_set)*0.1 + 0.1),
            "sigma_int": random.random(size = n_set)*0.02 + 0.08,
            "mBx1cU_int_variance": [1.0 - 0.05*(n_Uprops + 2), 0.05, 0.05] + [0.05]*n_Uprops,

            "true_x1cUs": random.normal(size = (n_sne, n_Uprops+2))*0.05 + stan_data["obs_mBx1cU"][:,1:],
            "alpha_S_N": zeros((n_set, n_Uprops+2), dtype=float64),

            "x1cU_star": [median(stan_data["obs_mBx1cU"][:,1:], axis = 0)]*n_set,

            "x1cU_Lmat": [x1cU_Lmat]*n_set,

            "log10_R_x1cU": [std(stan_data["obs_mBx1cU"][:,1:], axis = 0)]*n_set,


            "outl_frac": random.random(size = n_set)*0.02 + 0.01,
            "u_props_err_scale": 0.9999,
            "delta_x1cUs": [[1]*(2 + n_Uprops)]*n_set,
            "delta_pd_x1cUs": [[1]*(2 + n_Uprops)]*n_set,

            "cross_term": 0,

            "test_points_highmass": random.normal(size = [5, n_Uprops + 2, n_set])*0.01,
            "test_points_lowmass": random.normal(size = [5, n_Uprops + 2, n_set])*0.01
        }

def read_data(opts):
    uspec_keys = opts["uprops"]#"Uspecprop_I", "Uspecprop_II", "Uspecprop_III", "Uspecprop_IV", "Uspecprop_V"]

    n_sne = 0
    n_Uprops = len(uspec_keys)
    
    z_helio = []
    z_CMB = []
    mass = []
    dmass = []
    pdelay = []
    
    obs_mBx1cU = []
    obs_mBx1cU_cov = []
    
    data = pickle.load(open(sys.argv[2], 'rb'))
    other_data = {"sn_list": []}


    sn_set_names = list(sort(unique([data[item]["SNset"] for item in data])))
    print "sn_set_names", sn_set_names
    sn_set_inds = []

    keys = ["RestFrameMag_0_B", "X1", "Color"] + uspec_keys

    for SN in sorted(data.iterkeys()):
        if data[SN]["salt2.Color"] > -0.3 and abs(data[SN]["salt2.X1"]) < 5 and abs(data[SN]["salt2.Color"]) < 2. and all([abs(data[SN][key]) < 6 for key in uspec_keys]):
            n_sne += 1
            sn_set_inds.append(sn_set_names.index(data[SN]["SNset"]))
            z_helio.append(data[SN]["host.zhelio"])
            z_CMB.append(data[SN]["host.zcmb"])
            other_data["sn_list"].append(SN)
            mass.append(data[SN]["mass"])
            dmass.append(data[SN]["dmass"])
            pdelay.append(float(data[SN]["pdelay"]))

            obs_mBx1cU.append([data[SN]["salt2.RestFrameMag_0_B"], data[SN]["salt2.X1"], data[SN]["salt2.Color"]] + 
                              [data[SN][key] for key in uspec_keys])
            obs_mBx1cU_cov.append(zeros([3 + n_Uprops]*2, dtype=float64))

            obs_mBx1cU_cov[-1][0,0] = data[SN]["salt2.RestFrameMag_0_B.err"]**2. + ((5./log(10.))*((opts["pecvel"]/300000.)/z_CMB[-1]))**2.


            for i in range(3 + n_Uprops):
                for j in range(3 + n_Uprops):
                    if i != 0 or j != 0: # 0,0 handled above
                        key1 = "salt2.Cov" + keys[i] + keys[j]
                        key2 = "salt2.Cov" + keys[j] + keys[i]

                        if data[SN].has_key(key1):
                            obs_mBx1cU_cov[-1][i,j] = data[SN][key1]
                        elif data[SN].has_key(key2):
                            obs_mBx1cU_cov[-1][i,j] = data[SN][key2]
                        else:
                            print "Couldn't find ", SN, key1, key2
                            assert i != j
                            print "Setting ", key1, key2, "to 0!!!!"

            assert all(transpose(obs_mBx1cU_cov[-1]) == obs_mBx1cU_cov[-1])
            assert all(1 - isinf(obs_mBx1cU_cov[-1])), SN + " is bad!"
        else:
            print "Didn't select ", SN
            assert 0
            
            
    print "n_sne ", n_sne
    print array(obs_mBx1cU)

    #print "TEST OF UNCERTAINTIES!!!!!!!!!!!!!!!!!!!!"*100
    #obs_mBx1cU_cov = array([obs_mBx1cU_cov[0]]*n_sne)

    other_data["sn_set_names"] = sn_set_names

    stan_data = dict(n_sne = n_sne, n_Uprops = n_Uprops, sn_set_inds = sn_set_inds, n_sn_set = len(sn_set_names),
                     z_helio = z_helio, z_CMB = z_CMB, obs_mBx1cU = array(obs_mBx1cU), obs_mBx1cU_cov = array(obs_mBx1cU_cov),
                     mass = mass, dmass = dmass, allow_alpha_S_N = opts["allow_alpha_SN"],
                     do_twoalpha = opts["dotwoalpha"], do_twobeta = opts["dotwobeta"], do_fullDint = opts["multiint"],
                     outl_frac_prior_lnmean = log(opts["outfrac"]), outl_frac_prior_lnwidth = 0.5, alphalim = opts["alphalim"],
                     include_alpha = opts["includealpha"], Uprops_scale = opts["upropsscale"], apply_delta_x1cUs = opts["apply_delta_x1cUs"],
                     lognormal_intr_prior = opts["lognormal_intr_prior"], mass_step = opts["massstep"], delay_step = opts["delaystep"], pdelay = pdelay)

    print "shape ", stan_data["obs_mBx1cU"].shape
    print "shape ", stan_data["obs_mBx1cU_cov"].shape

    return stan_data, other_data

################################################# Main Fit ###################################################


def run_fit(**opts):
    bad_sampling = 1

    while bad_sampling:
        bad_sampling = 0
        stan_data, other_data = read_data(opts)

        init_lambda = lambda: init_fn(stan_data)

        print "Running...", time.asctime()

        
        f = open(opts["stan"], 'r')
        lines = f.read()
        f.close()

        if opts["debug"] == 0:
            lines =lines.replace("AAAAA", "\n").replace("BBBBB", "}\nmodel{\n").replace("CCCCC", "\n").replace("DDDDD", "\n")
        else:
            sublines = lines.split("AAAAA")[1].split("BBBBB")[0]
            lines = lines.replace("AAAAA", "\n").replace("BBBBB", "\n").replace(sublines, "").replace("CCCCC", sublines).replace("DDDDD", "}\nmodel{\n")
            
            print lines

        fit = pystan.stan(model_code=lines, data=stan_data,
                          iter=opts["niter"], chains=6, n_jobs = 6, refresh = 20, init = init_lambda)


        print "Extracting...", time.asctime()
        fit_params = fit.extract(permuted = True)

        print time.asctime()

        if opts.has_key("pickle_name"):
            if opts["debug"] == 0:
                del fit_params["true_x1cUs"]

            pickle.dump((stan_data, fit_params, other_data, opts), gzip.open("fit_params_%02i.pickle" % (opts["permind"]), "wb"))

        print time.asctime()

        print "I hope you have a log file:"

        #try:
        fitstr = str(fit)
        print fitstr

        for line in fitstr.split('\n'):
            parsed = line.split(None)
            if len(parsed) > 3:
                if parsed[0] == "alpha":
                    neff = float(parsed[-2])
                    print "Found neff ", neff, parsed
                    if neff < 100:
                        print "Bad sampling!"
                        bad_sampling = 1
                    else:
                        print "Good sampling!"
        #except:
        #    print "Couldn't print fit! Something is very wrong!"

        print time.asctime()

    return fit_params, stan_data

def credible(samples):
    val84 = scoreatpercentile(samples, 84.1345, axis = 0)
    val16 = scoreatpercentile(samples, 15.8655, axis = 0)
    val50 = scoreatpercentile(samples, 50., axis = 0)

    txt = ""

    try:
        val50[0]
    except:
        val50 = [val50]
        val16 = [val16]
        val84 = [val84]

    for i in range(len(val50)):
        txt += "%.3f +%.3f -%.3f;" % (val50[i], val84[i] - val50[i], val50[i] - val16[i])
    return txt[:-1]

def clean_str(item):
    return str(item).replace(" ", "").replace(",", "+").replace("[", "").replace("]", "").replace("..", "").replace("/", "").replace("'", "").replace('"', "")

def read_from_file(fl):
    f = open(fl)
    lines = f.read().split('\n')
    f.close()

    to_permute = {}
    for line in lines:
        parsed = line.split(None)
        if len(parsed) > 1:
            to_permute[parsed[0]] = eval(" ".join(parsed[1:]))
    print "to_permute", to_permute
    return to_permute


permutations, NA = permute(** read_from_file(sys.argv[1]))


for i in range(len(permutations)):
    permutations[i]["includealpha"] = 1
    #permutations.append(deepcopy(permutations[i]))
    #permutations[-1]["includealpha"] = 0
    
for item in permutations:
    print item

fres = open("results.csv", 'w')

fpickname = open("pickles.txt", 'w')

for permind, item in enumerate(permutations):

    keys = item.keys()
    keys.sort()
    
    towrite = []
    for key in keys:
        towrite += [key + "=" + clean_str(item[key])]
    item["pickle_name"] = "fit_results_" + "_".join([key + "=" + clean_str(item[key]) for key in keys])
    item["permind"] = permind

    fit_params, stan_data = run_fit(**item)

    fpickname.write("%s    fit_params_%02i.pickle\n" % (item["pickle_name"], permind))
    fpickname.flush()
    
    towrite += ["uprops=" + clean_str(item["uprops"]), "includealpha=" + str(item["includealpha"]),
                "MB=" + credible(fit_params["MB"]),
                "pecvel=" + str(item["pecvel"]),
                "alpha_L=" + credible(fit_params["alpha_L"]),
                "alpha_H=" + credible(fit_params["alpha_H"]),
                "beta_B=" + credible(fit_params["beta_B"]),
                "beta_R=" + credible(fit_params["beta_R"]),
                "delta=" + credible(fit_params["delta"]),
                "sigint=" + credible(fit_params["sigma_int"])]

    
    if stan_data["n_Uprops"] > 1:
        print "gamma.shape", fit_params["gamma"].shape
    print "delta_x1cUs.shape", fit_params["delta_x1cUs"].shape

    for i in range(stan_data["n_Uprops"]):
        if stan_data["n_Uprops"] > 1:
            towrite.append("gamma_" + str(i) + "=" + credible(fit_params["gamma"][:,i]))
            towrite.append("alpha-gamma_" + str(i) + "=" + credible(fit_params["alpha"] - fit_params["gamma"][:,i]))
        else:
            towrite.append("gamma_" + str(i) + "=" + credible(fit_params["gamma"]))
            towrite.append("alpha-gamma_" + str(i) + "=" + credible(fit_params["alpha"] - fit_params["gamma"]))

    if stan_data["n_Uprops"] > 0:
        towrite.append("u_props_err_scale=" + credible(fit_params["u_props_err_scale"]))
    
    for i in range(stan_data["n_Uprops"] + 2):
        towrite.append("delta_x1cUs=" + credible(fit_params["delta_x1cUs"][:,:,i]))


    fres.write(",".join(towrite) + '\n')
    fres.flush()

fres.close()
fpickname.close()

print "Done!"
