# contains functions from AIMA csp.py that we need to over-ride so they work with our TimetablingCSP() class as well
# as a few other odds and ends

# -------------------------------------------------------------------------------------
# in general: a constraint function f(A, a, B, b) that returns true if two variables
#             A, B satisfy the constraint when they have values A=a, B=b

# constraint: A, B have different assignments
def constraint_different_values(A, a, B, b, curricula):
    # note that this function does not need the argument 'curricula' but we need to maintain a consistent function
    # signature across all the constraint functions
    return (a != b)

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


