# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 14:39:16 2016

@author: Ana-Maria,Baoyang
"""

from tf_idf import *
import string
import os.path
import numpy as np

def cos( a, b): 
    if (np.linalg.norm(a)==0 or np.linalg.norm(b)==0):
        return 0
    else:
        return round(np.inner(a, b)/(np.linalg.norm(a)*np.linalg.norm(b)), 3)

#computes the similarity between the query and the corpus
def match_query(path_json,query,top_n = 10):
    #Fetching the ids that have already been processed
    processed_ids = set()
    if os.path.isfile(path_json + 'alchemy_tentative.txt'):
        f = open(path_json + 'alchemy_tentative.txt')
        for line in f:
            processed_ids.add(int(line.strip()))
        f.close()
    #Keeping only those ids that correspond to an existing .json file
    processed_ids=filter(lambda x: os.path.isfile(path_json+str(x)+'.json'), processed_ids)
    print processed_ids

    #keeping only those filenames that exist
    filenames=[path_json+str(x)+'.json' for x in processed_ids]

    #Loading the description and the corpus of reviews
    descriptions,reviews,_=build_corpus(filenames, extract_keywords = False, query = True)

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
        print i,' ',filenames[coeffs_argsort[i]],' ',coeffs[coeffs_argsort[i]]
    wtf = [filenames[coeffs_argsort[i]] for i in range(top_n)]
    return wtf

if __name__ == '__main__':
    path_json='data/'
    query='I would love to read some science-fiction, science and discovery'
    top_n=10
    simpl_query=query.lower().encode('utf-8').translate(None,string.punctuation)
    match_query(path_json,simpl_query,top_n)
