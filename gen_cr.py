pastipf = sorted(list(set([','.join([x.split(',')[0], x.split(',')[2]]) for x in open('./covid_xprize/oxford_data/data/OxCGRT_latest.csv', 'r').readlines()[1:]])))

with open('countries_regions_updated.csv', 'w+') as f:
    f.write('\n'.join(pastipf))