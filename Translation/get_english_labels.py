import csv
from nltk.corpus import wordnet as wn

def get_synset(line):
    "Produce synset from a line containing offset ID."
    original = line.strip()
    pos = original[0]
    offset = int(original[1:])
    synset = wn.synset_from_pos_and_offset(pos, offset)
    return original, pos, offset, synset


header = ['original', 'pos', 'offset', 'synset_name', 'lemma']
rows = []
with open('./concepts_googlenet_bottomup_12988.txt') as f:
    for line in f:
        original, pos, offset, synset = get_synset(line)
        synset_name = synset.name()
        lemma = synset.lemmas()[0].name()
        row = [original, pos, offset, synset_name, lemma]
        rows.append(row)

with open('Output/english_names.tsv','w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(header)
    writer.writerows(rows)
