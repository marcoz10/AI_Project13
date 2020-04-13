# read_itc_data_file.py: parse the ITC file format and return xxx#

import sys

# -------------------------------------------------------------------------------------
def read_itc_data_file(file_name):

    with open(file_name, 'r') as f:
        all_lines = f.readlines()
    # print(all_lines)

    # Let's grab info from each section
    # Header format:
    #   Name: ToyExample
    #   Courses: 4
    #   Rooms: 2
    #   Days: 5
    #   Periods_per_day: 4
    #   Curricula: 2
    #   Constraints: 8

    # Name
    words = all_lines[0].split()
    if words[0] == 'Name:':
        data_name = words[1]

    # Courses
    words = all_lines[1].split()
    if words[0] == 'Courses:':
        num_courses = int(words[1])

    # Rooms
    words = all_lines[2].split()
    if words[0] == 'Rooms:':
        num_rooms = int(words[1])

    # Days
    words = all_lines[3].split()
    if words[0] == 'Days:':
        num_days = int(words[1])

    # Periods_per_day
    words = all_lines[4].split()
    if words[0] == 'Periods_per_day:':
        periods_per_day = int(words[1])

    # Curricula
    words = all_lines[5].split()
    if words[0] == 'Curricula:':
        num_curricula = int(words[1])

    # Constraints
    words = all_lines[6].split()
    if words[0] == 'Constraints:':
        num_constraints = int(words[1])

    # print('name:', data_name)
    # print('courses:', num_courses)
    # print('rooms:', num_rooms)
    # print('days:', num_days)
    # print('periods_per_day:', periods_per_day)
    # print('curricula:', num_curricula)
    # print('constraints:', num_constraints)

    # assume for now that the header section is static and the start lines for other sections is based on the
    # numbers provided in the header
    course_section_start = 8 # line 9 in a text editor, but the array indexing starts at 0
    room_section_start = course_section_start + num_courses + 2
    curricula_section_start = room_section_start + num_rooms + 2
    unavail_section_start = curricula_section_start + num_curricula + 2

    # Courses Section
    # COURSES: course id, teacher id, (num days to schedule on, num lectures to be scheduled)?, max number of students
    # SceCosC Ocra 3 3 30
    # ArcTec Indaco 3 2 42
    # TecCos Rosa 5 4 40
    # Geotec Scarlatti 5 4 18

    words = all_lines[course_section_start].split()
    if words[0] != 'COURSES:':
        print('Error parsing COURSES section')
        sys.exit()

    courses = {}
    for i in range(num_courses):
        words = all_lines[course_section_start+i+1].split()
        courses[words[0]] = [words[1], int(words[2]), int(words[3]), int(words[4])]
    # print('courses:', courses)

    # Rooms Section
    # ROOMS: room name, capacity
    # A 32
    # B 50

    words = all_lines[room_section_start].split()
    if words[0] != 'ROOMS:':
        print('Error parsing ROOMS section')
        sys.exit()

    rooms = {}
    for i in range(num_rooms):
        words = all_lines[room_section_start+i+1].split()
        rooms[words[0]] = int(words[1])
    # print('rooms:', rooms)

    # Curricula Section
    # CURRICULA:
    # Cur1 3 SceCosC ArcTec TecCos
    # Cur2 2 TecCos Geotec

    words = all_lines[curricula_section_start].split()
    if words[0] != 'CURRICULA:':
        print('Error parsing CURRICULA section')
        sys.exit()

    curricula = {}
    for i in range(num_curricula):
        words = all_lines[curricula_section_start+i+1].split()
        # num_courses_in_curricula = int(words[1])
        the_courses = words[2:]
        curricula[words[0]] = the_courses
    # print('curricula:', curricula)

    # Unavailability Constraints Section
    # UNAVAILABILITY_CONSTRAINTS:
    # TecCos 2 0
    # TecCos 2 1
    # TecCos 3 2
    # TecCos 3 3
    # ArcTec 4 0
    # ArcTec 4 1
    # ArcTec 4 2
    # ArcTec 4 3

    words = all_lines[unavail_section_start].split()
    if words[0] != 'UNAVAILABILITY_CONSTRAINTS:':
        print('Error parsing UNAVAILABILITY_CONSTRAINTS section')
        sys.exit()

    unavail_contraints = {}
    for i in range(num_constraints):
        words = all_lines[unavail_section_start+i+1].split()
        if words[0] not in unavail_contraints:
            unavail_contraints[words[0]] = [(int(words[1]), int(words[2]))]
        else:
            unavail_contraints[words[0]].append((int(words[1]), int(words[2])))
    print('unavail_contraints:', unavail_contraints)

    return courses, rooms, num_days, periods_per_day, unavail_contraints, curricula

# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    # parse the file
    file_name = '/Users/brucks/Desktop/UTSA/CS5233_AI/Project/Timetabling/Data/ITC-2007/toy_prob.ctt.txt'
    read_itc_data_file(file_name)
