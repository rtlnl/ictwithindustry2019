# Flask-related imports:
from flask import Flask, request, render_template
import json
import elasticsearch
import requests

################################################################################
# Load data


################################################################################
# Set up general functions


################################################################################
# Set up app:
app = Flask(__name__)
es = elasticsearch.Elasticsearch()

CONCEPT_FIELDS = ('places', 'places_attributes', 'places_environment', 'coco', 'coco_count', 'imagenet')
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
        concept_scores = requests.get(f'http://localhost:5001/{term}').json()
        for field, scores in concept_scores.items():
            weights[FIELD_MAPPING.get(field, field.capitalize())] = dict(sorted(scores.items(), key=lambda x: -x[1]['weight'])[:4])
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
    return render_template('results.html', query=query, results=search(query, weights['Tekst']), weights=weights)

################################################################################
# Running the website

if __name__ == '__main__':
    app.debug = True
    app.run()
