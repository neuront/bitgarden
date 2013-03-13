class _AppEnv:
    appenv = None

    def __init__(self, c):
        self.server_port = int(c.get('server', 'port'))
        self.db_port = int(c.get('db', 'port'))

def _prepare():
    if _AppEnv.appenv != None:
        return
    import ConfigParser
    import sys
    if len(sys.argv) == 2:
        conf_filename = sys.argv[1]
        print 'Use configure file', conf_filename
    else:
        conf_filename = 'deploy.ini'
        print 'Use default configure file', conf_filename
    sys.stdout.flush()
    with open(conf_filename, 'r') as conf_file:
        c = ConfigParser.ConfigParser()
        c.readfp(conf_file)
        _AppEnv.appenv = _AppEnv(c)

def env():
    return _AppEnv.appenv

_prepare()
