def create_group(AssignmentGroupApi, logincookie,
                 assignment_id, candidates, examiners=[],
                 tags=[]):
    """
    :param candidates:
        List of ``{"candidate_id: "Some candidate id", "username": "someusername"}`` dicts.
    :param tags:
        List of tags.
    :param examiners:
        List of examiner usernames.
    :return:
        Dict with info about the created group. The ``id`` key contains the assigned ``id``.
    """
    return AssignmentGroupApi.create(logincookie, is_open=True,
                                     parentnode=assignment_id,
                                     fake_tags=tags,
                                     fake_candidates=candidates,
                                     fake_examiners=examiners)
