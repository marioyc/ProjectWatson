# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 11:19:32 2016

@author: Anca
"""

from tf_idf import *
import sys
import codecs
import os.path

def generate_matrix(path_json,coeff_d,coeff_r):
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
    
    #Reading the vocabulary
    vocabulary = set()
    if os.path.isfile(path_json + 'vocabulary.txt'):
        f = codecs.open(path_json + 'vocabulary.txt', 'r', 'utf-8')
        for line in f:
            vocabulary.add(line[:-2])
        f.close()
    #Building the vectorizer for reviews
    vectorizer_r=build_tf_idf(reviews,vocabulary)
    matrix_r=vectorizer_r.fit_transform(reviews).toarray()
    dist_r=similarities(matrix_r)
    
    #Building the vectorizer for descriptions
    vectorizer_d=build_tf_idf(descriptions)
    matrix_d=vectorizer_d.fit_transform(descriptions).toarray()
    dist_d=similarities(matrix_d)
    
    coeff_r=coeff_r/(coeff_r+coeff_d)
    coeff_d=coeff_d/(coeff_r+coeff_d)
    return processed_ids, coeff_r*dist_r+coeff_d*dist_d
    
def main():
    path_json='C:/Users/Anca/Documents/GitHub/ProjectWatson/data/'
    proc_ids,dist_r=generate_matrix(path_json,5,2)
    print proc_ids
    print dist_r

#main()