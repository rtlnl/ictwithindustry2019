import csv
from nltk.corpus import wordnet as wn

def get_rows(filename):
    "Get rows from a TSV file."
    with open(filename) as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    return rows


def no_translation(rows):
    "Get rows which have no translation."
    return [row for row in rows if row['synonyms'] == '']


def get_lemmas(synset_id):
    "Get the lemmas for a synset from WordNet"
    raw_lemmas = [lemma.name() for lemma in wn.synset(synset_id).lemmas()]
    spaced = [' '.join(lemma.split('_')) for lemma in raw_lemmas]
    return spaced



def prepare_translation_rows(to_do):
    "Prepare the untranslated rows for translation."
    rows = []
    for entry in to_do:
        wid = entry['wordnet_id']
        lang, version, offset, pos = wid.split('-')
        offset = int(offset)
        synset = wn.synset_from_pos_and_offset(pos, offset)
        for lemma in synset.lemmas():
            name = ' '.join(lemma.name().split('_'))
            row = [entry['key'], wid, name]
            rows.append(row)
    return rows

rows = get_rows('./Output/Incomplete/dutch_synonyms.tsv')
to_do = no_translation(rows)
to_write = prepare_translation_rows(to_do)

header = ['key', 'wordnet_id', 'lemma']
with open('./Output/Incomplete/to_translate.csv','w') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(to_write)
    
