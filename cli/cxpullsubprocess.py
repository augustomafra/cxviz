import os
import sys

import subprocess

class CxpullSubprocess(object):
    engine = 'phantomjs'
    cxpull = os.path.join(sys.path[0], '..', 'cxpull', 'cxpull.js')

    def launch_subprocess(self, cxdb, debug):
        pass
        cmd = [self.engine, self.cxpull, '--cxdb', cxdb]
        if debug:
            cmd.append('--debug')
        return subprocess.run(cmd).returncode

