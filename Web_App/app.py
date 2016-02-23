from flask import Flask, render_template, request, Response, g
from flask.ext.pymongo import PyMongo
import string
import json
from tf_idf import build_corpus, build_tf_idf
from query_tf_idf import match_query

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

    ## for testing
    #ids = list(range(1, 1000))

    #Loading the description and the corpus of reviews
    descriptions, reviews,_ = build_corpus(mongo.db, ids, extract_keywords = False, query = True)
    #Building the vectorizer for reviews
    vectorizer_r = build_tf_idf(reviews)
    matrix_r = vectorizer_r.fit_transform(reviews).toarray()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    top_n = 10
    query = request.args.get('input_sentence')
    query = query.lower().encode('utf-8').translate(None,string.punctuation)
    matches = match_query(query, vectorizer_r, matrix_r, ids, top_n)
    results = []
    for match in matches:
        book = mongo.db.books.find_one({'_id': str(match)})
        results.append(book)
    #print results
    return render_template('search.html',query=query,results=results)

@app.route('/graph')
def graph():
    center = request.args.get('center')
    result = mongo.db.books.find_one({'_id': str(center)})
    #print result
    return render_template('graph.html',center=center,result=result)

@app.route('/graph_json')
def graph_json():
    center = request.args.get('center')

    matrix = [cursor for cursor in mongo.db.tf_idf.find()]

    pos_dict = {}

    for i, node in enumerate(matrix):
        pos_dict[node['_id'] ] = i

    result = {}
    visited = set()
    Q = set()

    visited.add(center)
    Q.add(center)

    while len(Q) > 0:
        cur = Q.pop()
        pos_cur = pos_dict[cur]
        result[cur] = {'id' : cur}
        neighbourhood = []

        for neighbour in matrix[pos_cur]['value']:
            if neighbour['value'] > 0.31:
                aux = neighbour['_id']

                if aux not in visited:
                    visited.add(aux)
                    Q.add(aux)
                    neighbourhood.append({'id' : aux, 'value' : neighbour['value']})

        result[cur]['value'] = neighbourhood

    return Response(json.dumps(result),  mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
