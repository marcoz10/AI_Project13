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
import numpy as np
import sys
import os
from timeit import default_timer as timer

# *** set path to the AIMA code on your system ***
sys.path.append("../aima")
sys.path.append("../utils")
import csp

# import our code (in the same directory as this file)
from csp_utils import forward_checking, constraint_different_values, constraint_different_timeslots
from csp_utils import display_solution, display_solution_in_table
from read_itc_data_file import read_itc_data_file
from timetabling_csp import TimetablingCSP
from timeslot_csp import TimeSlot
from verify_solution import verify_solution


# USE_ONE_DAY_CLASSES = True

# -------------------------------------------------------------------------------------
def define_all_timeslots():
    days2 = [['M', 'W'], ['T', 'R']]
    days1 = ['M', 'T', 'W', 'R', 'F']
    times2_start = [700, 830, 1000, 1130, 1300, 1430, 1600, 1730, 1900]  # these are 1:15 minute classes
    times2_stop = [815, 945, 1115, 1245, 1415, 1545, 1715, 1845, 2015]
    # start and stop for one-day classes, evening times first
    times1_start = [1600, 1900, 700, 1000, 1300]  # these are 2:50 minute classes
    times1_stop = [1850, 2150, 950, 1250, 1550]

    # build a list of all the time periods we could use in this order:
    # use all 2-day ones first, then add single-day evening, then add single day day-time) ???
    all_timeslots = []
    for d in days2:
        for start, stop in zip(times2_start, times2_stop):
            all_timeslots.append(TimeSlot(d, start, stop))
    for d in days1:
        for start, stop in zip(times1_start, times1_stop):
            all_timeslots.append(TimeSlot(d, start, stop))

    return all_timeslots

# -------------------------------------------------------------------------------------
def set_up_csp(file_name, verbose=False):
    # Read in the ITC data file and do the pre-process necessary to convert the raw data into
    # variables, domains and constraints ... we might want to reuse this chunk of code

    courses, rooms, num_days, periods_per_day, unavail_constraints, curricula = read_itc_data_file(file_name)

    # ITC data has days and time slots as separate items, but for us it makes a lot more sense to map to a combo
    # print('courses:', courses)
    # print('rooms:', rooms)
    # print('num_days:', num_days)
    # print('periods_per_day:', periods_per_day)
    # print('unavail_constraints:', unavail_constraints)
    # print('curricula:',curricula)

    # -------------------------------------------------------------------------------------
    # data pre-processing steps:
    #   - convert the course day (in integer) and time-slot (also an integer) into a TimeSlot instance
    #   - do the same with the unavailability constraints

    # convert the day and time values into a TimeSlot instance
    # options: we can have 1-day per week classes, 2-day per week classes (MW or TR), 3-days per week (MWF)
    #          for now we will just have 2-day per week and we will add in 1-day per week if the problem space
    #          gets too large

    # get all the available timeslots
    all_timeslots = define_all_timeslots()

    # sanity check: make sure the number of courses is not greater than the number of available timeslots * # rooms
    # day-time slots * number of rooms
    if len(courses) > len(all_timeslots) * len(rooms):
        print('Error: too many courses for the combination of day-times and rooms')
        sys.exit()

    # select the needed number of timeslots
    time_slots = all_timeslots[:periods_per_day * num_days]

    # note: the input problem files sometimes have 6 days allowed for instruction, but we are only scheduling courses
    #       during 5 days; this is an issue when a course has an unavailability on day 5 or 6; the solution for now is
    #       to just ignore those unavailability constraints

    # setting up the blocked timeslots is a bit of a mess ... the problem files use integers for day and for time
    # in order to be cooler and more clever, we mapped that to MW or TR or M at some actual time ... so we need to take
    # the day number and the time number into a single number and then block that timeslot
    blocked_timeslots = {} # use a dict; key = course, value = list of TimeSlot items
    for c in unavail_constraints:
        blocked_timeslots[c] = []
        for item in unavail_constraints[c]:
            day = item[0]
            time = item[1]
            ts_number = day * (num_days-1) + time
            # sometimes we have an issue when we are adjusting the problem to make it harder that we have blocked
            # timeslots that refer to a day or time that is not in our set, so skip those
            if ts_number >= len(time_slots):
                continue
            blocked_timeslots[c].append(time_slots[ts_number])

    '''
    # convert the unavailability constraints into TimeSlot instances
    # unavail_constraints is a dict with entries like: 'c0025': [(2, 2), (2, 3) ... ]
    blocked_timeslots = {} # use a dict; key = course, value = list of TimeSlot items
    for c in unavail_constraints:
        blocked_timeslots[c] = []
        for item in unavail_constraints[c]:
            # item is a tuple of (day number, time period number)
            if item[0] >= len(days1):
                continue
            this_day = days1[item[0]]
            the_days = []
            # need to handle this carefully since our time slots are MW, TR and maybe M->F
            # so if the blocked day is W, then we need to block both W and MW ...
            for d in days2:
                if this_day in d:
                    the_days.append(d)

            # get start and stop times for the specified time slot
            time_num = item[1]
            start = times2_start[time_num]
            stop = times2_stop[time_num]
            for d in the_days:
                blocked_timeslots[c].append(TimeSlot(d, start, stop))
    '''
    if (verbose):
        print('blocked_timeslots:')
        for b in blocked_timeslots:
            print(b, ':', blocked_timeslots[b])


    # -------------------------------------------------------------------------------------
    # variables: a dict; key: variable name; value: tuple (list???) of a the values assigned to each variable attribute
    # variables: a dictionary of {var:(attribute1, ...)}
    # attr_names = ['Room', 'Day-Time']
    variables = {}
    for c in courses:
        variables[c] = (None, None)

    # -------------------------------------------------------------------------------------
    # apply the unary constraints; since they only constrain one attribute of a variable we will do that to limit the
    # domains of some variable attributes before constructing the Timetabling CSP problem

    # apply unary constraints based on room capacities
    # each course has a max number of students (element 3 in the list), each room has a max capacity
    # first let's make a list or dict of the domains
    room_violation = {}
    for c in courses:
        max_students = courses[c][3]
        # now look at all the rooms and see where we have a violation
        for r in rooms:
            if rooms[r] < max_students:
                if c not in room_violation:
                    room_violation[c] = [r]
                else:
                    room_violation[c].append(r)

    # now create the domain set for the 'Rooms' attribute for each variable
    room_domain_all = list(rooms.keys())
    room_domains = {}
    for v in variables:
        if v in room_violation:
            room_domains[v] = [r for r in room_domain_all if r not in room_violation[v]]
        else:
            room_domains[v] = room_domain_all
    if (verbose):
        print('room_domains:', room_domains)

    # now create the domain set for the 'Day-Time' attribute for each variable,
    # taking into account the blocked time slots for any course
    day_time_domains = {}
    for v in variables:
        if v in blocked_timeslots:
            # walk through all the available time slots and keep all that are not included
            # in the set of blocked time slots for this variable
            day_time_domains[v] = []
            for ts in time_slots:
                good = True
                for tb in blocked_timeslots[v]:
                    if ts == tb:
                        good = False
                if good:
                    day_time_domains[v].append(ts)
        else:
            # this variable has now unavailable time slots, so add them all to the domain
            day_time_domains[v] = time_slots

    if (verbose):
        print('day_time_domains:')
        for dt in day_time_domains:
            print(dt, day_time_domains[dt])

    # -------------------------------------------------------------------------------------
    # domains: a dict; key: variable name; value: list of a tuple of possible assignments for each variable attribute
    # for now, all courses have the same domains

    # for the current approach, we need to create the cartesian product of all the domains of each attribute
    # this is not going to be very feasible for larger problems
    domains = {}
    for x in variables:
        attr_prod = []
        for r in room_domains[x]:
            for dt in day_time_domains[x]:
                attr_prod.append((r, dt))
        domains[x] = attr_prod

    if (verbose):
        for d in domains:
              print('domain for:', d, ':', domains[d])

    # -------------------------------------------------------------------------------------
    # constraints   A list of functions f(A, a, B, b) that returns true if two variables A, B satisfy the constraint
    #               when they have values A=a, B=b
    # we have 2 constraints: 1) all variables have different assignments, 2) all courses in a curricula have
    # different time slots (even if they are in different rooms)
    constraints = [constraint_different_values, constraint_different_timeslots]

    return variables, domains, constraints, curricula, time_slots

