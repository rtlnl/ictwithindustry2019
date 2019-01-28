# Flask-related imports:
from flask import Flask, request, render_template
import json
import elasticsearch
import requests
from operator import itemgetter

################################################################################
# Load data

with open('static/imagenet_translations.json') as f:
    imagenet_translation = json.load(f)

################################################################################
# Set up general functions

def map_list(my_list, translations):
   "Return a translation for every item in a list"
   return [translations[item] for item in my_list]


def get_top_items(dictionary, n):
    "Get N top items from a dictionary"
    sorted_tuples = sorted(dictionary.items(), key=itemgetter(1), reverse=True)
    return [item for item, value in sorted_tuples[:n]]

################################################################################
# Set up app:
app = Flask(__name__)
es = elasticsearch.Elasticsearch()

CONCEPT_FIELDS = ('places', 'places_attributes', 'places_environment', 'coco', 'coco_count', 'imagenet', 'kinetics')
FIELD_MAPPING = {'places_attributes': 'Omgeving'}
TOOL_TIPS = {
    'places': 'Zoek op basis van de scenes in de Places365 dataset',
    'places_attributes':'Zoek op basis van scenebeschrijvingen in de Places365 dataset',
    'coco':'Zoek op basis van objecten in de MS-COCO dataset',
    'imagenet':'Zoek op basis van objecten in de ImageNet dataset',
    'kinetics':'Zoek op basis van acties in de Kinetics400 dataset',
    'Tekst':'Zoek op basis van tekstuele elementen in de videos en de beschrijving'}

try:
    assert es.cluster.health(timeout='10s').get('status') == 'green'
    MOCK_ES = False
    all_docs = es.search('ictwi2019', size=10000, _source=CONCEPT_FIELDS, request_timeout=60)["hits"]["hits"]
except:
    app.logger.warn('Cannot connect to Elasticsearch, using mock data.')
    MOCK_ES = True
    with open('static/search.json', encoding='utf-8') as f:
        all_docs = json.load(f)["hits"]["hits"]
    with open('static/mock.json', encoding='utf-8') as f:
        mock_embeddings = json.load(f)

max_scores = {}
for field in CONCEPT_FIELDS:
    max_scores[field] = {}
    for doc in all_docs:
        for k, v in doc['_source'].get(field, {}).items():
            max_scores[field][k] = max(max_scores[field].get(k, 0.0), v)

################################################################################
# Webpage-related functions

@app.route('/', methods=['GET'])
def main_page():
    """
    Function to display the main page.
    This is the first thing you see when you load the website.
    """
    return render_template('index.html')

def search(query, weights):
    visual_scores = visual_search(weights)
    text_scores = text_search(query, weights['Tekst'])

    max_visual_score = max(visual_scores.values())
    max_text_score = max(doc['_score'] for doc in text_scores)
    sum_text_weights = sum(v['weight'] for k, v in weights['Tekst'].items())
    sum_visual_weights = sum(sum(v['weight'] for _, v in w.items()) for k, w in weights.items() if k != 'Tekst')

    if max_visual_score == 0:
        max_visual_score = 1
    if max_text_score == 0:
        max_text_score = 1

    scores = {doc['_id']: doc['_score'] / max_text_score * sum_text_weights +
                          visual_scores[doc['_id']] / max_visual_score * sum_visual_weights
              for doc in text_scores}

    scores = sorted(text_scores, key=lambda doc: -scores[doc['_id']])[:10]

    docs = []
    for row in scores:
        doc = row['_source']
        doc['id'] = row["_id"]
        doc["title"] = doc["title"].replace(" - RTL NIEUWS - YouTube", "")
        item_date_raw = doc["meta"]["datePublished"].split('-')
        doc['date'] = "{0}-{1}-{2}".format(item_date_raw[2], item_date_raw[1], item_date_raw[0])
        doc['description'] = doc['description'].split("Abonneer je GRATIS voor meer video")[0]
        doc['url'] = doc["meta"]["og:video:url"]
        doc['tags'] = [tag.capitalize() for tag in doc["meta"]["og:video:tag"][4:]]
        doc['actions'] = " • ".join(get_top_items(doc['kinetics'],5))
        doc['imagenet_str'] = " • ".join(map_list(get_top_items(doc['imagenet'], 5), imagenet_translation))
        doc['coco_str'] = " • ".join(get_top_items(doc['coco'], 5))
        doc['places_str'] = " • ".join(get_top_items(doc['places'], 5))
        doc['places_attributes_str'] = " • ".join(get_top_items(doc['places_attributes'], 5))
        docs.append(doc)

    return docs

def text_search(query, weights):
    if MOCK_ES:
        search_data = all_docs
    else:
        query = {
            "query": {
                "bool": {
                    "should": [
                        {"match_all": {}},
                        {
                            "multi_match" : {
                                "query": query,
                                "fields": fields
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            }
        }
        search_data = es.search('ictwi2019', body=query, size=500)["hits"]["hits"]

    return search_data

def visual_search(weights):
    scores = {}
    for doc in all_docs:
        scores[doc['_id']] = 0.0
        for field, values in weights.items():
            if field in doc['_source']:
                for concept, value in values.items():
                    scores[doc['_id']] += doc['_source'][field].get(concept, 0.0) * float(value['weight'])
    return scores

def rank_concepts(query):
    weights = {
        'Tekst': {
            'title': {'nl': 'Titel', 'weight': 50},
            'description': {'nl': 'Beschrijving', 'weight': 20},
            'meta.og:video:tag': {'nl': 'Tags', 'weight': 10},
            'clean_ocr': {'nl': 'OCR', 'weight': 10}
        }
    }
    for term in query.split():
        if not MOCK_ES:
            concept_scores = requests.get(f'http://localhost:5001/{term}').json()
        else:
            concept_scores = mock_embeddings
        for field, scores in concept_scores.items():
            if field not in weights:
                weights[field] = {}
            for k, v in scores.items():
                v['weight'] *= max_scores[field].get(k, 0.0)
                if k not in weights[field]:
                    weights[field][k] = v
                else:
                    weights[field][k]['weight'] += v['weight']

    for field, scores in weights.items():
        weights[field] = dict(sorted(scores.items(), key=lambda x: -x[1]['weight'])[:4])
        if field != 'Tekst':
            for k, v in weights[field].items():
                v['weight'] = 0.0

    return weights

@app.route('/', methods=['POST'])
def results():
    """
    Show the results of the submitted query
    """
    query = request.form['textfield']
    weights = rank_concepts(query)
    for category in weights:
        for key, value in weights[category].items():
            if f'{category}/{key}' in request.form:
                value['weight'] = int(request.form[f'{category}/{key}'])

    return render_template('results.html', query=query, results=search(query, weights),
                           weights=weights, field_mapping={field: FIELD_MAPPING.get(field, field.capitalize()) for field in weights},
                           tooltips=TOOL_TIPS)

################################################################################
# Running the website

if __name__ == '__main__':
    app.debug = True
    app.run()
