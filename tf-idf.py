#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 05 10:55:23 2016

@author: Anca changed
"""
import json
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from alchemyapi import AlchemyAPI

alchemyapi = AlchemyAPI()

def build_tf_idf(corpus, preprocessed = False, voc = None):
    if not preprocessed:
        #vectorizer = TfidfVectorizer(stop_words = 'english', lowercase = True, norm = 'l2')
        vectorizer = TfidfVectorizer(norm = 'l2')
    else: 
        vectorizer = TfidfVectorizer(vocabulary = voc, norm = 'l2')
    return vectorizer.fit_transform(corpus)

def build_corpus(filenames):
    vocabulary = []
    reviews = []
    descriptions=[]
    for filename in filenames:
        d, r, v = get_review_keywords(filename)
        reviews.append(r)
        descriptions.append(d)
        for i in v:
            vocabulary.append(i)
    vocabulary = set(vocabulary)
    return descriptions,reviews, vocabulary

def get_review_keywords(filename, max_nb_reviews = 99):
    with open(filename) as infile:
        data = json.load(infile)
    reviews_raw = data.get('reviews')
    description=data.get('description')
    if reviews_raw is None or len(reviews_raw) == 0:
        return '', [] 
    reviews_raw = [i.get('body') for i in reviews_raw]
    nb_reviews = min(max_nb_reviews, len(reviews_raw))
    reviews = '\n'.join(reviews_raw[:nb_reviews])
    response_entities = alchemyapi.entities("text", reviews)  
    entities = [i.get('text') for i in response_entities.get('entities')]
    response_keywords = alchemyapi.keywords("text", reviews)
    if not response_keywords['language'] == 'english':
        return
    keywords = [i.get('text') for i in response_keywords.get('keywords')]
    return description, reviews, list(set(keywords) - set(entities))
    
def similarities(tf_idf):
    dist = linear_kernel(tf_idf)
    return dist
   
def main():
    if len(sys.argv) < 2:
        filenames = ['data/1.json','data/35.json','data/120725.json', 'data/77366.json', 'data/9520360.json',  'data/15872.json']
    else:
        filenames = sys.argv[1:]
    descriptions, corpus, vocabulary = build_corpus(filenames)
    tf_idf = build_tf_idf(corpus, True, vocabulary)
    tf_idf_benchmark = build_tf_idf(corpus)
    dist = similarities(tf_idf)
    dist_benchmark = similarities(tf_idf_benchmark)
    print 'Distance entre les reviews, avec Alchemy: '
    print dist
    print 'Distance entre les reviews, sans Alchemy: '
    print dist_benchmark
    tf_idf=build_tf_idf(descriptions)
    dist_descr=similarities(tf_idf)   
    print 'Distance entre les descriptions, sans Alchemy: '
    print dist_descr

main()
