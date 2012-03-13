#!/usr/bin/env python

import sys
from getpass import getpass
from os import linesep
from devilryrestfullib import RestfulFactory

from devilrycliscriptslib.argparsewrapper import ArgumentParser
from devilrycliscriptslib.login import login_using_args
from devilrycliscriptslib.commonargs import add_common_args
from devilrycliscriptslib.queries import find_period_id_by_shortnames
from devilrycliscriptslib.queries import aggregate_points_for_each_student
from devilrycliscriptslib.utils import split_path


argparser = ArgumentParser(description=('Show a table with CSV results for each '
                                        'student on the entire period '
                                        'aggregated. Meaning of the numbers in '
                                        'the table: 0: No deliveries, 1: Not approved, 2: Approved'))
add_common_args(argparser)
argparser.add_argument('--period', required=True,
                       help='Path to the period. E.g: "duck1010.spring2010"')
args = argparser.parse_args()

logincookie = login_using_args(args, getpass())
restful_factory = RestfulFactory(args.url)
PeriodApi = restful_factory.make('/administrator/restfulsimplifiedperiod/')
AssignmentApi = restful_factory.make('/administrator/restfulsimplifiedassignment/')
AssignmentGroupApi = restful_factory.make('/administrator/restfulsimplifiedassignmentgroup/')


def csv_approvedstats(students, all_assignments):
    """
    Create a csv table of students. For each assignment, a number is added:

        0: No deliveries
        1: Not approved
        2: Approved
    """
    # Print header ({0:<20} format string makes positional arg 0 occupy 20 chars left aligned)
    sys.stdout.write('USER') # Ending comma prevent newline
    for assignment_shortname in all_assignments:
        sys.stdout.write(',{0}'.format(assignment_shortname))
    sys.stdout.write(linesep)

    # Print the documented number for each user on each assignment
    for student, student_assignments in students.iteritems():
        sys.stdout.write(student)

        for assignment_shortname in all_assignments:
            number = 0
            if assignment_shortname in student_assignments:
                group = student_assignments[assignment_shortname]
                deliveries = group['number_of_deliveries']
                if deliveries > 0:
                    if group['feedback__is_passing_grade']:
                        number = 2
                    else:
                        number = 1
            else:
                pass # Student no registered on assignment - keep number at 0
            sys.stdout.write(',{0}'.format(number))
        sys.stdout.write(linesep)


subject, period = split_path(args.period, '--period', 2)
try:
    period_id = find_period_id_by_shortnames(PeriodApi, logincookie, subject, period)
except LookupError, e:
    raise SystemExit('ERROR: Could not find requested period: {0}'.format(args.period))
else:
    students, all_assignments = aggregate_points_for_each_student(AssignmentApi, AssignmentGroupApi, logincookie, period_id)
    csv_approvedstats(students, all_assignments)
