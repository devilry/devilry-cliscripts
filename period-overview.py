#!/usr/bin/env python

from getpass import getpass
from devilryrestfullib import RestfulFactory

from devilrycliscriptslib.argparsewrapper import ArgumentParser
from devilrycliscriptslib.login import login_using_args
from devilrycliscriptslib.commonargs import add_common_args
from devilrycliscriptslib.queries import find_period_id_by_shortnames
from devilrycliscriptslib.queries import aggregate_points_for_each_student
from devilrycliscriptslib.utils import split_path


argparser = ArgumentParser(description=('Show a table with results for each '
                                        'student on the entire period '
                                        'aggregated. Note that "no-data" means '
                                        'that the student is not registered on '
                                        'that assignment.'))
add_common_args(argparser)
argparser.add_argument('--period', required=True,
                       help='Path to the period. E.g: "duck1010.spring2010"')
args = argparser.parse_args()

logincookie = login_using_args(args, getpass())
restful_factory = RestfulFactory(args.url)
PeriodApi = restful_factory.make('/administrator/restfulsimplifiedperiod/')
AssignmentApi = restful_factory.make('/administrator/restfulsimplifiedassignment/')
AssignmentGroupApi = restful_factory.make('/administrator/restfulsimplifiedassignmentgroup/')


def create_table_from_points_aggregate(students, all_assignments):
    """
    Create a table of students and their points on each assignment.
    Takes the output from aggregate_points_for_each_student(...) as arguments.
    """

    # Print header ({0:<20} format string makes positional arg 0 occupy 20 chars left aligned)
    print '{0:<20} '.format('USER'), # Ending comma prevent newline
    for assignment_shortname in all_assignments:
        print '{0:<20} '.format(assignment_shortname),
    print 'SUM'

    # Print points for each user on each assignment
    for student, student_assignments in students.iteritems():
        print '{0:<20}'.format(student),

        total = 0
        for assignment_shortname in all_assignments:
            if assignment_shortname in student_assignments:
                group = student_assignments[assignment_shortname]
                points = group['feedback__points']
                if points == None:
                    points = 'no-feedback'
                else:
                    total += points
            else:
                points = 'no-data' # Student not registered on assignment
            print ' {0:<20}'.format(points),
        print ' {0:<20}'.format(total)


subject, period = split_path(args.period, '--period', 2)
try:
    period_id = find_period_id_by_shortnames(PeriodApi, logincookie, subject, period)
except LookupError, e:
    raise SystemExit('ERROR: Could not find requested period: {0}'.format(args.period))
else:
    students, all_assignments= aggregate_points_for_each_student(AssignmentApi, AssignmentGroupApi, logincookie, period_id)
    create_table_from_points_aggregate(students, all_assignments)
