#!/usr/bin/env python

from getpass import getpass
from devilryrestfullib import RestfulFactory

from devilrycliscriptslib.argparsewrapper import ArgumentParser
from devilrycliscriptslib.login import login_using_args
from devilrycliscriptslib.commonargs import add_common_args
from devilrycliscriptslib.queries import find_period_id_by_shortnames
from devilrycliscriptslib.queries import find_all_examiners_in_period
from devilrycliscriptslib.queries import find_all_assignmentgroups_in_period
from devilrycliscriptslib.utils import split_path


argparser = ArgumentParser(description='Show a table with the number of groups corrected by each examiner.')
add_common_args(argparser)
argparser.add_argument('--period', required=True,
                       help='Path to the period. E.g: "duck1010.spring2010"')
args = argparser.parse_args()

logincookie = login_using_args(args, getpass())
restful_factory = RestfulFactory(args.url)
AssignmentGroupApi = restful_factory.make('/administrator/restfulsimplifiedassignmentgroup/')
PeriodApi = restful_factory.make('/administrator/restfulsimplifiedperiod/')
ExaminerApi = restful_factory.make('/administrator/restfulsimplifiedexaminer/')


def list_number_of_assignments_corrected_by_examiners(period):
    examiners = find_all_examiners_in_period(ExaminerApi, logincookie, period)
    groups = find_all_assignmentgroups_in_period(AssignmentGroupApi, logincookie, period)
    assignment_shortnames = ['TOTAL']
    result = {}

    # Count corrected assignments and store them by examiner->assignment->count in ``result``
    for group in groups:
        assignment_shortname = group['parentnode__short_name']
        if not assignment_shortname in assignment_shortnames:
            assignment_shortnames.append(assignment_shortname)
        groupid = group['id']
        if groupid in examiners:
            groupexaminers = examiners[groupid]
            for examiner in groupexaminers:
                examiner_username = examiner['user__username']
                if not examiner_username in result:
                    result[examiner_username] = {'TOTAL': 0}
                result[examiner_username]['TOTAL'] += 1
                if assignment_shortname in result[examiner_username]:
                    result[examiner_username][assignment_shortname] += 1
                else:
                    result[examiner_username][assignment_shortname] = 1
        else:
            pass # Group has no examiners, and perhaps you want to print a warning?

    # Print result in a table
    stringformat = '{:<14} | '
    headerrow = stringformat.format('Examiner')
    for assignment_shortname in assignment_shortnames:
        headerrow += stringformat.format(assignment_shortname)
    print headerrow
    for examiner_username, count_by_assignment in result.iteritems():
        row = stringformat.format(examiner_username)
        for assignment_shortname in assignment_shortnames:
            count = count_by_assignment.get(assignment_shortname, '')
            row += stringformat.format(count)
        print row




subject, period = split_path(args.period, '--period', 2)
try:
    period_id = find_period_id_by_shortnames(PeriodApi, logincookie, subject, period)
except LookupError, e:
    raise SystemExit('ERROR: Could not find requested period: {0}'.format(args.period))
else:
    list_number_of_assignments_corrected_by_examiners(period_id)
