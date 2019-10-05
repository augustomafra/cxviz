import argparse
import os
import subprocess
import sys

import cxfeed

class SubcmdException(BaseException):
    def __init__(self, cmd):
        self.command = cmd

class UnknownSubcmd(SubcmdException):
    pass

class UnimplementedSubcmd(SubcmdException):
    pass

class Subcommand(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description=self.description)
        if not (hasattr(self, 'name')
                and hasattr(self, 'description')
                and hasattr(self, 'parser')):
            raise UnimplementedSubcmd('Missing name, description or parser attribute')

    def setup(self):
        pass

    def parse(self):
        self.args = self.parser.parse_args(sys.argv[2:])

    def run(self):
        self.parse()
        raise UnimplementedSubcmd(self.name)

def readable_path(path):
    if not os.access(path, os.R_OK):
        raise Exception('No read access on path: {}'.format(path))
    return path

def maybe_dir(maybe_dir):
    if not os.path.isdir(maybe_dir):
        os.mkdir(maybe_dir)

    just_dir = maybe_dir
    if not os.access(just_dir, os.W_OK):
        raise Exception('No write access on directory: {}'.format(just_dir))
    if not os.access(just_dir, os.R_OK):
        raise Exception('No read access on directory: {}'.format(just_dir))

    return just_dir

class CxdbSubcmd(Subcommand):
    cxdb = os.path.join(sys.path[0], '..', 'cxdb')
    def set_cxdb_arg(self, create_if_needed):
        self.parser.add_argument('--cxdb',
                                 action='store',
                                 type=maybe_dir if create_if_needed else readable_path,
                                 default=self.cxdb,
                                 help='Path to database. Default: {}'.format(self.cxdb))

class PullSubcmd(CxdbSubcmd):
    name = 'pull'
    description = 'Download data from Caixa and update cxdb database'
    engine = 'phantomjs'
    cxpull = os.path.join(sys.path[0], '..', 'cxpull', 'cxpull.js')

    def setup(self):
        self.set_cxdb_arg(True)
        self.parser.add_argument('--debug',
                                 action='store_true',
                                 help='Enable verbose log')

    def run(self):
        try:
            self.parse()
        except Exception as e:
            print(e)
            return 1
        cmd = [self.engine, self.cxpull, '--cxdb', self.args.cxdb]
        if self.args.debug:
            cmd.append('--debug')
        return subprocess.run(cmd).returncode

class FeedSubcmd(CxdbSubcmd):
    name = 'feed'
    description = 'Show feed with data about investiment funds'
    config = os.path.join(sys.path[0], '..', '.cxviz');

    def setup(self):
        self.set_cxdb_arg(False)
        cxfeed.set_locale()

    def run(self):
        try:
            self.parse()
            cxfeed.show_feed(self.args.cxdb, readable_path(self.config))
        except cxfeed.ConfigError as e:
            print('Error when loading config file: {}'.format(self.config))
            print(e)
            return 1
        except Exception as e:
            print(e)
            return 1
        return 0

