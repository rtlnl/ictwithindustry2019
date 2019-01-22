import csv
from collections import defaultdict

def get_csv_entries(filename):
    "Get entries from a CSV file."
    with open(filename) as f:
        reader = csv.DictReader(f, delimiter='\t')
        entries = list(reader)
    return entries


def combine_google_items(entries):
    "Combine entries from different rows."
    index = defaultdict(list)
    for entry in entries:
        key = entry['key']
        translation = entry['translation']
        index[key].append(translation)
    results = dict()
    for key, translations in index.items():
        results[key] = ', '.join(translations)
    return results


def modify_wordnet_entries():
    "Add the translated synonyms to the WordNet entries."
    for entry in wordnet_translate:
        key = entry['key']
        synonyms = entry['synonyms']
        if synonyms == '':
            entry['synonyms'] = gt_index[key]
            entry['provenance'] = 'google_translate'
        else:
            entry['provenance'] = 'odwn'

wordnet_translate = get_csv_entries('./Output/Incomplete/dutch_synonyms_1k.tsv')
google_translate = get_csv_entries('./Output/Incomplete/dutch_to_do_1k_sheets.tsv')
gt_index = combine_google_items(google_translate)
modify_wordnet_entries()

header = ['key', 'wordnet_id', 'synonyms', 'provenance']
with open('./Output/translated_1k.tsv', 'w') as f:
    writer = csv.DictWriter(f, delimiter='\t', fieldnames=header)
    writer.writeheader()
    writer.writerows(wordnet_translate)
