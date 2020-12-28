import pyomo.environ as pe
from pyomo.opt import SolverFactory
from pyomo.opt import SolverStatus, TerminationCondition
import os, sys
import time
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'../utilities')))
from optmodel_utilities import *
from tkinter import Tk, Canvas, Button, Toplevel, filedialog
from PIL import Image, EpsImagePlugin
EpsImagePlugin.gs_windows_binary =  r'C:\Program Files (x86)\gs\gs9.25\bin\gswin32c'

# This method will create a slover. It takes as argument the name of the solver 
# (a string variable, here by default is `'cplex'`, the argument would be `'gurobi'` if, e.g., Gurobi was desired instead of `'cplex'`)  and it returns an object solver where you can invoke `solve()`
# 
# Make sure to unzip the solvers in `solvers` directory 
# 
# 


def savegraph(canvas,window,title):
    fileName =  fileName = r'C:/Users/33758/Desktop/3A Mines/Optimisation/DM 2/figures/' + title
    if fileName:
        # save postscipt image 
        canvas.postscript(file = fileName)
        print("fileName : ",fileName)
        im = Image.open(fileName)
        im.save(fileName[:-4] + '_jpeg.jpeg', 'jpeg', dpi=(530,600), optimize=True, quality=94, progressive=True ) 

        

def PlotModel(window, model, level='root',type_opt="", solver_name=""):
    """
    level == 'root' : create canvas on the window
    level == 'ontop' : vreate another level on top of the window
    type_opt in {'PRS', 'MS', 'MBH}  """
    
    
    # extract usefull values from the model
    n = model.n.value
    r = model.r.value
    x_dict = model.x.get_values()
    y_dict = model.y.get_values()

    # set the parameters of the Tkinter window (root)
    margin = 0
    ech = 500
    bg_color = "#F5CBA7"
    ball_color = "#F1C40F"
    
    # fill the tkinter window:
    if level=='root' : root = window
    else: root = Toplevel(window)
    title = type_opt+" - Solver "+solver_name+" - n = "+str(n)
    root.title(title)
    root.geometry(str(2*margin+ech)+"x"+str(ech+40))
    
    # create the Canvas to plot the circles and add a save button
    cnv = Canvas(root, height=ech, width=ech) 
    cnv.grid(row=0, column=0)
    Button(root , text='Save to png',font=('Lucida Bright', '11'), bg="#0e2f2f", fg="#ffffff", command=lambda: savegraph(cnv,root,title)).grid(row=1, column =0)

    bg = cnv.create_rectangle(margin, margin, margin+ech, margin+ech, outline="#F5CBA7", fill=bg_color)
    

    def create_circle(canvas, x, y, r):
        return canvas.create_oval(x-r, y-r, x+r, y+r,dash=5, fill=ball_color)

    for i in range(n):
        cercle = create_circle(cnv, ech*x_dict[i+1], ech*y_dict[i+1], ech*r)
        cnv.pack
    



def create_solver(solver_name = 'cplex'):
    solver_path = get_solver_path(solver_name)
    return  SolverFactory(solver_name, executable=str(solver_path), solver_io = 'nl')

# random generating point keeping in [lb,ub]
def random_point(model, gen_multi):
    for i in model.N:
        model.x[i] = gen_multi.uniform(0, 1)
        model.y[i] = gen_multi.uniform(0, 1)

# perturbation
def perturb_point(model, gen_pert, epsilon = 0.3):
    epsilon = 0.3
    for i in model.N:
        model.x[i] = model.x[i].value*(1+gen_pert.uniform(-0.5, 0.5) * epsilon)
        model.y[i] = model.y[i].value*(1+gen_pert.uniform(-0.5, 0.5) * epsilon)
        model.r=model.r.value*(1+gen_pert.uniform(-0.5, 0.5) * epsilon)
        #project inside the box (ATTENTION: the perturbation is not anymore a uniform distribution)
        model.x[i] = max(0, min(model.x[i].value, 1))
        model.y[i] = max(0, min(model.y[i].value, 1))
        model.r = max(0, min(model.r.value, 1))

# adjusted perturbation
def perturb_point_adj(model, gen_pert):
    epsilon = 0.01*model.r.value
    for i in model.N:
        model.x[i] = model.x[i].value*(1+gen_pert.uniform(-0.5, 0.5) * epsilon)
        model.y[i] = model.y[i].value*(1+gen_pert.uniform(-0.5, 0.5) * epsilon)
        model.r=model.r.value*(1+gen_pert.uniform(-0.5, 0.5) * epsilon)
        #project inside the box (ATTENTION: the perturbation is not anymore a uniform distribution)
        model.x[i] = max(0, min(model.x[i].value, 1))
        model.y[i] = max(0, min(model.y[i].value, 1))
        model.r = max(0, min(model.r.value, 1))






# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Pure Random Search


# this function performs a pure random search on a model and
# for a given number of iterations
def purerandomsearch(mymodel, iter, gen_multi, labels,
                     logfile = None, epsilon=10**-4):

    algo_name = "PRS:"
    best_obj = 10000 #put a reasonable value bound for the objective
    bestpoint = {} #dictionary to store the best solution
    
    nb_solution = 0

    for it in range(1,iter+1):
        random_point(mymodel, gen_multi)

        #we trust random generation to produce a feasible point
        #otherwise we need to check feasibility
        
        # printing result and solution on screen
        obj = mymodel.obj()
        print(algo_name + " Iteration ", it, " current value ", obj, end = '', file = logfile)
        if obj < best_obj -epsilon:  # + epsilon:
            best_obj = obj
            print(" *", file = logfile)
            printPointFromModel(mymodel, logfile)
            StorePoint(mymodel, bestpoint, labels)
        else:
            print(file = logfile)

    print(algo_name +" Best record found  {0:8.4f}".format(best_obj))
    LoadPoint(mymodel, bestpoint)
    printPointFromModel(mymodel)

    return True

# this function performs a timed version ofpure random search 
def purerandomsearch_timed(mymodel, time_limit, gen_multi, labels,
                     logfile = None, epsilon=10**-4):

    algo_name = "PRS:"
    best_obj = 10000 #put a reasonable value bound for the objective
    bestpoint = {} #dictionary to store the best solution
    
    nb_solution = 0
    time_start = time.time()
    it = 0
    
    while time.time()-time_start < time_limit :
        it+=1
        random_point(mymodel, gen_multi)

        #we trust random generation to produce a feasible point
        #otherwise we need to check feasibility
        
        # printing result and solution on screen
        obj = mymodel.obj()
        print(algo_name + " Iteration ", it, " current value ", obj, end = '', file = logfile)
        if obj < best_obj -epsilon:  # + epsilon:
            best_obj = obj
            print(" *", file = logfile)
            printPointFromModel(mymodel, logfile)
            StorePoint(mymodel, bestpoint, labels)
        else:
            print(file = logfile)

    print(algo_name +" Best record found  {0:8.4f}".format(best_obj))
    LoadPoint(mymodel, bestpoint)
    printPointFromModel(mymodel)

    return True

def check_if_optimal(results):
    ok = (results.solver.status == pe.SolverStatus.ok)
    optimal = (results.solver.termination_condition
               == pe.TerminationCondition.optimal)
    return  (ok and optimal)







# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# MULTISTART 

# this function performs multistart on a model and
# for a given number of iterations
def multistart(mymodel, iter, gen_multi, localsolver, labels,
               logfile = None, epsilon = 10**-4):

    algo_name = "Multi:"
    best_obj = 10000 #put a reasonable value bound for the objective
    bestpoint = {} #dictionary to store the best solution
    
    nb_solution = 0
    feasible = False

    for it in range(1,iter+1):
        random_point(mymodel, gen_multi)

        # local search
        results = localsolver.solve(mymodel)

        # printing result and solution on screen
        if check_if_optimal(results):
            nb_solution += 1  # couting feasible iterations
            obj = mymodel.obj()
            print(algo_name + " Iteration ", it, " current value ", obj, end = '', file = logfile)
            if obj < best_obj - epsilon:  # + epsilon:
                best_obj = obj
                print(" *" , file = logfile)
                printPointFromModel(mymodel, logfile)
                feasible = True
                StorePoint(mymodel, bestpoint, labels)
            else:
                print(file = logfile)
        else:
            print(algo_name+" Iteration ", it, "No feasible solution", file = logfile)

    if feasible == True:
        print(algo_name + " Best record found  {0:8.4f}".format(best_obj))
        LoadPoint(mymodel, bestpoint)
        printPointFromModel(mymodel)
    else:
        print(algo_name + " No feasible solution found by local solver")
        
    print(algo_name + " Total number of feasible solutions ", nb_solution)

    return feasible


