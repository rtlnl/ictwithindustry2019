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

################################################################################
# Webpage-related functions

@app.route('/', methods=['GET'])
def main_page():
    """
    Function to display the main page.
    This is the first thing you see when you load the website.
    """
    return render_template('index.html')

try:
    assert es.cluster.health(timeout='10s').get('status') == 'green'
    MOCK_ES = False
except:
    app.logger.warn('Cannot connect to Elasticsearch, using mock data.')
    MOCK_ES = True

def search(query):
    if MOCK_ES:
        with open('static/search.json') as f:
            search_data = json.load(f)
    else:
        search_data = es.search(q=query)

    docs = []
    for row in search_data["hits"]["hits"]:
        doc = row['_source']
        doc['id'] = row["_id"]
        doc["title"] = doc["title"].replace(" - RTL NIEUWS - YouTube", "")
        item_date_raw = doc["meta"]["datePublished"].split('-')
        doc['date'] = "{0}-{1}-{2}".format(item_date_raw[2], item_date_raw[1], item_date_raw[0])
        doc['description'] = doc['description'].replace("Abonneer je GRATIS voor meer video\\xc2\\x92s: http://r.tl/1JBmAcsVolg nu LIVE het nieuws op: http://www.rtlnieuws.nlFacebook : https://www.facebook.com/rtlnieuwsnlTwitter : https://twitter.com/rtlnieuwsnl", "")
        doc['url'] = doc["meta"]["og:video:url"]
        doc['tags'] = [tag.capitalize() for tag in doc["meta"]["og:video:tag"][4:]]
        docs.append(doc)
    return docs

weights = {
    'BM25': {
        'title': {'nl': 'Titel', 'weight': 50},
        'description': {'nl': 'Beschrijving', 'weight': 20},
        'tags': {'nl': 'Tags', 'weight': 10}
    },
    'Coco': {
        'title': {'nl': 'Titel', 'weight': 50},
        'description': {'nl': 'Beschrijving', 'weight': 20},
        'tags': {'nl': 'Tags', 'weight': 10}
    }
}

@app.route('/results/', methods=['POST'])
def results():
    """
    Show the results of the submitted query
    """
    text = request.form['textfield']
    for category in weights:
        for key, value in weights[category].items():
            if key in request.form:
                value['weight'] = request.form[key]
    return render_template('results.html', query=text, results=search(text), weights=weights)

################################################################################
# Running the website

if __name__ == '__main__':
    app.debug = True
    app.run()
