#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 05 10:55:23 2016

@author: Anca
"""
import json
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from alchemyapi import AlchemyAPI

alchemyapi = AlchemyAPI()

def build_tf_idf(corpus, voc = None, preprocessed = True):
    if not preprocessed:
        vectorizer = TfidfVectorizer(stop_words = 'english', lowercase = True, norm = 'l2')
    else: 
        vectorizer = TfidfVectorizer(vocabulary = voc, norm = 'l2')
    return vectorizer.fit_transform(corpus)

def build_corpus(filenames):
    vocabulary = []
    reviews = []
    for filename in filenames:
        r, v = get_review_keywords(filename)
        reviews.append(r)
        for i in v:
            vocabulary.append(i)
    vocabulary = set(vocabulary)
    return reviews, vocabulary

def get_review_keywords(filename, max_nb_reviews = 25):
    with open(filename) as infile:
        data = json.load(infile)
    reviews_raw = data.get('reviews')
    if reviews_raw is None:
        return 
    reviews_raw = [i.get('body') for i in reviews_raw]
    nb_reviews = min(max_nb_reviews, len(reviews_raw))
    reviews = ' '.join(reviews_raw[:nb_reviews])
    response_entities = alchemyapi.entities("text", reviews)  
    entities = [i.get('text') for i in response_entities.get('entities')]
    response_keywords = alchemyapi.keywords("text", reviews)
    if not response_keywords['language'] == 'english':
        return
    keywords = [i.get('text') for i in response_keywords.get('keywords')]
    return reviews, list(set(keywords) - set(entities))
    
def similarities(tf_idf):
    dist = linear_kernel(tf_idf)
    return dist
   
def main():
    if len(sys.argv) < 2:
        filenames = ['data/1.json', 'data/120725.json', 'data/77366.json']
    else:
        filenames = sys.argv[1:]
    corpus, vocabulary = build_corpus(filenames)
    tf_idf = build_tf_idf(corpus, vocabulary)
    dist = similarities(tf_idf)
    print dist

main()
