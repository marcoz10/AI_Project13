# solve_itc_randomly.py: This python script extracts the dat from an ITC-2007 Course Timetabling Problem input file,
#                        constructs the CSP variables, domains and constraints and then generates a random "complete
#                        assignment" by assigning every variable to a randomly selected item from its domain.
#
#                        The assignment will almost certainly not be a solution as the assignement will not be
#                        consistent (not all constraints will be met).
#
#                        The main value is this approach is to test the verify_solution() function and perhaps as a
#                        starter for generating the population for the EA/GA approach


# import standard packages
import numpy as np
import sys

# set the path and import our code
sys.path.append("../utils")
from csp_utils import display_solution, display_solution_in_table
from solve_itc_baseline_csp import set_up_csp
from verify_solution import verify_solution

# -------------------------------------------------------------------------------------
def main_func(file_name, output_file=None):

    # Read in the ITC data file and do the pre-process necessary to convert the raw data into
    # variables, domains and constraints
    variables, domains, constraints, curricula, time_slots = set_up_csp(file_name)

    # -------------------------------------------------------------------------------------
    # generate a random solution, which should fail but will help for testing the verifier
    # np.random.seed(0)
    solution = {}
    for v in variables:
        # randomly choose an assignment from this variable's domain
        ind = np.random.choice(len(domains[v]))
        solution[v] = domains[v][ind]

    if solution:
        # display_solution(solution)
        display_solution_in_table(solution, time_slots, output_file)
    else:
        print('*** NO SOLUTION RETURNED ***')

    # run the verifier
    solved, solution_score = verify_solution(file_name, solution, verbose=True)
    print('Solution Verified:', solved, ', score:',solution_score)

# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    file_name = '../../Data/ITC-2007/comp03.ctt.txt'
    # file_name = '../../Data/ITC-2007/toy_prob.ctt.txt'

    # if you want to generate an output file of the schedule
    # output_file = '/Users/brucks/Desktop/random_comp01.txt'
    output_file = None  # if not

    main_func(file_name, output_file)
