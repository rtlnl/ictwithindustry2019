import csv
from nltk.corpus import wordnet as wn
from lxml import etree

ROOT = etree.parse('./Resources/odwn_cili.xml')

def parse(line):
    "Parse the wordnet offsets."
    line = line.strip()
    meta, *lemmas = line.split()
    lemmas = ' '.join(lemmas)
    pos = meta[0]
    rest = meta[1:]
    wordnet_id = '-'.join(["eng", "30", rest, pos])
    return meta, wordnet_id, lemmas


def get_synonyms(wordnet_id):
    "Get synonyms from Dutch."
    xpath = './/Sense[@synset="{}"]'.format(wordnet_id)
    senses = ROOT.findall(xpath)
    lemmas = []
    for sense in senses:
        lemma = sense.getparent().find('Lemma').attrib['writtenForm']
        lemmas.append(lemma)
    return lemmas


def load_data(filename):
    "Load data from categories file."
    with open(filename) as f:
        data = [parse(line) for line in f]
    return data


def enrich_data(data):
    "Enrich data with Dutch synonyms, if available."
    enriched = []
    untranslated = []
    for meta, wordnet_id, lemmas in data:
        dutch_synonyms = get_synonyms(wordnet_id)
        dutch_text = ', '.join(dutch_synonyms)
        row = [meta, wordnet_id, dutch_text]
        enriched.append(row)
        if not dutch_text):
            english_lemmas = lemmas.split(', ')
            for lemma in english_lemmas:
                row = [meta, wordnet_id, lemma]
                untranslated.append(row)
    return enriched, untranslated


syndata = load_data('./Resources/1k-categories.txt')
enriched, untranslated = enrich_data(syndata)


header = ['key', 'wordnet_id', 'synonyms']
with open('./Output/Incomplete/dutch_synonyms_1k.tsv','w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(header)
    writer.writerows(enriched)


header = ['key', 'wordnet_id', 'english']
with open('./Output/Incomplete/dutch_to_do_1k.tsv','w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(header)
    writer.writerows(untranslated)
