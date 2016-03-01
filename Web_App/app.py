from flask import Flask, render_template, request, Response, g
from flask.ext.pymongo import PyMongo
import string
import json
import os
from tf_idf import build_corpus, build_corpus_query, build_tf_idf
from query_tf_idf import match_query
from sklearn.externals import joblib
import cPickle as pickle

app = Flask(__name__)
mongo = PyMongo(app)


@app.before_first_request
def before_first_request():
    """execute before first request
    """
    global ids, vectorizer_r, matrix_r
    ## for latter usage
    cursor = mongo.db.books.find({'keywords': {'$exists': True}})
    ids = [doc['_id'] for doc in cursor]

    #If the data folder does not exist create it
    if not os.path.exists('static/data'):
        os.makedirs('static/data')

    if os.path.isfile('static/data/vectorizer_r_query.pkl'):
        vectorizer_r = joblib.load('static/data/vectorizer_r_query.pkl')
    else:
        #Loading the description and the corpus of reviews
        _, reviews = build_corpus_query(mongo.db)
        #Building the vectorizer for reviews
        vectorizer_r = build_tf_idf(reviews)
        vectorizer_r.fit(reviews)
        joblib.dump(vectorizer_r, 'static/data/vectorizer_r_query.pkl')

    if os.path.isfile('static/data/matrix_r.pkl'):
        with open('static/data/matrix_r.pkl', 'rb') as infile:
            matrix_r = pickle.load(infile)
    else:
        matrix_r = vectorizer_r.transform(reviews)
        with open('static/data/matrix_r.pkl', 'wb') as outfile:
            pickle.dump(matrix_r, outfile, pickle.HIGHEST_PROTOCOL)
    #matrix_r = vectorizer_r.fit_transform(reviews).toArray()
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    top_n = 10
    query = request.args.get('input_sentence')
    matches = match_query(query, vectorizer_r, matrix_r, ids, top_n)
    results = []
    for match in matches:
        book = mongo.db.books.find_one({'_id': str(match)})
        results.append(book)
    return render_template('search.html',query=query,results=results)

@app.route('/book_json')
def book_json():
    id = request.args.get('id')
    book = mongo.db.books.find_one({'_id' : str(id)},
                projection=['title', 'description', 'authors', 'publisher',
                            'publication_year', 'image_url', 'isbn'])
    return Response(json.dumps(book),  mimetype='application/json')

@app.route('/graph')
def graph():
    center = request.args.get('center')
    result = mongo.db.books.find_one({'_id': str(center)})
    return render_template('graph.html',center=center,result=result)

@app.route('/graph_json')
def graph_json():
    center = request.args.get('center')

    matrix = [cursor for cursor in mongo.db.tf_idf.find()]

    pos_dict = {}

    for i, node in enumerate(matrix):
        pos_dict[node['_id'] ] = i

    result = {'nodes' : [], 'edges' : []}
    visited = set()
    done = set()
    Q = set()

    visited.add(center)
    Q.add(center)
    edge_cont = 0

    while len(Q) > 0:
        cur = Q.pop()
        done.add(cur)
        title = mongo.db.books.find_one({'_id' : cur}, projection=['title'])['title']
        pos_cur = pos_dict[cur]
        node_size = 1

        for neighbour in matrix[pos_cur]['value']:
            if neighbour['value'] > 0.16:
                aux = neighbour['_id']

                if aux not in visited:
                    visited.add(aux)
                    Q.add(aux)
                    result['edges'].append({
                        'id' : edge_cont,
                        'source' : cur,
                        'target' : aux,
                        #'label' : str(int(neighbour['value'] * 1000) / 1000.0)
                    })
                    edge_cont += 1
                    node_size += 1
                elif aux not in done:
                    result['edges'].append({
                        'id' : edge_cont,
                        'source' : cur,
                        'target' : aux,
                        #'label' : str(int(neighbour['value'] * 1000) / 1000.0)
                    })
                    edge_cont += 1

        result['nodes'].append({'id' : cur, 'size' : node_size, 'label' : title})

    return Response(json.dumps(result),  mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
