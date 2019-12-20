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

def open_config_file(file, create_if_needed=False):
    try:
        if create_if_needed:
            return cxfeed.CxvizConfig(checker.maybe_file(file))
        else:
            return cxfeed.CxvizConfig(checker.readable_path(file))
    except cxfeed.ConfigError as e:
        print('Error when loading config file: {}'.format(file))
        raise e
    except Exception as e:
        raise e

class ConfigSubcmd(Subcommand):
    name = 'config'
    description = 'Configure cxviz with PhantomJS path'
    config = os.path.join(sys.path[0], '..', '.cxviz')

    def __init__(self):
        super().__init__()
        self.parser.add_argument('phantomjs_path',
                                 action='store',
                                 help='PhantomJS install dir')
        self.set_usage_string()

    def run(self):
        try:
            super().run()
            cfg = open_config_file(self.config, True)
            if 'phantomjs' in cfg.parser:
                oldpath = cfg.phantomjs()
                cfg.parser.remove_option('phantomjs', oldpath)
            else:
                cfg.parser.add_section('phantomjs')
            cfg.parser.set('phantomjs', self.args.phantomjs_path)
            with open(self.config, 'w') as config_file:
                cfg.parser.write(config_file)
        except Exception as e:
            print(e)
            return 1
        return 0

class CxdbSubcmd(Subcommand):
    cxdb = os.path.join(sys.path[0], '..', 'cxdb')
    config = os.path.join(sys.path[0], '..', '.cxviz')

    def __init__(self):
        super().__init__()
        if not hasattr(self, 'check_cxdb'):
            raise InvalidSubcmd(self.name)
        self.parser.add_argument('--cxdb',
                                 action='store',
                                 type=self.check_cxdb,
                                 default=self.cxdb,
                                 help='Path to database. Default: {}'.format(self.cxdb))

    def run(self):
        super().run()
        try:
            cfg = open_config_file(self.config)
            self.cxpull = cxpullsubprocess.CxpullSubprocess(cfg.phantomjs())
        except Exception as e:
            print(e)
            raise SubcmdException(self.name)

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

    def __init__(self):
        super().__init__()
        self.parser.add_argument('--no-pull',
                                 action='store_false',
                                 dest='allow_pull',
                                 help='Only plot funds, do not update database')
        self.parser.add_argument('--debug',
                                 action='store_true',
                                 help='Enable verbose log')
        self.set_usage_string()
        cxfeed.set_locale()

    def update_db(self, gui):
        status = self.cxpull.pull(self.args.cxdb, self.args.debug)
        if status == 1:
            gui.logln('Warning: cxdb was not updated correctly: {}'.format(self.args.cxdb))

    def run(self):
        status = 0
        try:
            super().run()
            gui = cxgui.CxGui(self.args.cxdb, self.config)
            self.cxpull.set_logger(gui.log)
            if self.args.allow_pull:
                self.update_db(gui)
            gui.create_config_buttons()
            gui.show_feed()
        except cxfeed.UnknownFund as e:
            gui.logln('Error on config file \'{}\': unknown fund: {}'.format(self.config, e))
            status = 1
        except cxfeed.UnknownMetric as e:
            gui.logln('Error on config file \'{}\': unknown metric: {}'.format(self.config, e))
            status = 1
        except Exception as e:
            gui.logln(e)
            status = 1
        gui.loop()
        return 0

