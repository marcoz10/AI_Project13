# contains functions from AIMA csp.py that we need to over-ride so they work with our TimetablingCSP() class as well
# as a few other odds and ends

# you may need to 'conda install tabulate' for this package (which makes a nice tabular printout)
from tabulate import tabulate

import csp
# -------------------------------------------------------------------------------------
# in general: a constraint function f(A, a, B, b) that returns true if two variables
#             A, B satisfy the constraint when they have values A=a, B=b

# constraint: A, B have "different" assignments, the meaning of different is defined below
def constraint_different_values(A, a, B, b, curricula):
    # note that this function does not need the argument 'curricula' but we need to maintain a consistent function
    # signature across all the constraint functions

    # for this problem, different means:
    # - the room assignments are different, or
    # - the days assigned are different, or
    # - if the room assignments are the same and there are days in common to both assignment (e.g. MW vs M)
    #   then the times to do not overlap
    if (a[0] != b[0]): # room assignment
        return True
    return not (a[1].overlaps(b[1]))
    # return (a != b)

# -------------------------------------------------------------------------------------
# constraint: A, B have different timeslots within a curriculum
def constraint_different_timeslots(A, a, B, b, curricula):
    for c in curricula:
        if A in curricula[c] and B in curricula[c]:
            if a[1].overlaps(b[1]):
                return False
    return True


# -------------------------------------------------------------------------------------
def forward_checking(csp, var, value, assignment, removals):
    """Prune neighbor values inconsistent with var=value."""
    csp.support_pruning()
    for B in csp.neighbors[var]:
        if B not in assignment:
            # for b in csp.curr_domains[B][:]:
            for b in csp.curr_domains[B]:
                # *** AIMA code makes the call below, but really the call should be to the fail_constraints function ***
                # if not csp.constraints(var, value, B, b):
                if csp.fail_constraints(var, value, B, b):
                    csp.prune(B, b, removals)
            if not csp.curr_domains[B]:
                return False
    return True


# -------------------------------------------------------------------------------------
# backtracking_search: so I can mess with the function and try to assess how well it does ...
def backtracking_search(csp, select_unassigned_variable=csp.first_unassigned_variable,
                        order_domain_values=csp.unordered_domain_values, inference=csp.no_inference):
    """[Figure 6.5]"""

    def backtrack(assignment, count=0):
        if len(assignment) == len(csp.variables):
            print('count:', count)
            return assignment
        var = select_unassigned_variable(assignment, csp)
        for value in order_domain_values(var, assignment, csp):
            if 0 == csp.nconflicts(var, value, assignment):
                csp.assign(var, value, assignment)
                removals = csp.suppose(var, value)
                if inference(csp, var, value, assignment, removals):
                    result = backtrack(assignment, count+1)
                    if result is not None:
                        return result
                csp.restore(removals)
        csp.unassign(var, assignment)
        return None

    result = backtrack({})
    assert result is None or csp.goal_test(result)
    return result

# -------------------------------------------------------------------------------------
def display_solution(solution, file_name=None):

    if file_name:
        file = open(file_name,'w')
        file.write('Course Code, Room, Days, Start Time, End Time\n')
        for s in solution:
            room = solution[s][0]
            ts = solution[s][1]
            start = ts.start
            stop = ts.stop
            days = ''.join(ts.days)
            file.write('%s,%s,%s,%04d,%04d\n' % (s, room, days, start, stop))
        file.close()


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
def display_solution_in_table(solution, time_slots, file_name=None):

    if file_name:
        file = open(file_name,'w')

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

    times = sorted(times)

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
        print('Schedule for room %s\n' % (r))
        if file_name:
            file.write('Schedule for room %s\n' % (r))

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
        print('\n------------------------------------------------------\n')
        if file_name:
            file.write(tabulate(all_values, headers=headers))
            file.write('\n------------------------------------------------------\n')

    if file_name:
        file.close()
