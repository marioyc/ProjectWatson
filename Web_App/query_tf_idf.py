# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 14:39:16 2016

@author: Ana-Maria,Baoyang
"""

from tf_idf import *
import string
import numpy as np
from sklearn.metrics.pairwise import linear_kernel

def match_query(query, vectorizer_r, matrix_r, ids, top_n = 10):
    """computes the similarity between the query and the corpus
    """
    
    query_vect_corpus = vectorizer_r.transform([query])
    cosine_similarities = linear_kernel(query_vect_corpus, matrix_r).flatten()
    #print cosine_similarities

    #Computing the cosine similarities using the sparse representation of vectors
    coeffs=np.array(cosine_similarities)
    #Fetching the indexes corresponding to the highest top_n cosine
    #similarities between the query and the books
    coeffs_argsort=coeffs.argsort()[::-1][:top_n]
    print 'Top top_n books matched to the query:'
    for i in range(top_n):
        print i,' ',ids[coeffs_argsort[i]],' ',coeffs[coeffs_argsort[i]]
    #Returning the book ids corresponding to the top_n matches
    wtf = [ids[coeffs_argsort[i]] for i in range(top_n)]
    return wtf

# executable only if called explicitly
if __name__ == '__main__':
    from pymongo import MongoClient
    from sklearn.externals import joblib
    import cPickle as pickle
    #initialize a db instance
    mongo=MongoClient()
    query='harry'
    query=query.lower().encode('utf-8').translate(None,string.punctuation)

    cursor = mongo.app.books.find({'keywords': {'$exists': True}})
    ids = [doc['_id'] for doc in cursor]
    vectorizer_r = joblib.load('static/data/vectorizer_r_query.pkl')
    with open('static/data/matrix_r.pkl', 'rb') as infile:
            matrix_r = pickle.load(infile)
            match_query(query,vectorizer_r,matrix_r,ids)
