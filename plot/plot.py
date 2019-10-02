import csv
from datetime import datetime
import locale
import matplotlib.pyplot
import numpy
import os

def set_locale():
    locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

class Cxdb(object):
    def __init__(self, cxdb_path, fund):
        self.fund = fund
        with open(os.path.join(cxdb_path, '{}'.format(fund)), 'r') as csvfile:
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

def show_feed(cxdb_path, fund):
    cxdb = Cxdb(cxdb_path, fund)
    header = ['Data',
              'Data Início',
              'Aplic Inicial (R$)',
              'Cota (R$)',
              'Variação Dia (%)',
              'Acumulado Mês (%)',
              'Acumulado Ano (%)',
              'Acumulado 12M (%)',
              'PL (milhões R$)',
              'PL Médio (milhões R$)']
    cxdb.subplot(1, header[4])
    cxdb.subplot(2, header[5])
    cxdb.subplot(3, header[6])
    matplotlib.pyplot.show()