# this function performs a timed version of multistart 
def multistart_timed(mymodel, time_limit, gen_multi, localsolver, labels,
               logfile = None, epsilon = 10**-4):

    algo_name = "Multi:"
    best_obj = 10000 #put a reasonable value bound for the objective
    bestpoint = {} #dictionary to store the best solution
    
    nb_solution = 0
    feasible = False
    time_start = time.time()
    it = 0
    
    while time.time()-time_start < time_limit :
        it+=1
        random_point(mymodel, gen_multi)

        # local search
        results = localsolver.solve(mymodel)

        # printing result and solution on screen
        if check_if_optimal(results):
            nb_solution += 1  # couting feasible iterations
            obj = mymodel.obj()
            print(algo_name + " Iteration ", it, " current value ", obj, end = '', file = logfile)
            if obj < best_obj - epsilon:  # + epsilon:
                best_obj = obj
                print(" *" , file = logfile)
                printPointFromModel(mymodel, logfile)
                feasible = True
                StorePoint(mymodel, bestpoint, labels)
            else:
                print(file = logfile)
        else:
            print(algo_name+" Iteration ", it, "No feasible solution", file = logfile)

    if feasible == True:
        print(algo_name + " Best record found  {0:8.4f}".format(best_obj))
        LoadPoint(mymodel, bestpoint)
        printPointFromModel(mymodel)
    else:
        print(algo_name + " No feasible solution found by local solver")
        
    print(algo_name + " Total number of feasible solutions ", nb_solution)

    return feasible





# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# MBH


# this function performs MBH on a model
def MBH(mymodel, gen, localsolver, labels,
        max_no_improve, pert, delta,
        logfile = None, epsilon = 10**-4):

    algo_name = "MBH:"
    best_obj = 10000 #put a reasonable value bound for the objective
    bestpoint = {} #dictionary to store the best solution (and current center)

    
    feasible = False
    no_improve = 0
    nb_solution = 0

    #look for a starting local solution
    random_point(mymodel, gen)
    results = localsolver.solve(mymodel)

    # a first feasible solution is found
    if check_if_optimal(results):
        feasible = True
        nb_solution += 1  # counting feasible iterations
        best_obj = mymodel.obj()
        StorePoint(mymodel, bestpoint, labels)

        print(algo_name, " starting center "," current value ", best_obj, " *", file = logfile)

        #start local search (perturbation of the current point)
        while (no_improve < max_no_improve):

            perturb_point_adj(mymodel, pert)
            results =localsolver.solve(mymodel)
            obj = mymodel.obj()

            if check_if_optimal(results):
                #improving on current center
                if obj < best_obj - epsilon:
                    feasible = True
                    best_obj = obj
                    print(algo_name + " ",  " no_improve ", no_improve, " best_obj ", best_obj, " *", file = logfile)
                    #no load needed - in model there is already the perturbed point
                    no_improve = 0
                else:
                    #restoring current center
                    LoadPoint(mymodel, bestpoint)
                    print(algo_name + " ", " no_improve ", no_improve, " noImprovingStep", file = logfile)
                    no_improve += 1
    else:
        print(algo_name, " No feasible solution", file = logfile)

    if feasible == True:
        print(algo_name + " Best record found  {0:8.4f}".format(best_obj))
        LoadPoint(mymodel, bestpoint)
        printPointFromModel(mymodel)
    else:
        print(algo_name + " No feasible solution found by local solver")
        
    print(algo_name + " Total number of feasible solutions ", nb_solution)

    return feasible


