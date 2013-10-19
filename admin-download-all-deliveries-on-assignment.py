#!/usr/bin/env python

from getpass import getpass
import os
import sys
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
argparser.add_argument('--role', required=True,
        help='Your role. Valid values: "examiner", "administrator".')
argparser.add_argument('--outdir', required=True,
        help='Local filesystem directory to put the result in. Will create a directory named what you put in ``--assignment`` within this directory.')
args = argparser.parse_args()

logincookie = login_using_args(args, getpass())
outdir = args.outdir
role = args.role
if not role in ('examiner', 'administrator'):
    raise SystemExit('Invalid role: {}. See --help.'.format(role))

restful_factory = RestfulFactory(args.url)
AssignmentApi = restful_factory.make('/{}/restfulsimplifiedassignment/'.format(role))
AssignmentGroupApi = restful_factory.make('/{}/restfulsimplifiedassignmentgroup/'.format(role))
DeadlineApi = restful_factory.make('/{}/restfulsimplifieddeadline/'.format(role))
DeliveryApi = restful_factory.make('/{}/restfulsimplifieddelivery/'.format(role))
FileMetaApi = restful_factory.make('/{}/restfulsimplifiedfilemeta/'.format(role))
FileMetaDownloadApi = restful_factory.make('/student/show-delivery/filedownload/')


try:
    path = split_path(args.assignment, '--assignment', 3)
    source_assignment_id = find_assignment_id_by_shortnames(AssignmentApi, logincookie, *path)
except LookupError:
    raise SystemExit('Assignment {0} not found.'.format(args.assignment))

groups = find_groups_in_assignment(AssignmentGroupApi,
        logincookie, source_assignment_id,
        result_fieldgroups=['assignment', 'period', 'subject', 'users'],
        limit=10000)

if not os.path.exists(outdir):
    raise SystemExit('{} does not exist. Please create it before running this script.'.format(outdir))

for groupnumber, group in enumerate(groups, start=1):
    assignmentpath = '{parentnode__parentnode__parentnode__short_name}.{parentnode__parentnode__short_name}.{parentnode__short_name}'.format(**group)
    if role == 'examiner':
        usernamelist = group['candidates__identifier']
    else:
        usernamelist = group['candidates__student__username']
    usernames = '__'.join(usernamelist)
    assignmentdir = os.path.join(outdir, assignmentpath, usernames)
    print 'Downloading all deliveries for {} (group {}/{})'.format(usernames, groupnumber, len(groups))

    deliveries = DeliveryApi.search(logincookie,
        filters=[{'field': "deadline__assignment_group", 'comp':"exact", 'value': group['id']}],
        orderby=['time_of_delivery'])
    for number, delivery in enumerate(deliveries['items']):
        print '   {}: {}'.format(number, delivery['time_of_delivery'])
        filemetas = FileMetaApi.search(logincookie,
            filters=[{'field': "delivery", 'comp':"exact", 'value': delivery['id']}])
        deliverydir = os.path.join(assignmentdir, 'delivery-{}'.format(number))
        if not os.path.exists(deliverydir):
            os.makedirs(deliverydir)
        for filemeta in filemetas['items']:
            filename = filemeta['filename'].encode('ascii', 'replace').replace('?', 'X').replace(' ', '_')
            filepath = os.path.join(deliverydir, filename)
            sys.stdout.write('      Downloading {} ...'.format(filename))
            response = FileMetaDownloadApi.download(logincookie, filemeta['id'])
            open(filepath, 'wb').write(response.read())
            sys.stdout.write(' OK{}'.format(os.linesep))
