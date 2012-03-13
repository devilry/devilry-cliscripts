#!/usr/bin/env python

import json
from devilryrestfullib import RestfulFactory

from devilrycliscriptslib.argparsewrapper import ArgumentParser
from devilrycliscriptslib.login import login_using_args
from devilrycliscriptslib.commonargs import add_common_args
from devilrycliscriptslib.queries import find_groups_in_assignment
from devilrycliscriptslib.queries import find_assignment_id_by_shortnames
from devilrycliscriptslib.utils import split_path

argparser = ArgumentParser(description='List groups on an assignment as json encoded data.')
add_common_args(argparser)
argparser.add_argument('--assignment', required=True,
                       help='Path to assignment. E.g: "duck1010.spring2010.assignment1"')
args = argparser.parse_args()

logincookie = login_using_args(args, 'test')
restful_factory = RestfulFactory(args.url)
AssignmentGroupApi = restful_factory.make('/administrator/restfulsimplifiedassignmentgroup/')
AssignmentApi = restful_factory.make('/administrator/restfulsimplifiedassignment/')
DeadlineApi = restful_factory.make('/administrator/restfulsimplifieddeadline/')


try:
    path = split_path(args.assignment, '--assignment', 3)
    source_assignment_id = find_assignment_id_by_shortnames(AssignmentApi, logincookie,
                                                            *path)
except LookupError:
    raise SystemExit('Assignment {0} not found.'.format(args.assignment))

groups = find_groups_in_assignment(AssignmentGroupApi, logincookie, source_assignment_id,
                                   result_fieldgroups=['feedback', 'users', 'tags'])
print json.dumps(groups, indent=2)