# this function performs MBH on a model
# for a given number of iterations (iter = 1 correspond to a single MBH)
# it can be re-implemented using calling MBH() function iter-times
def MBH_MultiTrial(mymodel, iter, gen, localsolver, labels,
        max_no_improve, pert, delta,
        logfile = None, epsilon = 10**-4):

    algo_name = "MBH:Trial"
    best_obj = 10000 #put a reasonable value bound for the objective
    bestpoint = {} #dictionary to store the best solution
    current_value = best_obj
    currentcenter = {} #dictionary to store the current center (for pertubation step)
    
    feasible = False

    for it in range(1,iter+1):
        no_improve = 0
        nb_solution = 0

        random_point(mymodel, gen)

        # local search
        results = localsolver.solve(mymodel)

        # a first feasible solution is found
        if check_if_optimal(results):
            nb_solution += 1  # couting feasible iterations
            current_value = mymodel.obj()
            StorePoint(mymodel, currentcenter, labels)
            
            print(algo_name + " ", it, " starting center "," current value ", current_value, end = '', file = logfile)

            #saving GO
            if current_value < best_obj - epsilon:
                best_obj = current_value
                print(" *", file = logfile)
                #printPointFromModel(mymodel)
                feasible = True
                StorePoint(mymodel, bestpoint, labels)
            else:
                print(file = logfile)
            
            #start local search (perturbation of the current point)
            while (no_improve < max_no_improve):
                
                perturb_point_adj(mymodel, pert)
                results =localsolver.solve(mymodel)
                obj = mymodel.obj()

                if check_if_optimal(results):
                    #improving on current center
                    if obj < current_value - epsilon:
                        current_value = obj
                        print(algo_name + " Trial ", it, " no_improve ", no_improve, " current value ", current_value, end ='', file = logfile)
                        #no load needed - in model there is already the perturbed point
                        no_improve = 0
                        #improving also on global solution
                        if obj < best_obj - epsilon:
                            best_obj = obj
                            print(" *", file = logfile)
                            feasible = True
                            StorePoint(mymodel, bestpoint, labels)
                        else:
                            print(file = logfile)
                    else:
                        #restoring current center
                        LoadPoint(mymodel, currentcenter)
                        print(algo_name + " ", it, " no_improve ", no_improve, " noImprovingStep", file = logfile)
                        no_improve += 1
        else:
            print(algo_name + " ", it, " no_improve ", no_improve, "No feasible solution", file = logfile)

    if feasible == True:
        print(algo_name + " Best record found  {0:8.4f}".format(best_obj))
        LoadPoint(mymodel, bestpoint)
        printPointFromModel(mymodel)
    else:
        print(algo_name + " No feasible solution found by local solver")
        
    print("Multi:Total number of feasible solutions ", nb_solution)

    return feasible


# this function performs a timed version of multi trial MBH
def MBH_MultiTrial_timed(mymodel, time_limit, gen, localsolver, labels,
        max_no_improve, pert, delta,
        logfile = None, epsilon = 10**-4):

    algo_name = "MBH:Trial"
    best_obj = 10000 #put a reasonable value bound for the objective
    bestpoint = {} #dictionary to store the best solution
    current_value = best_obj
    currentcenter = {} #dictionary to store the current center (for pertubation step)
    
    feasible = False
    time_start = time.time()
    it = 0
    
    while time.time()-time_start < time_limit :
        it+=1
        no_improve = 0
        nb_solution = 0

        random_point(mymodel, gen)

        # local search
        results = localsolver.solve(mymodel)

        # a first feasible solution is found
        if check_if_optimal(results):
            nb_solution += 1  # couting feasible iterations
            current_value = mymodel.obj()
            StorePoint(mymodel, currentcenter, labels)
            
            print(algo_name + " ", it, " starting center "," current value ", current_value, end = '', file = logfile)

            #saving GO
            if current_value < best_obj - epsilon:
                best_obj = current_value
                print(" *", file = logfile)
                #printPointFromModel(mymodel)
                feasible = True
                StorePoint(mymodel, bestpoint, labels)
            else:
                print(file = logfile)
            
            #start local search (perturbation of the current point)
            while (no_improve < max_no_improve):
                
                perturb_point(mymodel, pert)
                results =localsolver.solve(mymodel)
                obj = mymodel.obj()

                if check_if_optimal(results):
                    #improving on current center
                    if obj < current_value - epsilon:
                        current_value = obj
                        print(algo_name + " Trial ", it, " no_improve ", no_improve, " current value ", current_value, end ='', file = logfile)
                        #no load needed - in model there is already the perturbed point
                        no_improve = 0
                        #improving also on global solution
                        if obj < best_obj - epsilon:
                            best_obj = obj
                            print(" *", file = logfile)
                            feasible = True
                            StorePoint(mymodel, bestpoint, labels)
                        else:
                            print(file = logfile)
                    else:
                        #restoring current center
                        LoadPoint(mymodel, currentcenter)
                        print(algo_name + " ", it, " no_improve ", no_improve, " noImprovingStep", file = logfile)
                        no_improve += 1
        else:
            print(algo_name + " ", it, " no_improve ", no_improve, "No feasible solution", file = logfile)

    if feasible == True:
        print(algo_name + " Best record found  {0:8.4f}".format(best_obj))
        LoadPoint(mymodel, bestpoint)
        printPointFromModel(mymodel)
    else:
        print(algo_name + " No feasible solution found by local solver")
        
    print("Multi:Total number of feasible solutions ", nb_solution)

    return feasible