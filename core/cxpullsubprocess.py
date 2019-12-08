import os
import sys

import subprocess

class CxpullSubprocess(object):
    cxpull = os.path.join(sys.path[0], '..', 'cxpull', 'cxpull.js')
    logger = None

    def __init__(self, phantomjs_path):
        if sys.platform == 'win32':
            self.engine = os.path.join(phantomjs_path, 'bin', 'phantomjs.exe')
        else:
            self.engine = os.path.join(phantomjs_path, 'bin', 'phantomjs')

    def set_logger(self, logger):
        self.logger = logger

    def get_cmdline(self, cxdb):
        return [self.engine, self.cxpull, '--cxdb', cxdb]

    def launch_subprocess(self, cmd):
        try:
            if not self.logger:
                return subprocess.run(cmd).returncode
            process = subprocess.Popen(cmd,
                                       stdout=subprocess.PIPE,
                                       universal_newlines=True)
        except FileNotFoundError as e:
            self.logger('Error: PhantomJS was not found: {}\n'.format(cmd[0]))
            return 1
        self.poll_subprocess(process)
        self.flush_stdout(process)
        return process.returncode

    def poll_subprocess(self, process):
        while process.poll() is None:
            self.logger(process.stdout.readline())

    def flush_stdout(self, process):
        log = process.stdout.readline()
        while not log is '':
            self.logger(log)
            log = process.stdout.readline()

    def pull(self, cxdb, debug):
        cmd = self.get_cmdline(cxdb)
        if debug:
            cmd.append('--debug')
        return self.launch_subprocess(cmd)

    def unlock(self, cxdb):
        cmd = self.get_cmdline(cxdb)
        cmd.append('--unlock')
        return self.launch_subprocess(cmd)

