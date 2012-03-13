from devilryrestfullib import RestfulFactory

from devilrycliscriptslib.argparsewrapper import ArgumentParser
from devilrycliscriptslib.login import login_using_args
from devilrycliscriptslib.commonargs import add_common_args


argparser = ArgumentParser(description='Copy groups from one assignment to another.')
add_common_args(argparser)
args = argparser.parse_args()

logincookie = login_using_args(args, 'test')
restful_factory = RestfulFactory(args.url)
AssignmentGroup = restful_factory.make('/administrator/restfulsimplifiedassignmentgroup/')
from pprint import pprint
pprint(AssignmentGroup.search(logincookie))
