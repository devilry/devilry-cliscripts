#!/usr/bin/env python

import sys
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
StaticFeedbackApi = restful_factory.make('/administrator/restfulsimplifiedstaticfeedback/')


def list_number_of_assignments_corrected_by_examiners(period):
    print 'Reading information about all examiners. This takes a lot of time for large courses...'
    examiners_by_group = find_all_examiners_in_period(ExaminerApi, logincookie, period)
    examinerusers = {}
    for groupid, examiners in examiners_by_group.iteritems(): # NOTE: Exceptionally inefficient method of getting the username->name map for all examiners
        for examiner in examiners:
            examinerusers[examiner['user']] = examiner['user__devilryuserprofile__full_name'] or examiner['user__username']

    groups = find_all_assignmentgroups_in_period(AssignmentGroupApi, logincookie, period,
                                   result_fieldgroups=['assignment', 'feedback'])
    assignment_shortnames = ['TOTAL']
    result = {}

    # Count corrected assignments and store them by examiner->assignment->count in ``result``
    longest_examinername_length = 0
    longest_assignmentname_length = 0
    for groupnumber, group in enumerate(groups, start=1):
        loading_message = 'Collecting data from group {:8}/{:<8}'.format(groupnumber, len(groups))
        if groupnumber > 1:
            sys.stdout.write('\b' * len(loading_message)) # Remove the last message (we update the same line with the message)
        sys.stdout.write(loading_message)
        sys.stdout.flush()

        assignment_shortname = group['parentnode__short_name']
        if not assignment_shortname in assignment_shortnames:
            assignment_shortnames.append(assignment_shortname)
        if len(assignment_shortname) > longest_assignmentname_length:
            longest_assignmentname_length = len(assignment_shortname)

        groupid = group['id']
        if group['is_open']:
            continue
        feedback_id = group['feedback']
        if feedback_id == None:
            continue
        feedback = StaticFeedbackApi.read(logincookie, feedback_id)
        saved_by_examiner_id = feedback['saved_by']
        examiner_name = examinerusers.get(saved_by_examiner_id, 'Unknown user (id: {})'.format(saved_by_examiner_id))
        if len(examiner_name) > longest_examinername_length:
            longest_examinername_length = len(examiner_name)
        if not examiner_name in result:
            result[examiner_name] = {'TOTAL': 0}
        result[examiner_name]['TOTAL'] += 1
        if assignment_shortname in result[examiner_name]:
            result[examiner_name][assignment_shortname] += 1
        else:
            result[examiner_name][assignment_shortname] = 1
    print
    print


    # Print result in a table
    examinerformat = '{{:<{length}}} | '.format(length=longest_examinername_length)
    if longest_assignmentname_length < 4:
        longest_assignmentname_length = 4
    assignmentformat = '{{:<{length}}} | '.format(length=longest_assignmentname_length)
    headerrow = examinerformat.format('Examiner')
    for assignment_shortname in assignment_shortnames:
        headerrow += assignmentformat.format(assignment_shortname)
    print headerrow
    for examiner_name, count_by_assignment in result.iteritems():
        row = examinerformat.format(examiner_name.encode('ascii', 'replace'))
        for assignment_shortname in assignment_shortnames:
            count = count_by_assignment.get(assignment_shortname, '')
            row += assignmentformat.format(count)
        print row




subject, period = split_path(args.period, '--period', 2)
try:
    period_id = find_period_id_by_shortnames(PeriodApi, logincookie, subject, period)
except LookupError, e:
    raise SystemExit('ERROR: Could not find requested period: {0}'.format(args.period))
else:
    list_number_of_assignments_corrected_by_examiners(period_id)
