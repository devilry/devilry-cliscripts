#!/usr/bin/env python

from devilryrestfullib import RestfulFactory

from devilrycliscriptslib.argparsewrapper import ArgumentParser
from devilrycliscriptslib.login import login_using_args
from devilrycliscriptslib.commonargs import add_common_args
from devilrycliscriptslib.queries import find_groups_in_assignment
from devilrycliscriptslib.queries import find_assignment_id_by_shortnames
from devilrycliscriptslib.managegroups import create_group
from devilrycliscriptslib.utils import split_path


argparser = ArgumentParser(description='Copy groups from one assignment to another.')
add_common_args(argparser)
argparser.add_argument('--deadline', required=True,
                       help=('Initial deadline of the created groups. '
                             'Format: "YYYY-MM-DD hh:mm". Example: "2010-02-22 22:32"'))
argparser.add_argument('--source', required=True,
                       help='Path to assignment to copy from. E.g: "duck1010.spring2010.assignment1"')
argparser.add_argument('--target', required=True,
                       help='Path to assignment to copy to. E.g: "duck1010.spring2010.assignment2"')
argparser.add_argument('--allow_nonempty', default=False, action='store_true',
                       help=('Allow non-empty target assignment? If you enable '
                             'this, students are copied to the target even if they '
                             'already exist in a group within the target.'))
args = argparser.parse_args()

logincookie = login_using_args(args, 'test')
restful_factory = RestfulFactory(args.url)
AssignmentGroupApi = restful_factory.make('/administrator/restfulsimplifiedassignmentgroup/')
AssignmentApi = restful_factory.make('/administrator/restfulsimplifiedassignment/')
DeadlineApi = restful_factory.make('/administrator/restfulsimplifieddeadline/')


try:
    path = split_path(args.source, '--source', 3)
    source_assignment_id = find_assignment_id_by_shortnames(AssignmentApi, logincookie,
                                                            *path)
except LookupError:
    raise SystemExit('Assignment {0} not found.'.format(args.source))

try:
    path = split_path(args.target, '--target', 3)
    target_assignment_id = find_assignment_id_by_shortnames(AssignmentApi, logincookie,
                                                            *path)
except LookupError:
    raise SystemExit('Assignment {0} not found.'.format(args.target))
sourcegroups = find_groups_in_assignment(AssignmentGroupApi, logincookie, source_assignment_id,
                                         result_fieldgroups=['feedback', 'users', 'tags'])

if not args.allow_nonempty:
    targetgroups = find_groups_in_assignment(AssignmentGroupApi, logincookie, target_assignment_id,
                                             result_fieldgroups=['feedback', 'users', 'tags'])

    if len(targetgroups) > 0:
        raise SystemExit('Action aborted: The target assignment alread have {0} '
                         'groups. Use --allow_nonempty ignore this '
                         'check.'.format(len(targetgroups)))

copied = 0
for group in sourcegroups:
    if group['feedback__is_passing_grade']:
        candidates = [dict(candidate_id=None, username=username)
                      for username in group['candidates__student__username']]
        group = create_group(AssignmentGroupApi, logincookie,
                             target_assignment_id,
                             candidates=candidates,
                             examiners=group['examiners__user__username'],
                             tags=group['tags__tag'])
        DeadlineApi.create(logincookie,
                           deadline='{0}:00'.format(args.deadline),
                           assignment_group=group['id'])
        copied += 1

print "Copied {copied}/{total} groups from {source} to {target}.".format(copied=copied,
                                                                         total=len(sourcegroups),
                                                                         source=args.source,
                                                                         target=args.target)
