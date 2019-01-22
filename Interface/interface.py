# Flask-related imports:
from flask import Flask, request, render_template

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


@app.route('/results/', methods=['POST'])
def results():
    """
    Show the results of the submitted query
    """
    text = request.form['textfield']
    mock_data = [{'title': 'Some clip', 'description': 'This is a cool video', 'media': 'image_url'}] * 10
    return render_template('results.html', query=text, results=mock_data)

################################################################################
# Running the website

if __name__ == '__main__':
    app.debug = True
    app.run()
