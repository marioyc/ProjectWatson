# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 11:19:32 2016
@author: Ana-Maria, Baoyang
"""
from tf_idf import *
from functools import partial
from pymongo import MongoClient
from shelves import generate_matr_shelves

def row_to_dict(db, tf_idf, ids, index):
    """convert the index_th row of tf_idf matrix to dictionary
    return only first top_n entries
    """
    top_n = 10
    print 'processing ' + str(index)
    row = {}
    row['_id'] = ids[index]
    # an empty table to store similarities with other books
    col = []
    if top_n is None:
        ids_sort = tf_idf[index, :].argsort()[::-1][1:]
    else:
        ids_sort = tf_idf[index, :].argsort()[::-1][1:top_n+1]
    for i in ids_sort:
        entry = {'_id': ids[i], 'value': tf_idf[index][i]}
        col.append(entry)
    row['value'] = col
    db.similarities.insert_one(row)
    print str(row['_id']) + ' inserted'

def write_tf_idf(db, dist, ids):
    """write dist matrix to collection dist of database
    """
    map(partial(row_to_dict, db, dist, ids), range(len(dist)))

def generate_matrix(db, coeff_d, coeff_r,coeff_s):
    """generate tf_idf matrix
    coeff_d and coeff_r are weights of description and reviews matrix
    """
    print 'fetching ids of processed books...'
    ids = [doc['_id'] for doc in db.keywords.find()]

    print 'loading corpus...'
    #Loading the description and the corpus of reviews
    descriptions, reviews, keywords = build_corpus(db)
    
    print 'building vectorizer...'
    #Building the vectorizer for reviews
    vectorizer_r = build_vectorizer(reviews, keywords)

    print 'vectorizing reviews'
    #joblib.dump(vectorizer_r, 'static/data/vectorizer_r.pkl') 
    matrix_r = vectorizer_r.transform(reviews)
    
    print 'calculating similarities between reviews'
    dist_r = similarities(matrix_r)

    print 'building vectorizer of description...'
    #Building the vectorizer for descriptions
    vectorizer_d = build_vectorizer(descriptions)

    print 'vectorizing descriptions....'
    matrix_d = vectorizer_d.fit_transform(descriptions)

    print 'calculating similarities between descriptions...'
    dist_d = similarities(matrix_d)
    
    #Building the similiarity matrix for the shelves
    dist_s = generate_matr_shelves(db)

    #Normalization
    coeff_rr = coeff_r/(coeff_r+coeff_d+coeff_s)
    coeff_dd = coeff_d/(coeff_r+coeff_d+coeff_s)
    coeff_ss= coeff_s/(coeff_r+coeff_d+coeff_s)

    '''Play with the parameters, uncomment the following lines of code,
    and watch the difference between the similarity matrix
    when using the shelves and when not using them'''
#    dist_without_s=coeff_r/(coeff_r+coeff_d)*dist_r+coeff_d/(coeff_r+coeff_d)*dist_d
#    dist_with_s=coeff_rr*dist_r+coeff_dd*dist_d+coeff_ss*dist_s
#    print dist_with_s-dist_without_s
    return ids, coeff_rr*dist_r+coeff_dd*dist_d+coeff_ss*dist_s
    #return ids, coeff_rr*dist_r+coeff_dd*dist_d

# executable only if called explicitly
if __name__ == '__main__':
    # initialize database instance
    client = MongoClient()
    ids, dist_r = generate_matrix(client.app, 5.0, 2.0, 1.0)
    # write to database
    write_tf_idf(client.app, dist_r, ids)
