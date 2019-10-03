import argparse
import os
import subprocess
import sys

sys.path.append(os.path.join(sys.path[0], '..', 'plot'))
import plot

class SubcmdException(BaseException):
    def __init__(self, cmd):
        self.command = cmd

class UnknownSubcmd(SubcmdException):
    pass

class UnimplementedSubcmd(SubcmdException):
    pass

class SubcmdConfigError(SubcmdException):
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

class PlotSubcmd(CxdbSubcmd):
    name = 'plot'
    description = 'Plot data about investiment funds'
    config = os.path.join(sys.path[0], '..', '.cxviz');

    def setup(self):
        self.set_cxdb_arg(False)
        self.parser.add_argument('--fund',
                                 action='store',
                                 required=True,
                                 help='Investiment fund to be plotted. Must be\
                                 an existing csv file name inside cxdb.')
        plot.set_locale()
        try:
            plot.read_config(readable_path(self.config))
        except Exception as e:
            print('Error when loading config file: {}'.format(self.config))
            print(e)
            raise SubcmdConfigError(self.name)

    def run(self):
        try:
            self.parse()
            readable_path(os.path.join(self.args.cxdb, '{}'.format(self.args.fund)))
        except Exception as e:
            print(e)
            return 1
        plot.show_feed(self.args.cxdb, self.args.fund)
        return 0

