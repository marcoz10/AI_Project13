# solve_itc_baseline_csp.py: This python script formulates the data from ITC-2007 Course Timetabling Problem as a CSP
#                            in terms of the AIMA Code csp.Problem then runs Backtracking Search (and other algorithms)
#                            to find a solution

# Need to work on the rest of the constraints ...
# Hard Constraints:
# x all courses must be scheduled
# x courses assigned to different room-day-time combinations
# - teacher conflicts: a teach can not teach more than one course in the same day-time slot
# x course availability
# x courses assigned to rooms with adequate capacity (this is a unary constraint on course assignment to rooms)

# Soft Constraints:
# - minimum working days
# - curriculum compactness
# - room stability

# import standard packages
import numpy as np
import sys

# *** set path to the AIMA code on your system ***
sys.path.append("/users/brucks/source/aima")
import csp

# import our code (in the same directory as this file)
from csp_utils import forward_checking, constraint_different_values, constraint_different_timeslots
from read_itc_data_file import read_itc_data_file
from timetabling_csp import TimetablingCSP
from timeslot_csp import TimeSlot


USE_ONE_DAY_CLASSES = False

# -------------------------------------------------------------------------------------
def display_solution(solution, problem):
    # for a first cut, let's just print it out day by day ...
    # print('solution:', solution)

    # solution will be a dictionary where the key is the course name / ID
    # of the form: solution: {'c0072': ('F', TH-1430-1545), 'c0016': ('B', H-0700-0950), ...

    # let's try to refactor this into time slots, an array of tuples (time_slot, classroom, course)
    time_slots = []
    for s in solution:
        room = solution[s][0]
        ts = solution[s][1]
        time_slots.append((ts, room, s))

    # sort the list by element 0 (time slot)
    time_slots.sort(key=lambda x: x[0])
    for t in time_slots:
        print(t)

# -------------------------------------------------------------------------------------
def display_solution_in_table(solution, problem, time_slots):
    from tabulate import tabulate
    # let's just print headers and the time slots with a random string in each
    days = ['M','T','W','R','F']
    headers = ['Time'] + days

    # get the set of time slots as a string
    times = []
    for ts in time_slots:
        # make a start-stop string
        time_str = "%04d-%04d" % (ts.start, ts.stop)
        if time_str not in times:
            times.append(time_str)

    # print('in display_solution_in_table; times =')
    # for ts in times:
    #     print(ts)

    # need to get a schedule for each room ....
    all_rooms = []
    for s in solution:
        room = solution[s][0]
        if room not in all_rooms:
            all_rooms.append(room)

    for r in all_rooms:
        print('Schedule for room ', r)

        # now walk through the variable assignments in the solution and store the relevant elements of the solution in
        # a dictionary; key = time slot (string), value = list of len(days)
        table_values = {}
        for t in times:
            table_values[t] = [t] + len(days) * ['']

        # need to this for each room ...
        for s in solution:
            course = s
            room = solution[s][0]
            if r != room:
                continue
            ts = solution[s][1]
            time_str = "%04d-%04d" % (ts.start, ts.stop)

            # what time slot does this day-time go in
            time_ind = times.index(time_str)

            # what day(s) does this go in?
            for i,d in enumerate(days):
                for td in ts.days:
                    if d in td:
                        # append a string so we can see if we have multiple assignments
                        table_values[time_str][i+1] += (course + ' ')

        # now display the table
        all_values = []
        for t in times:
            all_values.append(table_values[t])

        print(tabulate(all_values, headers=headers))

