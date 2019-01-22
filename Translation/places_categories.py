import csv

with open('./Resources/Scene hierarchy-Places365.tsv') as f:
    rows = [line.strip().split('\t') for line in f]

coarse = rows[1][1:]
with open('Output/Incomplete/places_coarse.csv','w') as f:
    writer = csv.writer(f)
    writer.writerow(['location_name'])
    writer.writerows([[item,'bla'] for item in coarse])

fine, *_ = zip(*rows[2:])
fine = [cat.strip("'") for cat in fine]
header = ['location_full', 'location_main', 'location_spec']
rows = []
for location in fine:
    elements = location.split('/')
    if len(elements) == 3:
        row = [location, elements[2], '']
    else:
        row = [location, elements[2], elements[3]]
    rows.append(row)

with open('Output/Incomplete/places_fine.tsv','w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(header)
    writer.writerows(rows)
