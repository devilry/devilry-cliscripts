def split_path(path, what, expected_parts):
    if not path.count('.') == (expected_parts - 1):
        raise SystemExit('Invalid {0}: "{1}". Expected {2} "."'.format(what, path, expected_parts-1))
    return path.split('.')
