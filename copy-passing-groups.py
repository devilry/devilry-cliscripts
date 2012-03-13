from pprint import pprint
from devilryrestfullib import RestfulFactory

from devilrycliscriptslib.argparsewrapper import ArgumentParser
from devilrycliscriptslib.login import login_using_args
from devilrycliscriptslib.commonargs import add_common_args
from devilrycliscriptslib.queries import find_groups_in_assignment
from devilrycliscriptslib.queries import find_assignment_id_by_shortnames
from devilrycliscriptslib.managegroups import create_group


argparser = ArgumentParser(description='Copy groups from one assignment to another.')
add_common_args(argparser)
argparser.add_argument('--deadline', required=True,
                       help=('Initial deadline of the created groups. '
                             'Format: "YYYY-MM-DD hh:mm". Example: "2010-02-22 22:32"'))
argparser.add_argument('--source', required=True,
                       help='Path to assignment to copy from. E.g: "duck1010.spring2010.assignment1"')
argparser.add_argument('--target', required=True,
                       help='Path to assignment to copy to. E.g: "duck1010.spring2010.assignment2"')
argparser.add_argument('--allow_nonempty', default=False, action='store_false',
                       help=('Allow non-empty target assignment? If you enable '
                             'this, students are copied to the target even if they '
                             'already exist in a group within the target.'))
args = argparser.parse_args()

logincookie = login_using_args(args, 'test')
restful_factory = RestfulFactory(args.url)
AssignmentGroupApi = restful_factory.make('/administrator/restfulsimplifiedassignmentgroup/')
AssignmentApi = restful_factory.make('/administrator/restfulsimplifiedassignment/')
DeadlineApi = restful_factory.make('/administrator/restfulsimplifieddeadline/')


#pprint(AssignmentGroupApi.search(logincookie))
#subject, period, assignment = 'duck1100.spring01.week1'.split('.')

source_assignment_id = find_assignment_id_by_shortnames(AssignmentApi, logincookie,
                                                        *args.source.split('.'))
target_assignment_id = find_assignment_id_by_shortnames(AssignmentApi, logincookie,
                                                        *args.target.split('.'))
sourcegroups = find_groups_in_assignment(AssignmentGroupApi, logincookie, source_assignment_id,
                                         result_fieldgroups=['feedback', 'users', 'tags'])

if not args.allow_nonempty:
    targetgroups = find_groups_in_assignment(AssignmentGroupApi, logincookie, target_assignment_id,
                                             result_fieldgroups=['feedback', 'users', 'tags'])

    if len(targetgroups) > 0:
        raise SystemExit('Action aborted: The target assignment alread have {0} '
                         'groups. Use --allow_nonempty ignore this '
                         'check.'.format(len(targetgroups)))


for group in sourcegroups:
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
