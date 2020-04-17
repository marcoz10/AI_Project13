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

# import our code (in the same directory as this file)
from csp_utils import display_solution, display_solution_in_table
from solve_itc_baseline_csp import set_up_csp
# from verify_solution import verify_solution

# -------------------------------------------------------------------------------------
def main_func(file_name):

    # Read in the ITC data file and do the pre-process necessary to convert the raw data into
    # variables, domains and constraints
    variables, domains, constraints, curricula, time_slots = set_up_csp(file_name)

    # -------------------------------------------------------------------------------------
    # generate a random solution, which should fail but will help for testing the verifier
    solution = {}
    for v in variables:
        # randomly choose an assignment from this variable's domain
        ind = np.random.choice(len(domains[v]))
        solution[v] = domains[v][ind]

    if solution:
        display_solution(solution)
        display_solution_in_table(solution, time_slots)
    else:
        print('*** NO SOLUTION RETURNED ***')

    # run the verifier
    # STILL IN PROGRESS
    # solved, num_files = verify_solution(file_name, solution)



# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    file_name = '../Data/ITC-2007/comp01.ctt.txt'
    # file_name = '../Data/ITC-2007/toy_prob.ctt.txt'

    main_func(file_name)
