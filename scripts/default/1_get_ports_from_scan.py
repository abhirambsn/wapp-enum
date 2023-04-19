import csv

def run(scan_result):
    reader_res = csv.DictReader(open(scan_result, 'r'), delimiter=';')
    return {'ports_list': [int(c['port']) for c in reader_res]}