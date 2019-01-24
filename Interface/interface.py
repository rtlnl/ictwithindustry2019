# Flask-related imports:
from flask import Flask, request, render_template
import json
import elasticsearch

################################################################################
# Load data


################################################################################
# Set up general functions


################################################################################
# Set up app:
app = Flask(__name__)
es = elasticsearch.Elasticsearch()

CONCEPT_FIELDS = ('places', 'places_attributes', 'places_environment', 'coco', 'coco_count', 'imagenet')

try:
    assert es.cluster.health(timeout='10s').get('status') == 'green'
    MOCK_ES = False
    all_docs = es.search('ictwi2019', size=10000, _source=CONCEPT_FIELDS, timeout='60s')["hits"]["hits"]
except:
    raise
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
        'BM25': {
            'title': {'nl': 'Titel', 'weight': 50},
            'description': {'nl': 'Beschrijving', 'weight': 20},
            'meta.og:video:tag': {'nl': 'Tags', 'weight': 10},
            'clean_ocr': {'nl': 'OCR', 'weight': 10}
        },
        'Coco': {
            'cow': {'nl': 'Koe', 'weight': 50},
            'person': {'nl': 'Persoon', 'weight': 20},
            'tree': {'nl': 'Boom', 'weight': 10}
        }
    }
    return weights

@app.route('/results/', methods=['POST'])
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
    return render_template('results.html', query=query, results=search(query, weights['BM25']), weights=weights)

################################################################################
# Running the website

if __name__ == '__main__':
    app.debug = True
    app.run()
