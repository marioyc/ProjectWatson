# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 14:39:16 2016

@author: Ana-Maria,Baoyang
"""

from tf_idf import *
import string
import os.path
import numpy as np
from pymongo import MongoClient

def cos( a, b): 
    if (np.linalg.norm(a)==0 or np.linalg.norm(b)==0):
        return 0
    else:
        return round(np.inner(a, b)/(np.linalg.norm(a)*np.linalg.norm(b)), 3)

#computes the similarity between the query and the corpus
def match_query(db, query, top_n = 10):
    #Fetching the ids that have already been processed
    ids = list(range(1, 1000))

    #Loading the description and the corpus of reviews
    descriptions, reviews,_ = build_corpus(db, ids, extract_keywords = False, query = True)

    #Building the vectorizer for reviews
    vectorizer_r=build_tf_idf(reviews)
    matrix_r=vectorizer_r.fit_transform(reviews).toarray()

    coeffs=[]
    query_vect_corpus=vectorizer_r.transform([query]).toarray()
    for vector in matrix_r:
        for q_v in query_vect_corpus:
            cosine=cos(vector,q_v)
            coeffs.append(cosine)
    coeffs_array=np.array(coeffs)
    coeffs_argsort=coeffs_array.argsort()[::-1][:top_n]
    for i in range(top_n):
        print i,' ',ids[coeffs_argsort[i]],' ',coeffs[coeffs_argsort[i]]
    wtf = [ids[coeffs_argsort[i]] for i in range(top_n)]
    print wtf
    return wtf

if __name__ == '__main__':
    client = MongoClient()
    query='I would love to read some science-fiction, science and discovery'
    top_n=10
    simpl_query=query.lower().encode('utf-8').translate(None,string.punctuation)
    match_query(client.app,simpl_query,top_n)
