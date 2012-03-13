from pprint import pprint
from devilryrestfullib import RestfulFactory

from devilrycliscriptslib.argparsewrapper import ArgumentParser
from devilrycliscriptslib.login import login_using_args
from devilrycliscriptslib.commonargs import add_common_args
from devilrycliscriptslib.queries import find_groups_in_assignment


argparser = ArgumentParser(description='Copy groups from one assignment to another.')
add_common_args(argparser)
args = argparser.parse_args()

logincookie = login_using_args(args, 'test')
restful_factory = RestfulFactory(args.url)
AssignmentGroupApi = restful_factory.make('/administrator/restfulsimplifiedassignmentgroup/')


#pprint(AssignmentGroupApi.search(logincookie))
subject, period, assignment = 'duck1100.spring01.week1'.split('.')
groups = find_groups_in_assignment(AssignmentGroupApi, logincookie, subject, period, assignment,
                                   result_fieldgroups=['feedback', 'users'])
pprint(groups)
