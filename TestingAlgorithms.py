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
def main_PRS_MS(n, solver_name='snopt', time_limit=0):

    Multi_n_iter = n*100
    PRS_n_iter = Multi_n_iter*n*60

    seed1 = 42

    gen_multi = random.Random()

    # calling the solver
    localsolver = create_solver(solver_name)
    
    mymodel = CirclePacking(n)

    #needed to retrieve variable names
    labels = generate_cuid_names(mymodel)

    tech_time = time.process_time()

    logfile = open("mylog.txt", 'w')

    gen_multi.seed(seed1)
    # launching multistart
    if time_limit==0: FoundSolution = multistart(mymodel, Multi_n_iter, gen_multi, localsolver, labels, logfile)
    else: FoundSolution = multistart_timed(mymodel, time_limit, gen_multi, localsolver, labels, logfile)

    model_MS = mymodel.clone()
    multistart_time = time.process_time()

    print("-----------------\n\n")
        
    #restarting from same seed
    gen_multi.seed(seed1)
    if time_limit==0: purerandomsearch(mymodel, PRS_n_iter, gen_multi, labels, logfile)
    else: purerandomsearch_timed(mymodel, time_limit, gen_multi, labels, logfile)

    model_PRS = mymodel.clone()
    prs_time = time.process_time()

    print("\n--------------\nLoading... ", tech_time)
    print("Multistart ", multistart_time - tech_time)

    print("PRS ", prs_time - multistart_time)
    print("Total ", prs_time)

    return model_PRS, model_MS


# Testing MBH
def main_MBH(n,solver_name='snopt', iter=100, mbh_multitrial=False, time_limit=0):
    
    max_no_improve = n*2

    seed1 = 123
    seed2 = 48

    gen = random.Random()
    pert = random.Random()
    
    # calling the solver
    localsolver = create_solver(solver_name)
    
    # create the circle packing model
    mymodel = CirclePacking(n)

    #needed to retrieve variable names
    labels = generate_cuid_names(mymodel)

    tech_time = time.process_time()

    gen.seed(seed1)
    pert.seed(seed2)
    delta = 0.8

    logfile = open("mylog.txt", 'w')
    # launching multistart
    if mbh_multitrial:
        if time_limit == 0: FoundSolution = MBH_MultiTrial(mymodel, iter, gen, localsolver, labels, max_no_improve, pert, delta, logfile)
        else: FoundSolution = MBH_MultiTrial_timed(mymodel, time_limit, gen, localsolver, labels, max_no_improve, pert, delta, logfile)
    else: FoundSolution = MBH(mymodel, gen, localsolver, labels, max_no_improve, pert, delta, logfile)

    mbh_time = time.process_time()
    

    print("\n--------------\nLoading... ", tech_time)
    print("MBH ", mbh_time - tech_time)


    print("Total ", mbh_time)
    return mymodel






if __name__ == '__main__':
    n = 2
    solver_name = "minos" #,"loqo" , "lgo"  ,'knitro' , 'conopt' , 'snopt'
    iter = 10
    mbh_multitrial = True
    # if time_limit==0, the optimisation is not timed
    time_limit = 2 #(in seconds)
    
    # run different optimisation algorithms
    model_PRS, model_MS = main_PRS_MS(n,solver_name, time_limit)
    MBH_model = main_MBH(n,solver_name, iter, mbh_multitrial, time_limit)
    
    # plot the results
    window=Tk()      
    PlotModel(window, model_PRS,'root', "Pure Random Search", solver_name)
    PlotModel(window, model_MS,'ontop', "MultiStart", solver_name)
    PlotModel(window, MBH_model,'ontop', "MBH", solver_name)
    window.mainloop()


# NB:
# if problem with ghostscript (error gs ...), download gs from following link
# then and execute: https://www.ghostscript.com/download/gsdnld.html
# then check if the path for the 'EpsImagePlugin.gs_windows_binary' variable
# in code 'BoxConstrainedGO_Algorithms.py' fits yours.
    
