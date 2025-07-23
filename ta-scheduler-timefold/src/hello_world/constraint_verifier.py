from timefold.solver.test   import ConstraintVerifier
# This file is used to verify the constraints defined in the constraints.py file.
from .constraints           import *
from .domain                import Shift, TA, ShiftAssignment, Timetable


# Create a ConstraintVerifier instance to verify the constraints
constraint_verifier = ConstraintVerifier.build(define_constraints, Timetable, Shift, TA, ShiftAssignment)
# constraint_verifier = ConstraintVerifier.build(define_constraints_tabriz_edition, Timetable, Shift, TA, ShiftAssignment)

