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
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from alchemyapi import AlchemyAPI
from process_text import process_kw
from pymongo import MongoClient

def build_vectorizer(corpus, voc = None):
    """returns a vectorizer
    if preprocessed is set True and voc (for vocabulary) is given
    the vectorizer is built uniquely using vocabulary
    """
    if voc is None or len(voc) == 0:
        vectorizer = TfidfVectorizer(norm = 'l2',stop_words='english',analyzer='word')
    else: 
        vectorizer = TfidfVectorizer(vocabulary = voc, norm = 'l2',stop_words='english',analyzer='word')
    vectorizer.fit(corpus)
    return vectorizer


def build_corpus(db):
    """returns a corpus and a set of keywords extracted by AlchemyAPI
    only documents of given ids in database are considered
    """
    # Load the dictionary file, containing the words not to be taken into account
    keywords = []
    reviews = []
    descriptions = []
    cursor = db.keywords.find()
    for idx in cursor:
        id = idx['_id']
        doc = db.books.find_one({'_id': str(id)})
        descriptions.append(doc['description'])
        reviews_this = [review['body'] for review in db['reviews']]
        reviews.append('\n'.join(reviews_this))

        keywords_this = [review['keywords'] for review in idx['reviews']]
        keywords_this = list(set([process_kw(keyword) for keyword in keywords_this]))
        keywords.extend(keywords_this)
    keywords = list(set(keywords))
    return descriptions, reviews, keywords

def process_keywords_book(db):
    cursor = db.keywords.find()
    for idx in cursor:
        id = idx['_id']
        keywords_this = [review['keywords'] for review in idx['reviews']]
        keywords_this = list(set([process_kw(keyword) for keyword in keywords_this]))
        db.keywords.update(
            {'_id': str(id)},
            {'$set': {
                        'keywords': keywords_this
                    }
            }
        )

def extract_keywords_each(db, id, max_nb_reviews=99):
    """returns a string of concatenation of
    certain number (default 99) reviews 
    and a set of keywords extracted by AlchemyAPI
    """
    # get document with given id
    data = db.books.find_one(str(id))
    # if None, that means book doesn't exist
    if data is None:
        print str(id) + ' not found'
        return

    print str(id) + ' processing'

    # extract reviews, if field not exist, None type is returned
    reviews_raw = data.get('reviews')

    if reviews_raw is None or len(reviews_raw) == 0:
        print str(id) + ' empty reviews'
        return

    # we are only interested in 'body' filed of reviews
    reviews_raw = [(i.get('_id'), i.get('body')) for i in reviews_raw]

    # remove duplicate reviews
    reviews_raw = list(set(reviews_raw))

    # determine how many reviews are going to used
    nb_reviews = min(max_nb_reviews, len(reviews_raw))

    # concatenation of reviews into a single string splited by return

    reviews = reviews_raw[:nb_reviews]

    for idx, review in reviews:
        # inspecting progress
        print str(idx) + " calling alchemy"
        # extract keywords
        response_keywords = alchemyapi.keywords("text", review)
        if response_keywords is not None and response_keywords.get('keywords') is not None:
            db.keywords.update(
                    {'_id': str(id)},
                    {'$push': {
                        'reviews': {
                                    '_id': str(idx),
                                    'keywords': response_keywords.get('keywords')
                                    }
                             }
                    }
            )
    
def similarities(tf_idf):
    """returns a (symmetric) matrix
    contains document-wise similarities
    """
    dist = linear_kernel(tf_idf)
    return dist

# executable only if called explicitly
if __name__ == '__main__':
    alchemyapi = AlchemyAPI()
    # initialize an instance
    client = MongoClient()
    # number of documents to be proceeded
    nb_doc_to_extract = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    # save vocabulary to database
    save_vocabulary(client.app, nb_doc_to_extract)