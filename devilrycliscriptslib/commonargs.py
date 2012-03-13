from login import add_login_args

def add_common_args(argparser):
    """
    Add common args that are always required.
    """
    argparser.add_argument('--url', required=True,
                           help='Devilry server url.',
                           metavar='https://devilry.example.com')
    add_login_args(argparser)
