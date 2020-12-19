import pyomo.environ as pe
from pyomo.core.base.block import generate_cuid_names

from pyomo.opt import SolverFactory
from pyomo.opt import SolverStatus, TerminationCondition

from BoxConstrainedFunctions import *
from CirclePacking import *
from BoxConstrainedGO_Algorithms import *

import random
import time

#Testing PRS vs Multistart
def main1(n):

    Multi_n_iter = 2*100
    PRS_n_iter = Multi_n_iter*2*60

    seed1 = 42

    gen_multi = random.Random()

    # chosing the solver
    localsolver = create_solver('snopt')
    
    mymodel = CirclePacking(n)

    #needed to retrieve variable names
    labels = generate_cuid_names(mymodel)

    tech_time = time.process_time()

    logfile = open("mylog.txt", 'w')

    gen_multi.seed(seed1)
    # launching multistart
    FoundSolution = multistart(mymodel, Multi_n_iter, gen_multi, localsolver, labels, logfile)

    multistart_time = time.process_time()

    print("-----------------\n\n")
        
    #restarting from same seed
    gen_multi.seed(seed1)
    purerandomsearch(mymodel, PRS_n_iter, gen_multi, labels, logfile)

    prs_time = time.process_time()

    print("\n--------------\nLoading... ", tech_time)
    print("Multistart ", multistart_time - tech_time)

    print("PRS ", prs_time - multistart_time)
    print("Total ", prs_time)
    
    return mymodel


# Testing MBH
def main2(n):
    
    
    max_no_improve = n*20

    seed1 = 123
    seed2 = 48

    gen = random.Random()
    pert = random.Random()
    
    # chosing the solver
    localsolver = create_solver('snopt')
    
    #mymodel = Rastrigin(n, -5.12, 5.12)
    mymodel = CirclePacking(n)

    #needed to retrieve variable names
    labels = generate_cuid_names(mymodel)

    tech_time = time.process_time()

    gen.seed(seed1)
    pert.seed(seed2)
    delta = 0.8

    logfile = open("mylog.txt", 'w')
    # launching multistart
    FoundSolution = MBH(mymodel, gen, localsolver, labels, max_no_improve, pert, delta, logfile)

    mbh_time = time.process_time()
    

    print("\n--------------\nLoading... ", tech_time)
    print("MBH ", mbh_time - tech_time)


    print("Total ", mbh_time)
    return mymodel



if __name__ == '__main__':
    n = 4
    mymodel = main2(n)
    PlotModel(mymodel)


