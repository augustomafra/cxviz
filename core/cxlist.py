import csv
import glob
import os

def get_fund_files(cxdb_path):
    return glob.glob(os.path.join(cxdb_path, '*.csv'))

def list_funds(cxdb_path):
    fund_files = get_fund_files(cxdb_path)
    return [os.path.basename(csv_file).replace('.csv', '') for csv_file in fund_files]

def get_csv_header(fund_file):
    with open(fund_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';', strict=True)
        return next(csvreader)

def list_metrics(cxdb_path):
    fund_files = get_fund_files(cxdb_path)
    if len(fund_files) == 0:
        return []
    some_fund = fund_files[0]
    return get_csv_header(some_fund)

