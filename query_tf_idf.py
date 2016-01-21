# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 14:39:16 2016

@author: Anca
"""

from tf_idf import *
import sys
import codecs
import os.path

 query_vect_corpus=vect_corpus.transform(["I want to read and english novel with science-fiction and robot"]).toarray()
    for vector in tf_idf_benchmark:
        for q_v in query_vect_corpus:
            cosine=cos(vector,q_v)
            print cosine