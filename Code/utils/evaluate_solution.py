##scoring is a percentage, the program gets a whole point if the class and time is 
#the same as the one wanted, but only get's half a point if only the class is 
#included but the time is different. 
##d1 is the original schedule someone wants
scheduleWanted={'cs': ('A', 'MW-0700-815'), 'bus':('A', 'MW-0830-0945'),'tec':('B', 'MW-1000-1115'), 'mus':('L', 'TR-1000-1115')}
##d2 is the solution given by the program 
solution={'bus':('A', "MW-0830-0945"),'tec':('B', 'MW-1000-1115'),'cs':('C', 'TR-8000-0915'),'mus':('L', 'TR-1000-1115') }
solution2={'bus':('A', "MW-0830-0945"),'tec':('B', 'MW-1000-1115'),'cs':('C', 'TR-8000-0915')}
def percentCorrect(d1,d2):
    d1l=len(d1)
    d2l=len(d2)
    unmatch=d1l-d2l

    #finds if both the keys and values match 
    ans= dict(d2.items() - d1.items())
    ansl=len(ans)

    unmatch=unmatch+ansl


    a2=(d1.keys())&(ans.keys())

    #finds if only the keys match 
    for thing in a2:
        del[ans[thing]] 
        unmatch-=.5
    
    asl=len(ans)
    matches = d1l-unmatch
    print("percent correct = ", (matches/d1l)*100)
percentCorrect(scheduleWanted,solution)
percentCorrect(scheduleWanted,solution2)