# -------------------------------------------------------------------------------------
def main_func(file_name, output_file=None):

    # Read in the ITC data file and do the pre-process necessary to convert the raw data into
    # variables, domains and constraints
    variables, domains, constraints, curricula, time_slots = set_up_csp(file_name)

    # set up the problem
    my_problem = TimetablingCSP(variables, domains, constraints, curricula)

    # try it with min_conflicts
    # print('Solving with min_conflicts')
    # solution = csp.min_conflicts(my_problem, max_steps=100)
    # display_solution(solution)
    # display_solution_in_table(solution, time_slots, output_file)
    # print('--------------------------\n')
    # sys.exit()

    # reset the problem
    my_problem = TimetablingCSP(variables, domains, constraints, curricula)

    # try it with backtracking_search
    # current options for backtracking_search:
    #   select_unassigned_variable = [first_unassigned_variable,mrv]
    #   order_domain_values = [unordered_domain_values, lcv]
    #   inference = [no_inference, forward_checking, mac]
    #
    print('Solving with backtracking_search')
    start = timer()
    solution = csp.backtracking_search(my_problem, select_unassigned_variable=csp.first_unassigned_variable,
                                       order_domain_values=csp.unordered_domain_values,
                                       inference=csp.no_inference)
    end = timer()

    if solution:
        # display_solution(solution)
        display_solution_in_table(solution, time_slots, output_file)
    else:
        print('*** NO SOLUTION RETURNED ***')

    # let's compute some measure of the difficulty of the problem ...
    # *** STILL a work in progress
    '''
    # maybe min, median and avg number of domains (after unary constraints applied) per variable
    # load the number of domains for each variable into a list
    domains_xx = np.array([len(domains[d]) for d in domains])
    print('domains_xx:', domains_xx)
    print('min of domains: ', np.min(domains_xx))
    print('avg of domains: ', np.mean(domains_xx))
    print('med of domains: ', np.median(domains_xx))
    print('number of variables = ', len(variables))

    # compute a problem score ...
    complexity = np.mean(domains_xx) / len(variables)
    # print('problem complexity = ', complexity)

    # how did the algorithm do ???
    print('number of assignments = ', my_problem.nassigns)
    print('number of un-assignments = ', my_problem.num_unassigns)
    '''

    # run the verifier
    solved, solution_score = verify_solution(file_name, solution, verbose=True)
    print('Solution Verified:', solved, ', score:',solution_score)
    print('Solver time:', end - start)

# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv)==2 and os.path.exists(sys.argv[1]):
        file_name = sys.argv[1]
    else:
        file_name = '../../Data/ITC-2007/comp01.ctt.txt'
    # file_name = '../../Data/ITC-2007/toy_prob.ctt.txt'

    # if you want to generate an output file of the schedule
    # output_file = '/Users/brucks/Desktop/baseline_comp01.txt'
    output_file = None  # if not

    main_func(file_name, output_file)
