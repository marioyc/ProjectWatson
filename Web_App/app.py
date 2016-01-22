from flask import Flask, render_template, request
from query_tf_idf import match_query

import string
import json

app = Flask(__name__)

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/search')
def search():
    path_json = 'data/'
    top_n = 10

    query = request.args.get('input_sentence')
    query = query.lower().encode('utf-8').translate(None,string.punctuation)

    matches = match_query(path_json, query, top_n)
    results = []

    for match in matches:
        f = open(match)
        book = json.load(f)
        results.append(book)

    return render_template('search.html',query=query,results=results)

@app.route('/graph')
def graph():
    center = request.args.get('center')
    return render_template('graph.html',center=center)

if __name__ == '__main__':
  app.run(debug=True)
