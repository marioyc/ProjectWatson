#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 05 10:55:23 2016

@author: Ana-Maria, Baoyang
"""
import json
import numpy as np
import numpy.linalg as LA
import sys
import os.path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from alchemyapi import AlchemyAPI

alchemyapi = AlchemyAPI()

def build_tf_idf(corpus, voc = None):
    """return a (sparse) tf-idf matrix of given corpus
    if preprocessed is set True and voc (for vocabulary) is given
    the tf-idf matrix is built uniquely using vocabulary
    """
    if voc is None or len(voc) == 0:
        vectorizer = TfidfVectorizer(norm = 'l2')
    else: 
        vectorizer = TfidfVectorizer(vocabulary = voc, norm = 'l2')
    return vectorizer

def build_corpus(filenames, extract_keywords = True):
    """return a corpus and a set of keywords extracted by AlchemyAPI
    filenames is a list of string who are paths of json data files
    """
    vocabulary = []
    reviews = []
    descriptions = []
    for filename in filenames:
        if not os.path.isfile(filename):
            continue
        d, r, v = get_review_keywords(filename)
        if (d, r, v) == ('', '', []):
            continue
        reviews.append(r)
        descriptions.append(d)
        for i in v:
            vocabulary.append(i)
    vocabulary = set(vocabulary)
    return descriptions, reviews, vocabulary

def get_review_keywords(filename, max_nb_reviews = 99, extract_keywords = True):
    """return a string of concatenation of
    certain number (default 99) reviews 
    and a set of keywords extracted by AlchemyAPI
    """
    # load file
    if not os.path.isfile(filename):
        return '', '', []
    with open(filename) as infile:
        data = json.load(infile)
    # extract reviews, if field not exist, None type is returned
    reviews_raw = data.get('reviews')
    description = data.get('description')
    if reviews_raw is None or len(reviews_raw) == 0:
        return description, '', [] 
    # we are only interested in 'body' filed of reviews
    reviews_raw = [i.get('body') for i in reviews_raw]
    # determine how many reviews are going to used
    nb_reviews = min(max_nb_reviews, len(reviews_raw))
    # concatenation of reviews into a single string splited by return
    reviews = '\n'.join(reviews_raw[:nb_reviews])
    if not extract_keywords:
        return description, reviews, [] 
    # extract entities
    response_entities = alchemyapi.entities("text", reviews)  
    entities = [i.get('text') for i in response_entities.get('entities')]
    # extract keywords
    response_keywords = alchemyapi.keywords("text", reviews)
    if response_keywords is None or response_keywords.get('keywords') is None:
        return description, reviews, []
    # we do not consider entities as keywords
    keywords = [i.get('text') for i in response_keywords.get('keywords')]
    return description, reviews, list(set(keywords) - set(entities))
    
def similarities(tf_idf):
    """return a (symmetric) matrix
    contains document-wise similarities
    """
    dist = linear_kernel(tf_idf)
    return dist

cos = lambda a, b : round(np.inner(a, b)/(LA.norm(a)*LA.norm(b)), 3) 
 
def main():
    # if no argument is given, use default setting
    if len(sys.argv) < 2:
        filenames = ['../data/1.json', '../data/35.json','../data/37.json','../data/101.json','../data/41804.json','../data/120725.json', '../data/77366.json', '../data/9520360.json', '../data/14406312.json', '../data/15872.json']
    # otherwise take system argument as file paths
    else:
        filenames = sys.argv[1:]
    descriptions, corpus, vocabulary = build_corpus(filenames)
    # calculate tf-idf matrix based on corpus and vocabulary
#    tf_idf = build_tf_idf(corpus, vocabulary)
    # calculate tf-idf matrix only with corpus
    vect_corpus = build_tf_idf(corpus)
    tf_idf_benchmark=vect_corpus.fit_transform(corpus).toarray()
    # calculate similarity matrices
#    dist = similarities(tf_idf)
    dist_benchmark = similarities(tf_idf_benchmark)
 #   print 'Distance entre les reviews, avec Alchemy: '
  #  print dist
  #  print 'Distance entre les reviews, sans Alchemy: '
    print dist_benchmark
 #   tf_idf_descr=build_tf_idf(descriptions)
#    dist_descr = similarities(tf_idf_descr)   
   # print 'Distance entre les descriptions, sans Alchemy: '
  #  print dist_descr
    query_vect_corpus=vect_corpus.transform(["I want to read and english novel with science-fiction and robot"]).toarray()
    for vector in tf_idf_benchmark:
        for q_v in query_vect_corpus:
            cosine=cos(vector,q_v)
            print cosine
    

#main()
