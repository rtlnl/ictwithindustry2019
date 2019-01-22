import csv
from nltk.corpus import wordnet as wn
from lxml import etree

def parse(item):
    "Parse the wordnet offsets."
    pos = item[0]
    rest = item[1:].strip()
    wordnet_id = '-'.join(["eng", "30", rest, pos])
    return wordnet_id

root = etree.parse('./Resources/odwn_cili.xml')

def get_synonyms(wordnet_id):
    xpath = './/Sense[@synset="{}"]'.format(wordnet_id)
    senses = root.findall(xpath)
    lemmas = []
    for sense in senses:
        lemma = sense.getparent().find('Lemma').attrib['writtenForm']
        lemmas.append(lemma)
    return lemmas


def get_synonym_data(filename):
    with open(filename) as f:
        lines = [line.strip() for line in f]
    wordnet_ids = [parse(ident) for ident in lines]
    synonyms = [get_synonyms(wid) for wid in wordnet_ids]
    rows = []
    for key, wid, syn in zip(lines,wordnet_ids,synonyms):
        row = [key, wid, ', '.join(syn)]
        rows.append(row)
    return rows

syndata = get_synonym_data('./Resources/concepts_googlenet_bottomup_12988.txt')
header = ['key', 'wordnet_id', 'synonyms']

with open('./Output/Incomplete/dutch_synonyms.tsv','w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(header)
    writer.writerows(syndata)
