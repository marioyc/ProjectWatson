# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 14:39:16 2016

@author: Anca
"""

from tf_idf import *
import sys
import codecs
import os.path

def cos( a, b): 
    if (LA.norm(a)==0 or LA.norm(b)==0): 
        return 0
    else:
        return round(np.inner(a, b)/(LA.norm(a)*LA.norm(b)), 3) 

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
    coeffs_array=np.array(coeffs)
    coeffs_argsort=coeffs_array.argsort()[::-1][:top_n]
    for i in range(top_n):
        print i,' ',filenames[coeffs_argsort[i]],' ',coeffs[coeffs_argsort[i]]
        print descriptions[coeffs_argsort[i]]
            
def main():
    path_json='C:/Users/Anca/Documents/GitHub/ProjectWatson/data/'
    query='I would love to read an adventure book with cool characters, thrilling plot and fantastic setting, trees and grass'
    top_n=10
    match_query(path_json,query,top_n)
    
main()
    