#!/usr/bin/env python

from getpass import getpass
from devilryrestfullib import RestfulFactory

from devilrycliscriptslib.argparsewrapper import ArgumentParser
from devilrycliscriptslib.login import login_using_args
from devilrycliscriptslib.commonargs import add_common_args
from devilrycliscriptslib.queries import find_groups_in_assignment
from devilrycliscriptslib.queries import find_assignment_id_by_shortnames
from devilrycliscriptslib.utils import split_path

argparser = ArgumentParser(description='Download all deliveries on an assignment.')
add_common_args(argparser)
argparser.add_argument('--assignment', required=True,
        help='Path to assignment. E.g: "duck1010.spring2010.assignment1"')
argparser.add_argument('--outdir', required=True,
        help='Local filesystem directory to put the result in. Will create a directory named what you put in ``--assignment`` within this directory.')
args = argparser.parse_args()

logincookie = login_using_args(args, getpass())
outdir = args.outdir
restful_factory = RestfulFactory(args.url)
AssignmentGroupApi = restful_factory.make('/administrator/restfulsimplifiedassignmentgroup/')
AssignmentApi = restful_factory.make('/administrator/restfulsimplifiedassignment/')
DeadlineApi = restful_factory.make('/administrator/restfulsimplifieddeadline/')
DeliveryApi = restful_factory.make('/administrator/restfulsimplifieddelivery/')
FileMetaApi = restful_factory.make('/administrator/restfulsimplifiedfilemeta/')



try:
    path = split_path(args.assignment, '--assignment', 3)
    source_assignment_id = find_assignment_id_by_shortnames(AssignmentApi, logincookie, *path)
except LookupError:
    raise SystemExit('Assignment {0} not found.'.format(args.assignment))

groups = find_groups_in_assignment(AssignmentGroupApi,
        logincookie, source_assignment_id,
        result_fieldgroups=['assignment', 'period', 'subject', 'users'],
        limit=10000)

for group in groups:
    assignmentpath = '{parentnode__parentnode__parentnode__short_name}.{parentnode__parentnode__short_name}.{parentnode__short_name}'.format(**group)
    usernames = '__'.join(group['candidates__student__username'])
    print assignmentpath, usernames
    deadlines = DeadlineApi.search(logincookie,
            filters=[{'field': "assignment_group", 'comp': "exact", 'value': group['id']}])
    for deadline in deadlines['items']:
        deadlinename = 'deadline-{deadline}'.format(**deadline)
        print '   ', deadlinename
        deliveries = DeliveryApi.search(logincookie,
            filters=[{'field': "deadline", 'comp':"exact", 'value': deadline['id']}],
            orderby=['time_of_delivery'])
        for number, delivery in enumerate(deliveries['items']):
            print '       {}: {}'.format(number, delivery['time_of_delivery'])
            filemetas = FileMetaApi.search(logincookie,
                filters=[{'field': "delivery", 'comp':"exact", 'value': delivery['id']}])
            for filemeta in filemetas['items']:
                filename = filemeta['filename'].encode('ascii', 'replace').replace('?', 'X').replace(' ', '_')
                print '         ', filename
