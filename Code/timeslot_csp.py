# time_slot.py: defines the TimeSlot class

# -------------------------------------------------------------------------------------
# create a class to represent a course time slot
class TimeSlot():
    def __init__(self, days, time_start, time_stop):
        """ Construct a TimeSlot object"""
        # days is a list of chars
        # times should be ints (4 digits using military time)
        # if isinstance(days, list):
        self.days = days
        # else:
        #     self.days = [days]
        self.start = time_start
        self.stop = time_stop

    def __repr__(self):
        if len(self.days) == 1:
            return "%s-%04d-%04d" % (self.days, self.start, self.stop)
        else:
            days_str = ''.join(self.days)
            return "%s-%04d-%04d" % (days_str, self.start, self.stop)

    def __eq__(self, other):
        return (self.days == other.days) and (self.start == other.start) and (self.stop == other.stop)

    def __ne__(self, other):
        return (self.days != other.days) or (self.start != other.start) or (self.stop != other.stop)

    def __lt__(self, other):
        # define < so we can sort a set of TimeSlot variables
        # if self.start == other.start:
        #     self.stop < other.stop
        # else:
        #     self.start < other.start
        return self.__repr__() < other.__repr__()

    def __hash__(self):
        return hash(repr(self))

    def overlaps(self, ts):
        # returns true if self overlaps with ts

        # does the day overlap?
        this_set = set(self.days)
        ts_set = set(ts.days)
        if not (this_set & ts_set):
            return False

        # these timelots do not overlap if
        #   the other stops before this starts OR
        #   the other starts after this ends
        if ts.stop < self.start or ts.start > self.stop:
            return False
        return True

        # # does the time overlap? 3 cases to check
        # # does end time of ts land in (self.start, self.stop)
        # if ts.stop >= self.start and ts.stop <= self.stop:
        #     return True
        # # does start time of ts land in (self.start, self.stop)
        # if ts.start >= self.start and ts.start <= self.stop:
        #     return True
        # # does ts completly cover  (self.start, self.stop)
        # if ts.start <= self.start and ts.stop >= self.stop:
        #     return True
        #
        # return False
