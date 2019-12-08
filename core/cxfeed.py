import configparser
import csv
from datetime import datetime
import locale
import matplotlib.pyplot
import numpy
import os

import checker

def set_locale():
    locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

class ConfigError(BaseException):
    pass

class UnknownFund(BaseException):
    pass

class UnknownMetric(BaseException):
    pass

class CxvizConfig(object):
    def __init__(self, config_file):
        self.data = {'phantomjs': '', 'funds' : [], 'metrics' : []}
        try:
            self.parser = configparser.ConfigParser(delimiters=('='), allow_no_value=True)
            self.set_case_sensitive(self.parser)
            self.parser.read(config_file)
        except Exception as e:
            raise ConfigError(e)
        self.read_singleton_config(self.parser, 'phantomjs')
        self.read_config(self.parser, 'funds')
        self.read_config(self.parser, 'metrics')

    def set_case_sensitive(self, config):
        config.optionxform = str

    def read_config(self, config, section):
        if section in config:
            for key in config[section]:
                self.data[section].append(key)

    def read_singleton_config(self, config, section):
        if section in config:
            for key in config[section]:
                self.data[section] = key

    def phantomjs(self):
        return self.data['phantomjs']

    def funds(self):
        return self.data['funds']

    def metrics(self):
        return self.data['metrics']

class CxdbFund(object):
    def __init__(self, cxdb_path, fund):
        self.fund = fund
        csv_path = os.path.join(cxdb_path, '{}.csv'.format(fund))
        try:
            checker.readable_path(csv_path)
        except Exception as e:
            raise UnknownFund(fund)
        with open(csv_path, 'r') as csvfile:
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

    def subplot(self, num_rows, index, metric):
        if index > num_rows:
            raise Exception('Invalid subplot index')
        matplotlib.pyplot.subplot(num_rows, 1, index)
        if index == 1:
            matplotlib.pyplot.title(self.fund)
        date_header = list(self.data.keys())[0]
        try:
            plot_data = self.data[metric]
        except KeyError as e:
            raise UnknownMetric(metric)
        matplotlib.pyplot.plot(date(self.data[date_header]),
                               numeric(plot_data))
        matplotlib.pyplot.ylabel(metric)
        matplotlib.pyplot.xlabel(date_header)
        matplotlib.pyplot.grid(True)

def numeric(data_array):
    return [numpy.nan if i == '-' else locale.atof(i) for i in data_array]

def date(data_array):
    weekday = '%a'
    month = '%b'
    day = '%d'
    year = '%Y'
    hour = '%H'
    minute = '%M'
    second = '%S'
    zone = '%Z'
    offset = '%z'
    ignore = '%f' # HACK Actually %f stands for microseconds
    hour_format = ':'.join([hour, minute, second])
    zone_format = zone + offset
    ignore = '(-{})'.format(ignore)
    date_format = ' '.join([weekday, month, day, year,
                            hour_format, zone_format, ignore])

    return [datetime.strptime(i, date_format) for i in data_array]

def create_plot_figure(cxdb_path, config, fund):
    figure = matplotlib.pyplot.figure()
    cxdb_fund = CxdbFund(cxdb_path, fund)
    index = 1
    for metric in config.metrics():
        cxdb_fund.subplot(len(config.metrics()), index, metric)
        index += 1
    return figure

def plot_feed(cxdb_path, config_file):
    cxviz_config = CxvizConfig(config_file)
    for fund in cxviz_config.funds():
        yield create_plot_figure(cxdb_path, cxviz_config, fund)

def plot_fund(cxdb_path, config_file, fund):
    cxviz_config = CxvizConfig(config_file)
    return create_plot_figure(cxdb_path, cxviz_config, fund)

