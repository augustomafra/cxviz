#!/usr/bin/python3

import argparse
import sys

import subcommand

class RepeatedSubcmd(subcommand.SubcmdException):
    pass

class Cxviz(object):
    HELP_INDENT = '   '
    HELP_TAB = '      '
    description = 'Caixa investment data visualization'
    usage = '''cxviz <command> [<args>]

Available commands
'''
    subcommands = {}

    def add_subcommand(self, subcommand):
        if subcommand.name in self.subcommands:
            raise RepeatedSubcmd(subcommand.name)
        self.subcommands[subcommand.name] = subcommand.run
        self.usage += self.HELP_INDENT \
                    + subcommand.name \
                    + self.HELP_TAB \
                    + subcommand.description \
                    + '\n'

    def launch_cli(self):
        parser = argparse.ArgumentParser(description=self.description, usage=self.usage)
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not args.command in self.subcommands:
            raise subcommand.UnknownSubcmd(args.command)
        return self.subcommands[args.command]()

def main():
    cxviz = Cxviz()
    try:
        cxviz.add_subcommand(subcommand.FeedSubcmd())
        cxviz.add_subcommand(subcommand.PullSubcmd())
        cxviz.add_subcommand(subcommand.UnlockSubcmd())
    except RepeatedSubcmd as e:
        print('Invalid setup: Subcommand \'{}\' is repeated'.format(e))
        exit(1)

    status = 0
    try:
        status = cxviz.launch_cli()
    except subcommand.UnknownSubcmd as errorCmd:
        print('Unrecognized command: {}'.format(errorCmd.command))
        exit(1)
    exit(status)

if __name__ == '__main__':
    main()

