def find_groups_in_assignment(AssignmentGroupApi, logincookie,
                              subject_shortname, period_shortname,
                              assignment_shortname, limit=10,
                              result_fieldgroups=[]):
    search = AssignmentGroupApi.search(logincookie,
                                       limit=limit,
                                       filters=[{'field':'parentnode__parentnode__parentnode__short_name', 'comp':'exact', 'value':subject_shortname},
                                                {'field':'parentnode__parentnode__short_name', 'comp':'exact', 'value':period_shortname},
                                                {'field':'parentnode__short_name', 'comp':'exact', 'value':assignment_shortname}],
                                       # Get the latest feedback and students in addition to information stored
                                       # directly on each group.
                                       result_fieldgroups=result_fieldgroups)
    total = search['total']
    if total > limit:
        # Do a new request for _all_ items if the total number of groups is more than the initial limit
        return find_groups_in_assignment(subject_shortname,
                                         period_shortname,
                                         assignment_shortname,
                                         limit=total)
    else:
        return search['items']
