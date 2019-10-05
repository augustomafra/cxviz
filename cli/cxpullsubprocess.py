import os
import sys

import subprocess

class CxpullSubprocess(object):
    engine = 'phantomjs'
    cxpull = os.path.join(sys.path[0], '..', 'cxpull', 'cxpull.js')

    def get_cmdline(self, cxdb):
        return [self.engine, self.cxpull, '--cxdb', cxdb]

    def launch_subprocess(self, cmd):
        return subprocess.run(cmd).returncode

    def pull(self, cxdb, debug):
        cmd = self.get_cmdline(cxdb)
        if debug:
            cmd.append('--debug')
        return self.launch_subprocess(cmd)

    def unlock(self, cxdb):
        cmd = self.get_cmdline(cxdb)
        cmd.append('--unlock')
        return self.launch_subprocess(cmd)

