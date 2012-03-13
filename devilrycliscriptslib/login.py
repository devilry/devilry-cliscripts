from devilryrestfullib import login


LOGIN_PROFILES = dict(devilry={'usernamefield': 'username', 'passwordfield': 'password', 'loginpath': '/authenticate/login'},
                     uio={'usernamefield': 'user', 'passwordfield': 'password', 'loginpath': '/login'})
AVAILABLE_LOGINPROFILES = ', '.join(repr(p) for p in LOGIN_PROFILES)


def add_login_args(argparser):
    argparser.add_argument('--user', required=True,
                           help='Username used to login to Devilry. You are prompted for a password.')
    argparser.add_argument('--loginprofile', default=None,
                           help=('A login profile sets --usernamefield, --passwordfield '
                                 'and --loginpath according to a profile. Available profiles: {0}.'
                                 .format(AVAILABLE_LOGINPROFILES)))
    argparser.add_argument('--usernamefield', default='username',
                           help='The username field in the login form. Defaults to "username".')
    argparser.add_argument('--passwordfield', default='password',
                           help='The password field in the login form. Defaults to "password".')
    argparser.add_argument('--loginpath', default='/authenticate/login',
                           help=('The prefix of the login URL. Defaults to "/authenticate/login". '
                                 'Changing this normally means that you authenticate through '
                                 'something other than devilry.'))

def login_using_args(args, password):
    """
    Login using args from argparse added by :func:`add_login_args`.
    """
    ## Login using other form parameters and url.
    ## (just an example for setups that do not authenticate through Devilry, this one for UiO.)
    if args.url.endswith('/'):
        url = args.url[:-1]
    else:
        url = args.url

    if args.loginprofile:
        try:
            loginprofile = LOGIN_PROFILES[args.loginprofile]
        except KeyError:
            raise SystemExit('Invalid login profile: \'{0}\'. See --help for more available profiles.'
                             .format(args.loginprofile, AVAILABLE_LOGINPROFILES))
        else:
            loginpath = loginprofile['loginpath']
            kw = {loginprofile['usernamefield']: args.user,
                  loginprofile['passwordfield']: password}
    else:
        loginpath = args.loginpath
        kw = {args.usernamefield: args.user,
              args.passwordfield: password}

    login_url = '{0}{1}'.format(url, loginpath)
    logincookie = login(login_url, **kw)
    return logincookie
