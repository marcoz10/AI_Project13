# solve_itc_baseline_csp.py: This python script formulates the data from ITC-2007 Course Timetabling Problem as a CSP
#                            in terms of the AIMA Code csp.Problem then runs Backtracking Search (and other algorithms)
#                            to find a solution

# TODO:
# - test the baseline approach on the harder problems when applying the curriculum constraints
# - finish and test the verifier
# - move the display stuff to csp_utils.py ?
# - re-org the code directory, and add the AIMA code (?)
#   - csp, ga, utils, aima, misc ???

# import standard packages
from timeit import default_timer as timer
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import pandas as pd

# *** set path to the AIMA code on your system ***
# sys.path.append("/users/brucks/source/aima")
sys.path.append("../aima")
sys.path.append("../utils")
sys.path.append("../ga")
sys.path.append("../csp")
import csp
from itc_ga_framework import init_population, genetic_algorithm
# import search

# import our code (in the same directory as this file)
from csp_utils import forward_checking, constraint_different_values, constraint_different_timeslots
from csp_utils import display_solution, display_solution_in_table
from read_itc_data_file import read_itc_data_file
from timetabling_csp import TimetablingCSP
from timeslot_csp import TimeSlot
from verify_solution import verify_solution, score_solution, fitness_function
from solve_itc_baseline_csp import set_up_csp

import timeit

#Fitness performance testing
def perf_test(file_name):    
    SETUP_CODE ='''
file_name = "'''+file_name+'''"
from itc_ga_framework import init_population
from solve_itc_baseline_ga import set_up_csp
from verify_solution import score_solution
variables, domains, constraints, curricula, time_slots = set_up_csp(file_name)
population = init_population(100, variables, domains)'''
    TEST_CODE = '''
list(map(lambda x: score_solution(file_name, x), population))'''
    print(timeit.timeit(TEST_CODE,SETUP_CODE, number = 10))
    
    SETUP_CODE2 ='''
file_name = "'''+file_name+'''"
from itc_ga_framework import init_population
from solve_itc_baseline_ga import set_up_csp
from read_itc_data_file import read_itc_data_file
from verify_solution import fitness_function
variables, domains, constraints, curricula, time_slots = set_up_csp(file_name)
courses, rooms, num_days, periods_per_day, unavail_constraints, curricula = read_itc_data_file(file_name)    
population = init_population(100, variables, domains)'''
    TEST_CODE2 = '''
list(map(lambda x: fitness_function(courses, rooms, curricula, x), population))'''
    print(timeit.timeit(TEST_CODE2,SETUP_CODE2, number = 10))
    
    variables, domains, constraints, curricula, time_slots = set_up_csp(file_name)
    courses, rooms, num_days, periods_per_day, unavail_constraints, curricula = read_itc_data_file(file_name)
    population = init_population(100, variables, domains)
    
    fitnessOld = list(map(lambda x: score_solution(file_name, x), population))
    print(sum(fitnessOld))
    
    fitnessNew = list(map(lambda x: fitness_function(courses, rooms, curricula, x), population))
    print(sum(fitnessNew))
    
    print(fitnessOld == fitnessNew)
    
    
def main_func(file_name, output_file=None):
    print ('Performing GA Analysis on '+file_name)
    # Read in the ITC data file and do the pre-process necessary to convert the raw data into
    # variables, domains and constraints
    variables, domains, constraints, curricula, time_slots = set_up_csp(file_name)
    courses, rooms, num_days, periods_per_day, unavail_constraints, curricula = read_itc_data_file(file_name)
    
    population = init_population(100, variables, domains)
    
    start = timer()
    result, stats = genetic_algorithm(population, lambda x: fitness_function(courses, rooms, curricula, x), domains, ngen=100, f_thres=0)
    end = timer()
    print('GA took {:.1f} seconds'.format(end - start)) # Time in seconds, e.g. 5.38091952400282

    display_solution_in_table(result, time_slots, output_file)
    
    df = pd.DataFrame(stats)
    fig = plt.figure(1)
    ax = plt.subplot(111)
    ax.plot(df['generation'], df['max'], label='Maximum Fitness')
    ax.plot(df['generation'], df['mean'], label='Mean Fitness')
    ax.plot(df['generation'], df['min'], label='Minimum Fitness')
    ax.legend(loc='lower right')
    ax.set_ylabel('Fitness Score')
    ax.set_xlabel('Generation')
    plt.title("Generational Fitness in GA")
    plt.show()

# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    
    # if you want to generate an output file of the schedule
    # output_file = '/Users/brucks/Desktop/baseline_comp01.txt'
    output_file = None  # if not
    
    if len(sys.argv)==2 and os.path.exists(sys.argv[1]):
        file_name = sys.argv[1]
        main_func(file_name, output_file)
    elif (sys.argv)==3 and os.path.exists(sys.argv[1]) and sys.argv[2] == 'test':
        file_name = sys.argv[1]
        perf_test(file_name)
    else:
        file_name = '../../Data/ITC-2007/comp01.ctt.txt'
        main_func(file_name, output_file)

    

