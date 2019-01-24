# Flask-related imports:
from flask import Flask, request, render_template
import json

################################################################################
# Load data


################################################################################
# Set up general functions


################################################################################
# Set up app:
app = Flask(__name__)

################################################################################
# Webpage-related functions

@app.route('/', methods=['GET'])
def main_page():
    """
    Function to display the main page.
    This is the first thing you see when you load the website.
    """
    return render_template('index.html')


@app.route('/initial-query/', methods=['POST'])
def initial_query():
    """
    Show the interpretation of the user query.
    Users can still modify their query.
    """
    text = request.form['textfield']
    return render_template('initial_query.html', query=text)


@app.route('/advanced/', methods=['GET'])
def advanced():
    """
    Function to display the main page.
    This is the first thing you see when you load the website.
    """
    return render_template('advanced.html')

MOCK_DATA = [{'title': 'Some clip', 'description': 'This is a cool video', 'shots': ['/static/Frames/frame0001.jpg']*5}] * 10

with open('static/search.json') as f:
    search_data = json.load(f)

MOCK_DATA = []
for row in search_data["hits"]["hits"]:
    title = row["_source"]["title"].replace(" - RTL NIEUWS - YouTube", "")
    description = row["_source"]['description'].decode('utf8').encode('ascii', errors='ignore')
    item_date_raw = row["_source"]["meta"]["datePublished"].split('-')
    item_date = "{0}-{1}-{2}".format(item_date_raw[2], item_date_raw[1], item_date_raw[0])
    chapeau = row["_source"]["meta"]["keywords"].split(', ')[4].capitalize()
    description = description.replace("Abonneer je GRATIS voor meer video\\xc2\\x92s: http://r.tl/1JBmAcsVolg nu LIVE het nieuws op: http://www.rtlnieuws.nlFacebook : https://www.facebook.com/rtlnieuwsnlTwitter : https://twitter.com/rtlnieuwsnl", "")
    MOCK_DATA.append({'title': title,
                      'description': description,
                      'url': row["_source"]["meta"]["og:video:url"],
                      'date': item_date,
                      'chapeau': chapeau,
                      'shots': ['/static/Frames/frame0001.jpg']*5})

MOCK_QUERIES = ['aap', 'hond', 'kat', 'cavia']

@app.route('/results/', methods=['POST'])
def results():
    """
    Show the results of the submitted query
    """
    text = request.form['textfield']
    return render_template('results.html', query=text, results=MOCK_DATA, related_queries=MOCK_QUERIES)

################################################################################
# Running the website

if __name__ == '__main__':
    app.debug = True
    app.run()
