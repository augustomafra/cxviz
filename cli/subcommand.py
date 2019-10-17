import argparse
import os
import sys

sys.path.append(os.path.join(sys.path[0], '..', 'core'))
import checker
import cxlist
import cxfeed
import cxpullsubprocess

sys.path.append(os.path.join(sys.path[0], '..', 'gui'))
import cxgui

class SubcmdException(BaseException):
    def __init__(self, cmd):
        self.command = cmd

class UnknownSubcmd(SubcmdException):
    pass

class InvalidSubcmd(SubcmdException):
    pass

class Subcommand(object):
    def __init__(self):
        if not (hasattr(self, 'name') and hasattr(self, 'description')):
            raise InvalidSubcmd('Missing name or description attributes')
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
    cxpull = cxpullsubprocess.CxpullSubprocess()

    def __init__(self):
        super().__init__()
        if not hasattr(self, 'check_cxdb'):
            raise InvalidSubcmd(self.name)
        self.parser.add_argument('--cxdb',
                                 action='store',
                                 type=self.check_cxdb,
                                 default=self.cxdb,
                                 help='Path to database. Default: {}'.format(self.cxdb))

class ReadableCxdbSubcmd(CxdbSubcmd):
    def check_cxdb(self, cxdb):
        return checker.readable_path(cxdb)

class CreatableCxdbSubcmd(CxdbSubcmd):
    def check_cxdb(self, cxdb):
        return checker.maybe_dir(cxdb)

class PullSubcmd(CreatableCxdbSubcmd):
    name = 'pull'
    description = 'Download data from Caixa and update cxdb database'

    def __init__(self):
        super().__init__()
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

class UnlockSubcmd(ReadableCxdbSubcmd):
    name = 'unlock'
    description = 'Unlock cxdb directory locked by previous cxviz run'

    def __init__(self):
        super().__init__()
        self.set_usage_string()

    def run(self):
        try:
            super().run()
        except Exception as e:
            print(e)
            return 1
        return self.cxpull.unlock(self.args.cxdb)

class ListSubcmd(ReadableCxdbSubcmd):
    name = 'list'
    description = 'List funds or metrics available in cxdb database'

    def __init__(self):
        super().__init__()
        self.parser.add_argument('--funds',
                                 action='store_true',
                                 help='List funds in cxdb')
        self.parser.add_argument('--metrics',
                                 action='store_true',
                                 help='List metrics in cxdb')
        self.set_usage_string()

    def run(self):
        try:
            super().run()
            if not (self.args.funds or self.args.metrics):
                self.parser.error('Must add --funds or --metrics switches')
            if self.args.funds:
                print('\n'.join(cxlist.list_funds(self.args.cxdb)))
            if self.args.metrics:
                print('\n'.join(cxlist.list_metrics(self.args.cxdb)))
        except Exception as e:
            print(e)
            return 1
        return 0

class FeedSubcmd(CreatableCxdbSubcmd):
    name = 'feed'
    description = 'Pull and show feed with data about investiment funds'
    config = os.path.join(sys.path[0], '..', '.cxviz')

    def __init__(self):
        super().__init__()
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

class GuiSubcmd(ReadableCxdbSubcmd):
    name = 'gui'
    description = 'Open gui application'
    config = os.path.join(sys.path[0], '..', '.cxviz')

    def __init__(self):
        super().__init__()
        self.set_usage_string()

    def run(self):
        try:
            super().run()
            gui = cxgui.CxGui(self.args.cxdb,
                              checker.readable_path(self.config))
            gui.loop()
        except Exception as e:
            print(e)
            return 1
        return 0

