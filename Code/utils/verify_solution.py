# verify_solution.py: This python script extracts data from ITC-2007 Course Timetabling Problem and determines if a
#                            solution meets all of the constraints

# I am thinking that we use this function for 2 purposes:
# - to verify a solution of course
# - to compute a score for each solution, under the assumption that it might be used as a fitness function for EA/GA

# import our code (in the same directory as this file)
from read_itc_data_file import read_itc_data_file

HARD_FAIL_SCORE = 1e6
HARD_CONSTRAINT_PENALTY = 1
SOFT_CONSTRAINT_PENALTY = 0.5

# -------------------------------------------------------------------------------------
def verify_solution(file_name, solution, verbose=False):
    """ Verifies / scores a solution to an Timetabling CSP problem
        Note: if the 'solution' is not complete (not all variables are assigned) the returned score will be HARD_FAIL_SCORE

    :param file_name:  path to the ITC data file that specifies the problem
    :param solution:  a solution to the problem that is to be verified / scored
    :param verbose:  flag indicating you want to see a bunch of info printed out
    :return:  verified (bool): True indicates that the solution meets all contraints
              num_fails (int): The number of failures in the solution
    """

    # Read in the ITC data file
    courses, rooms, num_days, periods_per_day, unavail_constraints, curricula = read_itc_data_file(file_name)

    # Need to verify the provide solution based on the input data. These are done and mostly tested:
    # - check that all courses have an assignment
    # - check that all courses are assigned to rooms with adequate capacity
    # - check that no room-timeslot combination has more than once course assigned

    # These still need to be done:
    # - a solution contains only one assignment for each course
    # - unavailability constraints

    # ---------------------------------------------------------------------------------
    # First, check that all courses have an assignment and the the solution only assigns
    hard_fail = False
    if verbose:
        print('checking for complete assignment ...',)
    for c in courses:
        if c not in solution.keys():
            hard_fail = True
            break

    if hard_fail:
        if verbose:
            print('HARD FAIL: not all variables are assigned ...', )
        return False, HARD_FAIL_SCORE

    # should also check that solution contains only one assignment for each course, since if we get here all variables
    # have been assigned, we only need to verify that the  number of assignments in the solution == number of variables
    if len(solution) != len(courses):
        if verbose:
            print('HARD FAIL: number of assignments in the solution != number of variables ...', )
        return False, HARD_FAIL_SCORE

    # keep a count of the number of num_fails as a score
    total_score = 0

    # ---------------------------------------------------------------------------------
    # 2: check that all courses are assigned to rooms with adequate capacity
    if verbose:
        print('checking room capacity vs course enrollment ...',)
    num_fails = 0
    for s in solution:
        assigned_room = solution[s][0]
        room_capacity = rooms[assigned_room]
        course_enrollment = courses[s][3]
        if course_enrollment > room_capacity:
            num_fails += 1
            total_score -= HARD_CONSTRAINT_PENALTY
            print('course ',s,': enrollment=',course_enrollment, ', assigned room=', assigned_room, ', capacity=', room_capacity)

    if verbose:
        if num_fails > 0:
            print('FAIL(', num_fails, ')')
        else:
            print('PASS')

    # ---------------------------------------------------------------------------------
    # 3: check that no room-timeslot is multiply occupied
    # fails = find_occupied_slots(solution, verbose=False)
    num_fails = 0
    if verbose:
        print('checking that no room-timeslot is multiply occupied ...',)

    # have to do this room-by-room, so first get the set of rooms
    all_rooms = []
    for s in solution:
        room = solution[s][0]
        all_rooms.append(room)

    all_rooms = list(set(all_rooms))
    # print('all_rooms:',all_rooms)

    for r in all_rooms:
        # print('Room ',r)
        occupied = {}
        for s in solution:
            course = s
            room = solution[s][0]
            ts = solution[s][1]
            if r == room:
                if ts not in occupied:
                    occupied[ts] = [course]
                else:
                    occupied[ts].append(course)
        # print('Occupied:')
        for o in occupied:
            # print(occupied[o])
            # now we need to look for an occupied rooms with more than one entry ...
            # add to the count if there is more than one ...
            penalty = len(list(occupied[o]))-1
            if penalty > 0:
                num_fails += penalty
                total_score -= HARD_CONSTRAINT_PENALTY * penalty

    if verbose:
        if num_fails > 0:
            print('FAIL(', num_fails, ')')
        else:
            print('PASS')

    # now we need to look at the curricula constraints
    # if verbose:
    if verbose:
        print('checking curricula constraints ...',)
    # walk through each curriculum
    num_fails = 0
    for c in curricula:
        if verbose:
            print('curricula:', c, ':', curricula[c])
        # get the courses and check each against the rest to see are in the same room and overlap timeslots
        courses = curricula[c]
        num_courses = len(courses)
        for i in range(0,num_courses):
            for j in range(i+1, num_courses):
                a1 = solution[courses[i]]
                a2 = solution[courses[j]]
                if a1[0] != a2[0] or not a1[1].overlaps(a2[1]):
                    # different room
                    continue
                elif not a1[1].overlaps(a2[1]):
                    # same room but times do not overlap
                    continue
                else:
                    if verbose:
                        print('\t',courses[i], '(', a1, '),', courses[j], '(', a2, ') failure')
                    num_fails += 1
                    total_score -= SOFT_CONSTRAINT_PENALTY

    if verbose:
        if num_fails > 0:
            print('FAIL(', num_fails, ')')
        else:
            print('PASS')

    return total_score == 0, total_score


