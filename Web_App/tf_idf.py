#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 05 10:55:23 2016
@author: Ana-Maria, Baoyang
"""
import string
import json
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from alchemyapi import AlchemyAPI
from process_text import process_kw
from pymongo import MongoClient

alchemyapi = AlchemyAPI()

def build_tf_idf(corpus, voc = None):
    """returns a vectorizer
    if preprocessed is set True and voc (for vocabulary) is given
    the vectorizer is built uniquely using vocabulary
    """
    if voc is None or len(voc) == 0:
        vectorizer = TfidfVectorizer(norm = 'l2',stop_words='english',analyzer='word')
    else: 
        vectorizer = TfidfVectorizer(vocabulary = voc, norm = 'l2',stop_words='english',analyzer='word')
    return vectorizer

def build_corpus_query(db, max_nb_reviews = 99):
    """returns a corpus and a set of keywords extracted by AlchemyAPI
    only documents of given ids in database are considered
    """
    # Load the dictionary file, containing the words not to be taken into account
    reviews = []
    descriptions = []
    cursor = db.books.find({'keywords': {'$exists': True}})
    # loop over books
    for doc in cursor:
        print 'processing ' + doc['_id']
        # get descriptions, reviews and splitted keywords, if there are any
        reviews_raw = doc.get('reviews')
        description = doc.get('description')

        if reviews_raw is None or len(reviews_raw) == 0:
            print str(id) + ' empty reviews'
            return description, '', []

        # we are only interested in 'body' filed of reviews
        reviews_raw = [i.get('body') for i in reviews_raw]

        # remove duplicate reviews
        reviews_raw = list(set(reviews_raw))

        # determine how many reviews are going to used
        nb_reviews = min(max_nb_reviews, len(reviews_raw))

        # concatenation of reviews into a single string splited by return
        reviews_single = ['\n'.join(reviews_raw[:nb_reviews])]
        reviews_single = '\n'.join(reviews_single)

        reviews.append(reviews_single)
        descriptions.append(description)
    return descriptions, reviews

def build_corpus(db, ids, max_nb_reviews = 99, extract_keywords = True, concat_to_extract = True, query = False):
    """returns a corpus and a set of keywords extracted by AlchemyAPI
    only documents of given ids in database are considered
    """
    # Load the dictionary file, containing the words not to be taken into account
    vocabulary = []
    reviews = []
    descriptions = []

    # loop over books
    for id in ids:
        # get descriptions, reviews and splitted keywords, if there are any
        d, r, v = get_review_keywords(db, id, max_nb_reviews, extract_keywords, concat_to_extract, query)
        reviews.append(r)
        descriptions.append(d)
        for i in v:
            vocabulary.append(i)
    # make sure that keywords are unique
    vocabulary = list(set(vocabulary))
    return descriptions, reviews, vocabulary
        

def get_review_keywords(db, id, max_nb_reviews=99, extract_keywords = True, concat_to_extract = True, query = False):
    """returns a string of concatenation of
    certain number (default 99) reviews 
    and a set of keywords extracted by AlchemyAPI
    """
    # get document with given id
    data = db.books.find_one(str(id))
    # if None, that means book doesn't exist
    if data is None:
        print str(id) + ' not found'
        return '', '', []
    print str(id) + ' processing'

    # extract reviews, if field not exist, None type is returned
    reviews_raw = data.get('reviews')
    description = data.get('description')

    if reviews_raw is None or len(reviews_raw) == 0:
        print str(id) + ' empty reviews'
        return description, '', []

    # we are only interested in 'body' filed of reviews
    reviews_raw = [i.get('body') for i in reviews_raw]

    # remove duplicate reviews
    reviews_raw = list(set(reviews_raw))

    # determine how many reviews are going to used
    nb_reviews = min(max_nb_reviews, len(reviews_raw))

    # concatenation of reviews into a single string splited by return
    if concat_to_extract:
        reviews = ['\n'.join(reviews_raw[:nb_reviews])]
    else:
        reviews = reviews_raw[:nb_reviews]
    if not extract_keywords:
        return description, '\n'.join(reviews), []

    # if keywords already extracted
    # return directly
    cursor = db.books.find_one({'_id': str(id)})
    if cursor.has_key('keywords'):
        return description, '\n'.join(reviews), cursor.get('keywords')

    keywords = []
    entities = []
    for idx, review in enumerate(reviews):
        # inspecting progress
        print str(idx) + " calling alchemy"
        # extract entities
        response_entities = alchemyapi.entities("text", review)
        if response_entities is not None and response_entities.get('entities') is not None:
            entities.extend([i.get('text') for i in response_entities.get('entities')])
        # extract keywords
        response_keywords = alchemyapi.keywords("text", review)
        if response_keywords is not None and response_keywords.get('keywords') is not None:
            l=[]
            for i in response_keywords.get('keywords'):
                l=i.get('text')+l
            keywords=l+keywords
	else:
            return description, '\n'.join(reviews), []
    #Processing the text of reviews - removing the upper case letters,
    # And the punctuation except for the '
    reviews = [review for review in reviews]
    return description, '\n'.join(reviews), list(set(keywords) - set(entities))
    
def similarities(tf_idf):
    """returns a (symmetric) matrix
    contains document-wise similarities
    """
    dist = linear_kernel(tf_idf)
    return dist

# executable only if called explicitly
if __name__ == '__main__':
   filenames = ['../data/1.json', '../data/35.json','../data/37.json','../data/101.json','../data/41804.json','../data/120725.json', '../data/77366.json', '../data/9520360.json',  '../data/15872.json']
   d, r, voc=get_review_keywords(filenames[0],concat_to_extract=False)
   print voc
