# compute_itc_complexity.py: This python computes an estimate of the complexity of an ITC-2007 Course Timetabling
#                            Problem input file. This is done by randomly assigning all variables to one element from
#                            its domain and then scoring the assignment. This is repeated for N (default=500) trials
#                            and the average is taken as the (negative of the) complexity score
#


# import standard packages
import matplotlib.pyplot as plt
import numpy as np
import sys

# set the path and import our code
sys.path.append("../aima")
sys.path.append("../utils")
from solve_itc_baseline_csp import set_up_csp
from verify_solution import verify_solution

# -------------------------------------------------------------------------------------
def measure_complexity(file_name):

    # Read in the ITC data file and do the pre-process necessary to convert the raw data into
    # variables, domains and constraints
    variables, domains, constraints, curricula, time_slots = set_up_csp(file_name)
    N = 500
    scores = []
    output = []
    for i in range(N):
        # create a random solution
        solution = {}
        for v in variables:
            # randomly choose an assignment from this variable's domain
            ind = np.random.choice(len(domains[v]))
            solution[v] = domains[v][ind]

        # score it
        solved, solution_score = verify_solution(file_name, solution, verbose=False)
        # print(solution_score)

        scores.append(solution_score)


    print('file: ', file_name, ' mean:', np.mean(scores), np.std(scores))
    file = file_name.replace('../../Data/ITC-2007/', '')
    file = file.replace('.ctt.txt', '')
    output = (file, np.mean(scores), np.std(scores))

    return output

# -------------------------------------------------------------------------------------
if __name__ == "__main__":

    outptut = []
    for i in range(9):
        file_name = '../../Data/ITC-2007/comp0%s.ctt.txt' % (i+1)
        out = measure_complexity(file_name)
        outptut.append(out)

    for i in range(9,21):
        file_name = '../../Data/ITC-2007/comp%s.ctt.txt' % (i+1)
        out = measure_complexity(file_name)
        outptut.append(out)

    print(outptut)

    # bar plot this thing the easy way
    labels = []
    scores = []
    for i in outptut:
        labels.append(i[0])
        scores.append(-1.0*i[1])

    pos = range(len(scores))
    plt.bar(pos, scores)
    plt.xticks(pos, labels, rotation=60)
    plt.ylabel('Complexity')
    plt.title('ITC 2007 Timetabling Data')
    plt.show()

    # now get a bar chart color coded the way i want it ... with colors that match the color scheme of the poster
    # BFBFBF for easy
    # B8CDFF for medium
    # 021E48 for hard

    colors = []
    for i,s in enumerate(scores):
        if s < 10:
            colors.append('#BFBFBF')
        elif s < 20:
            colors.append('#B8CDFF')
        else:
            colors.append('#021E48')

    fig, ax = plt.subplots(1, 1)
    plt.bar(pos, scores, color=colors)
    plt.xticks(pos, labels, rotation=60)
    plt.ylabel('Complexity')
    plt.title('ITC 2007 Timetabling Data')

    # add the legend manually
    colors = {'easy': '#BFBFBF', 'medium': '#B8CDFF', 'hard': '#021E48'}
    legend_labels = ['easy', 'medium', 'hard'] #list(colors.keys())
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[label]) for label in legend_labels]
    plt.legend(handles, legend_labels)

    # plt.legend(['Easy', 'Medium', 'Hard'])
    plt.show()
