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
