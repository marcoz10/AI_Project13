# test_itc_basic_cpp.py
#
# This script uses the backtracking_search from AIMA CSP to solve the simplest of Timetabling Problems: the ITC 2007
# Toy Problem, trimmed down to just assigning each course to a room and day
#
# In order to use the AIMA CSP code functions without any modification of sub-classing, we just concatenate the rooms
# and times into a single string. This is needed since the AIMA CSP code requires that the variables be atomic.

# An effort is underway to extend the AIMA CSP code to handle more complex variables and multi-dimensional domains

import csp

from copy import deepcopy

# -------------------------------------------------------------------------------------
# constraints A function f(A, a, B, b) that returns true if two variables
#                     A, B satisfy the constraint when they have values A=a, B=b
# but it seems like we could just use the two variables A, B
def constraint_different_values(A, a, B, b):
    # return true if a and b are different
    return (a != b)

# -------------------------------------------------------------------------------------
if __name__ == "__main__":

    # fake some data, worry about parsing the file later
    courses = ['SceCosC', 'ArcTec', 'TecCos', 'Geotec']
    rooms = ['A', 'B']
    days = list(range(5))
    periods = list(range(5))
    print('courses:', courses)
    print('days:', days)
    print('rooms:', rooms)

    # -------------------------------------------------------------------------------------
    # variables: A list of variables; each is atomic (e.g. int or string).
    variables = courses

    # -------------------------------------------------------------------------------------
    # domains: A dict of {var:[possible_value, ...]} entries.
    # for this simple problem, all courses have the same domains, which is the cartesian product of the rooms and days
    all_domains = ['r'+r+'-d'+str(d) for r in rooms for d in days]
    domains = {}
    for v in variables:
        domains[v] = all_domains #(rooms, days)
    print('domains:', domains)

    # -------------------------------------------------------------------------------------
    # neighbors: A dict of {var:[var,...]} that for each variable lists the other variables that
    #            participate in constraints
    # for this simple problem, all courses are neighbors
    neighbors = {}
    for v in variables:
        neigh = deepcopy(variables)
        # neighbors = all_var_names.copy()
        neigh.remove(v)
        neighbors[v] = neigh

    # -------------------------------------------------------------------------------------
    # constraints   A function f(A, a, B, b) that returns true if two variables A, B satisfy the constraint
    #               when they have values A=a, B=b
    # at some point we will need to be able to supply a list of constraints, or maybe we just combine multiple into
    # a single function
    constraints = constraint_different_values

    # set up the problem
    my_problem = csp.CSP(variables, domains, neighbors, constraints)

    print('my_problem.variables:', my_problem.variables)
    print('my_problem.domains:', my_problem.domains)
    print('my_problem.constraints:', my_problem.constraints)
    print('my_problem.neighbors:', my_problem.neighbors)

    # try it with min_conflicts
    solution = csp.min_conflicts(my_problem, max_steps=10)
    print('MC solution:', solution)

    # try it with backtracking_search
    solution = csp.backtracking_search(my_problem)
    print('BT solution:', solution)

