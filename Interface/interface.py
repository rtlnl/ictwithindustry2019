# Flask-related imports:
from flask import Flask, request, render_template
import json
import elasticsearch
import requests
from operator import itemgetter

################################################################################
# Load data


################################################################################
# Set up general functions

def get_top_items(dictionary, n):
    "Get N top items from a dictionary"
    sorted_tuples = sorted(dictionary.items(), key=itemgetter(1))
    return [item for item, value in sorted_tuples[:n]]

################################################################################
# Set up app:
app = Flask(__name__)
es = elasticsearch.Elasticsearch()

CONCEPT_FIELDS = ('places', 'places_attributes', 'places_environment', 'coco', 'coco_count', 'imagenet', 'kinetics')
FIELD_MAPPING = {'places_attributes': 'Attributen'}

try:
    assert es.cluster.health(timeout='10s').get('status') == 'green'
    MOCK_ES = False
    all_docs = es.search('ictwi2019', size=10000, _source=CONCEPT_FIELDS, request_timeout=60)["hits"]["hits"]
except:
    app.logger.warn('Cannot connect to Elasticsearch, using mock data.')
    MOCK_ES = True
    with open('static/search.json') as f:
        all_docs = json.load(f)["hits"]["hits"]
    with open('static/mock.json') as f:
        mock_embeddings = json.load(f)

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
    return text_search(query, weights['Tekst'])

def text_search(query, weights):
    if MOCK_ES:
        search_data = all_docs
    else:
        query = {"query": {"multi_match" : {
            "query": query,
            "fields": [f'{k}^{w["weight"]}' for k, w in weights.items()]
        }}}
        search_data = es.search(body=query)["hits"]["hits"]

    docs = []
    for row in search_data:
        doc = row['_source']
        doc['id'] = row["_id"]
        doc["title"] = doc["title"].replace(" - RTL NIEUWS - YouTube", "")
        item_date_raw = doc["meta"]["datePublished"].split('-')
        doc['date'] = "{0}-{1}-{2}".format(item_date_raw[2], item_date_raw[1], item_date_raw[0])
        doc['description'] = doc['description'].split("Abonneer je GRATIS voor meer video")[0]
        doc['url'] = doc["meta"]["og:video:url"]
        doc['tags'] = [tag.capitalize() for tag in doc["meta"]["og:video:tag"][4:]]
        doc['actions'] = get_top_items(doc['kinetics'],5)
        doc['objects'] = list(zip(get_top_items(doc['imagenet'], 5), get_top_items(doc['coco'], 5)))
        doc['locations'] = list(zip(get_top_items(doc['places'], 5), get_top_items(doc['places_attributes'], 5)))
        docs.append(doc)
    return docs

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
                if k not in weights[field]:
                    weights[field][k] = v
                else:
                    weights[field][k]['weight'] += v['weight']

    for field, scores in weights.items():
        weights[field] = dict(sorted(scores.items(), key=lambda x: -x[1]['weight'])[:4])

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
                value['weight'] = request.form[f'{category}/{key}']

    return render_template('results.html', query=query, results=search(query, weights),
                           weights={FIELD_MAPPING.get(field, field.capitalize()): v for field, v in weights.items()})

################################################################################
# Running the website

if __name__ == '__main__':
    app.debug = True
    app.run()
