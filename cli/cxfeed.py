import configparser
import csv
from datetime import datetime
import locale
import matplotlib.pyplot
import numpy
import os

def set_locale():
    locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

cxviz_config = {'funds' : [], 'metrics' : []}
def read_config(config_file):
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str # Make the parser case sensitive
    config.read(config_file)
    if 'funds' in config:
        for fund in config['funds']:
            cxviz_config['funds'].append(fund)
    if 'metrics' in config:
        for metric in config['metrics']:
            cxviz_config['metrics'].append(metric)

class Cxdb(object):
    def __init__(self, cxdb_path, fund):
        self.fund = fund
        with open(os.path.join(cxdb_path, '{}.csv'.format(fund)), 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';', strict=True)
            self.parse_csv(csvreader)

    def parse_csv(self, csvreader):
        parsingHeader = True
        for line in csvreader:
            if parsingHeader:
                self.data = {col:[] for col in line}
                parsingHeader = False
            else:
                i = 0
                for col in self.data:
                    self.data[col].append(line[i])
                    i += 1

    def subplot(self, index, metric):
        if index > 3:
            raise Exception('Invalid subplot index')
        matplotlib.pyplot.subplot(3, 1, index)
        if index == 1:
            matplotlib.pyplot.title(self.fund)
        date_header = list(self.data.keys())[0]
        matplotlib.pyplot.plot(date(self.data[date_header]),
                               numeric(self.data[metric]))
        matplotlib.pyplot.ylabel(metric)
        matplotlib.pyplot.xlabel(date_header)
        matplotlib.pyplot.grid(True)

def numeric(data_array):
    return [numpy.nan if i == '-' else locale.atof(i) for i in data_array]

def date(data_array):
    d = {'weekday' : '%a',
            'month' : '%b',
            'day' : '%d',
            'year' : '%Y',
            'hour' : '%H',
            'minute' : '%M',
            'second' : '%S',
            'zone' : '%Z',
            'offset' : '%z',
            'ignore' : '%f'} # HACK Actually %f stands for microseconds
    hour_format = ':'.join([d['hour'], d['minute'], d['second']])
    zone_format = d['zone'] + d['offset']
    ignore = '(-{})'.format(d['ignore'])
    date_format = ' '.join([d['weekday'], d['month'], d['day'], d['year'],
                            hour_format, zone_format, ignore])

    return [datetime.strptime(i, date_format) for i in data_array]

def show_feed(cxdb_path):
    for fund in cxviz_config['funds']:
        matplotlib.pyplot.figure()
        cxdb = Cxdb(cxdb_path, fund)
        index = 1
        for metric in cxviz_config['metrics']:
            cxdb.subplot(index, metric)
            index += 1
    matplotlib.pyplot.show()

