# timetabling_csp.py: defines the Timetabling class which inherits from AIMA csp.Problem class but with modifications
#                     to allow for non-atomic variables. This allows us to use the CSP solver / search algorithms from
#                     the AIMA code base.
#

import csp

from copy import deepcopy

# -------------------------------------------------------------------------------------
class TimetablingCSP(csp.CSP):
    """Make a CSP for the Timetabling problem
    A CSP is specified by the following inputs:
        variables   A dict of {var:(attribute1, ...)} to handle a variable that is not atomic.
        attr_names  A list of the names of the attributes for each variable; this is only needed to parse the set of
                    unary constraints (and maybe for printing, output, solution verification)
        domains     A dict of {var:([possible_values for att1, ...], [att2],...)} entries.
        neighbors   A dict of {var:[var,...]} that for each variable lists
                    the other variables that participate in constraints
                    ==> we will build this at init since for a TT problem all courses are neighbors of each other
        constraints:        A list of functions f(A, a, B, b) that returns true if two variables
                            A, B satisfy the constraint when they have values A=a, B=b

    """

    def __init__(self, variables, attr_names, domains, constraints):
        """ Construct a TimetablingCSP problem."""
        self.variables = variables
        self.attr_names = attr_names
        self.domains = domains
        self.constraints = constraints
        self.curr_domains = None
        self.nassigns = 0

        # set up neighbors for all variables (it is all the other vars)
        all_var_names = list(self.variables.keys())
        self.neighbors = {}
        for v in self.variables:
            neighbors = deepcopy(all_var_names)
            neighbors.remove(v)
            self.neighbors[v] = neighbors

    def nconflicts(self, var, val, assignment):
        """Return the number of conflicts var=val has with other variables."""

        # assignment is a dictionary of {var:val} entries
        def fail_constraints(var1, val1, var2, val2):
            for c in self.constraints:
                # constraint functions return true if two variables satisfy the constraint
                if not c(var1, val1, var2, val2):
                    return True
            return False

        def conflict(var2):
            # fail = fail_constraints(var, val, var2, assignment[var2])
            return var2 in assignment and fail_constraints(var, val, var2, assignment[var2])

        num_conflicts = 0
        for v in self.neighbors[var]:
            if conflict(v):
                num_conflicts += 1
        return num_conflicts
        # return utils.count(conflict(v) for v in self.neighbors[var])

    def assign(self, var, val, assignment):
        """Add {var: val} to assignment; Discard the old value if any."""
        assignment[var] = val
        self.nassigns += 1

    # These are for constraint propagation
    def support_pruning(self):
        """Make sure we can prune values from domains. (We want to pay
        for this only if we use it.)"""
        if self.curr_domains is None:
            self.curr_domains = {v: list(self.domains[v]) for v in self.variables}

    def suppose(self, var, value):
        """Start accumulating inferences from assuming var=value."""
        self.support_pruning()
        removals = [(var, a) for a in self.curr_domains[var] if a != value]
        self.curr_domains[var] = [value]
        return removals

    def choices(self, var):
        """Return all values for var that aren't currently ruled out."""
        # This is tricky, we need to return a list of tuples with a value for each variable
        dom = (self.curr_domains or self.domains)
        poss_vals = [i for i in dom[var]]
        return poss_vals
