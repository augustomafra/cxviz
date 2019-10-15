import argparse
import os
import sys

import checker
import cxfeed
import cxpullsubprocess

class SubcmdException(BaseException):
    def __init__(self, cmd):
        self.command = cmd

class UnknownSubcmd(SubcmdException):
    pass

class Subcommand(object):
    def __init__(self):
        if not (hasattr(self, 'name') and hasattr(self, 'description')):
            raise UnknownSubcmd('Missing name or description attributes')
        self.parser = argparse.ArgumentParser(description=self.description)

    def set_usage_string(self):
        usage = self.parser.format_usage()
        usage = usage.replace('usage: ', '')
        usage = usage.replace('cxviz', 'cxviz {}'.format(self.name))
        self.parser.usage = usage

    def run(self):
        self.args = self.parser.parse_args(sys.argv[2:])

class CxdbSubcmd(Subcommand):
    cxdb = os.path.join(sys.path[0], '..', 'cxdb')
    def __init__(self, create_if_needed):
        super().__init__()
        self.parser.add_argument('--cxdb',
                                 action='store',
                                 type=checker.maybe_dir if create_if_needed else checker.readable_path,
                                 default=self.cxdb,
                                 help='Path to database. Default: {}'.format(self.cxdb))

class PullSubcmd(CxdbSubcmd):
    name = 'pull'
    description = 'Download data from Caixa and update cxdb database'
    cxpull = cxpullsubprocess.CxpullSubprocess()

    def __init__(self):
        super().__init__(True)
        self.parser.add_argument('--debug',
                                 action='store_true',
                                 help='Enable verbose log')
        self.set_usage_string()

    def run(self):
        try:
            super().run()
        except Exception as e:
            print(e)
            return 1
        return self.cxpull.pull(self.args.cxdb, self.args.debug)

class UnlockSubcmd(CxdbSubcmd):
    name = 'unlock'
    description = 'Unlock cxdb directory locked by previous cxviz run'
    cxpull = cxpullsubprocess.CxpullSubprocess()

    def __init__(self):
        super().__init__(False)
        self.set_usage_string()

    def run(self):
        try:
            super().run()
        except Exception as e:
            print(e)
            return 1
        return self.cxpull.unlock(self.args.cxdb)

class FeedSubcmd(CxdbSubcmd):
    name = 'feed'
    description = 'Pull and show feed with data about investiment funds'
    config = os.path.join(sys.path[0], '..', '.cxviz');
    cxpull = cxpullsubprocess.CxpullSubprocess()

    def __init__(self):
        super().__init__(True)
        self.set_usage_string()
        cxfeed.set_locale()

    def run(self):
        try:
            super().run()
            status = self.cxpull.pull(self.args.cxdb, False)
            if status == 1:
                print('Warning: cxdb was not updated correctly: {}'.format(self.args.cxdb))
            cxfeed.show_feed(self.args.cxdb, checker.readable_path(self.config))
        except cxfeed.ConfigError as e:
            print('Error when loading config file: {}'.format(self.config))
            print(e)
            return 1
        except cxfeed.UnknownFund as e:
            print('Error on config file \'{}\': unknown fund: {}'.format(self.config, e))
            return 1
        except cxfeed.UnknownMetric as e:
            print('Error on config file \'{}\': unknown metric: {}'.format(self.config, e))
            return 1
        except Exception as e:
            print(e)
            return 1
        return 0

