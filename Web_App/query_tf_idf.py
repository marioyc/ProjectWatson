# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 14:39:16 2016

@author: Anca
"""

import string
import os.path

from numpy import array, inner
from numpy.linalg import norm

from tf_idf import *

def cos(a, b):
    if norm(a) == 0 or norm(b) == 0:
        return 0
    else:
        return round(inner(a, b)/(norm(a) * norm(b)), 3)

#computes the similarity between the query and the corpus
def match_query(path_json,query,top_n):
    #Fetching the ids that have already been processed
    processed_ids = set()
    if os.path.isfile(path_json + 'processed.txt'):
        f = open(path_json + 'processed.txt')
        for line in f:
            processed_ids.add(int(line.strip()))
        f.close()
    #Keeping only those ids that correspond to an existing .json file
    processed_ids=filter(lambda x: os.path.isfile(path_json+str(x)+'.json'), processed_ids)

    #keeping only those filenames that exist
    filenames=[path_json+str(x)+'.json' for x in processed_ids]

    #Loading the description and the corpus of reviews
    descriptions,reviews,_=build_corpus(filenames,False)

    #Building the vectorizer for reviews
    vectorizer_r=build_tf_idf(reviews)
    matrix_r=vectorizer_r.fit_transform(reviews).toarray()

    coeffs=[]
    query_vect_corpus=vectorizer_r.transform([query]).toarray()
    for vector in matrix_r:
        for q_v in query_vect_corpus:
            cosine=cos(vector,q_v)
            coeffs.append(cosine)
    coeffs_array=array(coeffs)
    coeffs_argsort=coeffs_array.argsort()[::-1][:top_n]
    results = []

    for i in range(top_n):
        results.append(filenames[coeffs_argsort[i]])
        #print i,' ',filenames[coeffs_argsort[i]],' ',coeffs[coeffs_argsort[i]]
        # print reviews[coeffs_argsort[i]]

    return results

"""def main():
    path_json='C:/Users/Anca/Documents/GitHub/ProjectWatson/data/'
    query='I would love to read some science-fiction, science and discovery'
    top_n=10
    simpl_query=query.lower().encode('utf-8').translate(None,string.punctuation)
    match_query(path_json,simpl_query,top_n)

#main()"""