# -------------------------------------------------------------------------------------
def main_func(file_name):
    # Read in the ITC data file and do the pre-process necessary to convert the raw data into
    # variables, domains and constraints
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
    days2 = [['M','W'], ['T','R']]
    days1 = ['M','T','W','R','F']
    times2_start = [700,830,1000,1130,1300,1430,1600,1730,1900] # these are 1:15 minute classes
    times2_stop = [815,945,1115,1245,1415,1545,1715,1845,2015]
    times1_start = [700,1000,1300,1600,1900] # these are 2:50 minute classes
    times1_stop = [950,1250,1550,1850,2150]

    # keep the specified number of time slots == periods_per_day times
    indices = list(range(0,periods_per_day))
    # np.random.shuffle(indices) # (choose which to keep at random?)
    times2_start = [times2_start[i] for i in indices]
    times2_stop =  [times2_stop[i] for i in indices]
    # print('times2_start:',times2_start)
    # print('times2_stop:',times2_stop)

    # convert into instances of class TimeSlot():
    time_slots = []
    for d in days2:
        for start,stop in zip(times2_start, times2_stop):
            time_slots.append(TimeSlot(d, start, stop))
    if USE_ONE_DAY_CLASSES:
        for d in days1:
            for start,stop in zip(times1_start, times1_stop):
                time_slots.append(TimeSlot(d, start, stop))

    # note: the input problem files sometimes have 6 days allowed for instruction, but we are only scheduling courses
    #       during 5 days; this is an issue when a course has an unavailability on day 5 or 6; the solution for now is
    #       to just ignore those unavailability constraints

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

    # print('blocked_timeslots:')
    # for b in blocked_timeslots:
    #     print(b, ':', blocked_timeslots[b])

    # first sanity check: make sure the number of courses is not greater than the number of available
    # day-time slots * number of rooms
    if len(courses) > len(time_slots) * len(rooms):
        print('Error: too many courses for the combination of day-times and rooms')
        sys.exit()

    # -------------------------------------------------------------------------------------
    # variables: a dict; key: variable name; value: tuple (list???) of a the values assigned to each variable attribute
    # variables: a dictionary of {var:(attribute1, ...)}
    attr_names = ['Room', 'Day-Time']
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
    # print('room_violation:', room_violation)

    # now create the domain set for the 'Rooms' attribute for each variable
    room_domain_all = list(rooms.keys())
    room_domains = {}
    for v in variables:
        if v in room_violation:
            room_domains[v] = [r for r in room_domain_all if r not in room_violation[v]]
        else:
            room_domains[v] = room_domain_all
    # print('room_domains:', room_domains)

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

    # print('day_time_domains:')
    # for dt in day_time_domains:
    #     print(dt, day_time_domains[dt])

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
    for d in domains:
          print('domain for:', d, ':', domains[d])

    # -------------------------------------------------------------------------------------
    # constraints   A list of functions f(A, a, B, b) that returns true if two variables A, B satisfy the constraint
    #               when they have values A=a, B=b
    # we have 2 constraints: 1) all variables have different assignments, 2) all courses in a curricula have
    # different time slots (even if they are in different rooms)
    constraints = [constraint_different_values, constraint_different_timeslots]

    # do something about the curricula constraints ... if 2 courses are in a curricula then they will have students
    # in common and should not (or can not) be offered in the same timeslot (even if the room is different)
    # set up the problem
    my_problem = TimetablingCSP(variables, attr_names, domains, constraints, curricula)

    # try it with min_conflicts
    # print('Solving with min_conflicts')
    # solution = csp.min_conflicts(my_problem, max_steps=100)
    # display_solution(solution, my_problem)
    # display_solution_in_table(solution, my_problem, time_slots)
    # print('--------------------------\n')
    # sys.exit()

    # reset the problem
    my_problem = TimetablingCSP(variables, attr_names, domains, constraints, curricula)

    # try it with backtracking_search
    # current options for backtracking_search:
    #   select_unassigned_variable = [first_unassigned_variable,mrv]
    #   order_domain_values = [unordered_domain_values, lcv]
    #   inference = [no_inference, forward_checking, mac]
    #
    print('Solving with backtracking_search')
    solution = csp.backtracking_search(my_problem, select_unassigned_variable=csp.mrv,
                                       order_domain_values=csp.lcv,
                                       inference=forward_checking)

    display_solution(solution, my_problem)
    display_solution_in_table(solution, my_problem, time_slots)

    # let's compute some measure of the difficulty of the problem ...
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
    print('problem complexity = ', complexity)

    # how did the algorithm do ???
    print('number of assignments = ', my_problem.nassigns)
    print('number of un-assignments = ', my_problem.num_unassigns)


# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    file_name = '../Data/ITC-2007/comp01.ctt.txt'
    # file_name = '../Data/ITC-2007/toy_prob.ctt.txt'

    main_func(file_name)
