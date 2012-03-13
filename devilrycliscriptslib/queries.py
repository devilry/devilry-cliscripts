def find_period_id_by_shortnames(PeriodApi, logincookie,
                                 subject_shortname, period_shortname):
    search = PeriodApi.search(logincookie, limit=1,
                                  filters=[{'field':'parentnode__short_name', 'comp':'exact', 'value':subject_shortname},
                                           {'field':'short_name', 'comp':'exact', 'value':period_shortname}])
    if len(search['items']) == 0:
        raise LookupError()
    else:
        return search['items'][0]['id']


def find_assignment_id_by_shortnames(AssignmentApi, logincookie,
                                     subject_shortname, period_shortname,
                                     assignment_shortname):
    search = AssignmentApi.search(logincookie, limit=1,
                                  filters=[{'field':'parentnode__parentnode__short_name', 'comp':'exact', 'value':subject_shortname},
                                           {'field':'parentnode__short_name', 'comp':'exact', 'value':period_shortname},
                                           {'field':'short_name', 'comp':'exact', 'value':assignment_shortname}])
    if len(search['items']) == 0:
        raise LookupError()
    else:
        return search['items'][0]['id']



def find_groups_in_assignment(AssignmentGroupApi, logincookie,
                              assignment_id, limit=10,
                              result_fieldgroups=[]):
    search = AssignmentGroupApi.search(logincookie,
                                       limit=limit,
                                       filters=[{'field':'parentnode', 'comp':'exact', 'value':assignment_id}],
                                       result_fieldgroups=result_fieldgroups)
    total = search['total']
    if total > limit:
        # Do a new request for _all_ items if the total number of groups is more than the initial limit
        return find_groups_in_assignment(AssignmentGroupApi, logincookie,
                                         assignment_id, limit=total,
                                         result_fieldgroups=result_fieldgroups)
    else:
        return search['items']


def find_all_examiners_in_period(ExaminerApi, logincookie, period_id):
    """ Get all examiners in the period as a dict where the assignmentgroup is
    the key, and the value is a list of examiners. (for efficient lookup of
    examiner when you have a group). """
    examiners = ExaminerApi.search(logincookie,
                                   limit=100000,
                                   filters=[{'field':'assignmentgroup__parentnode__parentnode',
                                             'comp':'exact',
                                             'value':period_id}],
                                   result_fieldgroups=['userdetails']) # Include username, fullname, ...
    result = {}
    for examiner in examiners['items']:
        groupid = examiner['assignmentgroup']
        if not groupid in result:
            result[groupid] = []
        result[groupid].append(examiner)
    return result


def find_all_assignmentgroups_in_period(AssignmentGroupApi, logincookie, period_id):
    search = AssignmentGroupApi.search(logincookie,
                                       limit=100000,
                                       filters=[{'field':'parentnode__parentnode',
                                                 'comp':'exact',
                                                 'value':period_id}],
                                       result_fieldgroups=['assignment']) # Include info about the assignment in the result
    return search['items']
