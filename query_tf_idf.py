# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 14:39:16 2016

@author: Anca
"""

from tf_idf import *
import sys
import codecs
import os.path

#computes the similarity between the query and the corpus
def match_query(query,top_n):
    query_vect_corpus=vect_corpus.transform([query]).toarray()
    for vector in tf_idf_benchmark:
        for q_v in query_vect_corpus:
            cosine=cos(vector,q_v)
            print cosine