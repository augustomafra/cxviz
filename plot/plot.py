import csv
import locale
import matplotlib.pyplot
import numpy
import os

def set_locale():
    locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

class Cxdb(object):
    def __init__(self, cxdb_path, fund):
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

def numeric(data_array):
    return [numpy.nan if i == '-' else locale.atof(i) for i in data_array]

def subplot(index, fund, metric, data):
    if index > 3:
        raise Exception('Invalid subplot index')
    matplotlib.pyplot.subplot(3, 1, index)
    if index == 1:
        matplotlib.pyplot.title(fund)
    matplotlib.pyplot.plot(data)
    matplotlib.pyplot.ylabel(metric)
    matplotlib.pyplot.xlabel('Data')
    matplotlib.pyplot.grid(True)

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
    subplot(1, fund, header[4], numeric(cxdb.data[header[4]]))
    subplot(2, fund, header[5], numeric(cxdb.data[header[5]]))
    subplot(3, fund, header[6], numeric(cxdb.data[header[6]]))
    matplotlib.pyplot.show()

