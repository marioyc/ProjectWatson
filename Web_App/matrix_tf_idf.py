# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 11:19:32 2016
@author: Ana-Maria, Baoyang
"""
from tf_idf import *
from functools import partial
from pymongo import MongoClient
from shelves import generate_matr_shelves

def row_to_dict(tf_idf, ids, index, top_n = 10):
    """convert the index_th row of tf_idf matrix to dictionary
    return only first top_n entries
    """
    row = {}
    row['_id'] = ids[index]
    # an empty table to store similarities with other books
    col = []
    ids_sort = tf_idf[index, :].argsort()[::-1][1:top_n+1]
    for i in ids_sort:
        entry = {'_id': ids[i], 'value': tf_idf[index][i]}
        col.append(entry)
    row['value'] = col
    return row

def write_tf_idf(db, tf_idf, ids):
    """write tf_idf matrix to collection tf_idf of database
    """
    assert tf_idf.shape[0] == len(ids)
    res = map(partial(row_to_dict, tf_idf, ids), range(len(ids)))
    for wtf in res:
        db.tf_idf.insert_one(wtf)
        print str(wtf['_id']) + ' inserted'

def generate_matrix(db, coeff_d, coeff_r,coeff_s):
    """generate tf_idf matrix
    coeff_d and coeff_r are weights of description and reviews matrix
    """
    
    # get a cursor that runs over all books with vocabulary extracted
    cursor = db.books.find({'keywords': {'$exists': True}})
    # obtain their ids
    # clearly this stage can be optimized
    ids = [doc['_id'] for doc in cursor]

    #Reading the vocabulary
    vocabulary = []
    for doc in cursor:
        vocabulary.extend(doc['keywords'])
    vocabulary = list(set(vocabulary))

    #Loading the description and the corpus of reviews
    descriptions, reviews,_ = build_corpus(db, ids, extract_keywords = False, concat_to_extract = False)
    
    #Building the vectorizer for reviews
    vectorizer_r = build_tf_idf(reviews, vocabulary)
    #joblib.dump(vectorizer_r, 'static/data/vectorizer_r.pkl') 
    matrix_r = vectorizer_r.fit_transform(reviews).toarray()
    
    dist_r = similarities(matrix_r)

    #Building the vectorizer for descriptions
    vectorizer_d = build_tf_idf(descriptions)
    #joblib.dump(vectorizer_d, 'static/data/vectorizer_d.pkl') 
    matrix_d = vectorizer_d.fit_transform(descriptions).toarray()
    dist_d = similarities(matrix_d)
    
    #Building the similiarity matrix for the shelves
    dist_s=generate_matr_shelves(db)

    #Normalization
    coeff_rr = coeff_r/(coeff_r+coeff_d+coeff_s)
    coeff_dd = coeff_d/(coeff_r+coeff_d+coeff_s)
    coeff_ss= coeff_s/(coeff_r+coeff_d+coeff_s)

    print coeff_rr, coeff_dd, coeff_ss

    return ids, coeff_rr*dist_r+coeff_dd*dist_d+coeff_ss*dist_s

# executable only if called explicitly
if __name__ == '__main__':
    # initialize database instance
    client = MongoClient()
    proc_ids, dist_r = generate_matrix(client.app, 5.0, 2.0,1.0)
    # write to database
    write_tf_idf(client.app, dist_r, list(proc_ids))
