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

alchemyapi = AlchemyAPI()

os.environ['HTTP_PROXY']="http://kuzh.polytechnique.fr:8080"
os.environ['HTTPS_PROXY']="http://kuzh.polytechnique.fr:8080"

if os.name != 'posix':
    path = 'C:/Users/Anca/Documents/GitHub/ProjectWatson/data/'
else:
    path = './data/'

filetype = '.json'

def build_tf_idf(corpus, voc = None):
    """return a (sparse) tf-idf matrix of given corpus
    if preprocessed is set True and voc (for vocabulary) is given
    the tf-idf matrix is built uniquely using vocabulary
    """
    if voc is None or len(voc) == 0:
        vectorizer = TfidfVectorizer(norm = 'l2',stop_words='english',analyzer='word')
    else: 
        vectorizer = TfidfVectorizer(vocabulary = voc, norm = 'l2',stop_words='english')
    return vectorizer

def build_corpus(filenames, max_nb_reviews = 99, extract_keywords = True, concat_to_extract = True):
    """return a corpus and a set of keywords extracted by AlchemyAPI
    filenames is a list of string who are paths of json data files
    """
    #Load the dictionary file, containing the words not to be taken into account   
    dictpath= path + 'dictionary.txt'
    dictfile= []
    dictio = {'0': '0'}
    shelf_vectors=[]
    if os.path.isfile(path + 'alchemy_tentative.txt'):
        with open(dictpath,'r') as dictionaryfile:
            dictfile = dictionaryfile.readlines()
        dictfile=[x[:-1] for x in dictfile]
    
    vocabulary = []
    reviews = []
    descriptions = []
    for filename in filenames:
        shelf_vect, d, r, v = get_review_keywords(filename, dictio, dictfile, max_nb_reviews, extract_keywords,
                                                  concat_to_extract)
        shelf_vectors.append(shelf_vect)        
        reviews.append(r.lower().encode('utf-8').translate(None, string.punctuation))
        descriptions.append(d)
        for i in v:
            vocabulary.append(i)
        print filename + ' processed'
    vocabulary = list(set(vocabulary))
    
    #Resizing the vectors inside the shelf_vectors matrix
    for i in range(len(shelf_vectors)):
        shelf_vectors[i].resize(len(shelf_vectors[-1]))
    return shelf_vectors, descriptions, reviews, vocabulary
        

def get_review_keywords(filename, dictio = {'0' : '0'}, dictfile = [], max_nb_reviews=99, extract_keywords=True, concat_to_extract=True):
    """return a string of concatenation of
    certain number (default 99) reviews 
    and a set of keywords extracted by AlchemyAPI
    """
    # load file
    if not os.path.isfile(filename):
        return [], '', '', []
    with open(filename) as infile:
        data = json.load(infile)
    # extract reviews, if field not exist, None type is returned
    reviews_raw = data.get('reviews')
    description = data.get('description')
    # shelves
    shelves = list(set(list(set(data.get('shelves').keys())-set(dictfile)) + dictio.keys()))
    shelf_vect = np.zeros(len(shelves))
    
    for shelf in shelves:
        found = dictio.get(shelf,0)
        if (found>0):
            shelf_vect[found]=data.get('shelves').get(shelf,0)
        else :
            dictio[shelf]=len(dictio)
            shelf_vect[dictio[shelf]]=data.get('shelves').get(shelf,0) 
    
    if reviews_raw is None or len(reviews_raw) == 0:
        return shelf_vect, description, '', []
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
        return shelf_vect, description, '\n'.join(reviews), []
    keywords = []
    entities = []
    print 'Number of reviews:',len(reviews)
    for review in reviews:
        # extract entities
        response_entities = alchemyapi.entities("text", review)
        if response_entities is not None and response_entities.get('entities') is not None:
            entities.extend([i.get('text') for i in response_entities.get('entities')])
        # extract keywords
        response_keywords = alchemyapi.keywords("text", review)
        if response_keywords is not None and response_keywords.get('keywords') is not None:
            keywords.extend([i.get('text')+i.get('relevance') for i in response_keywords.get('keywords')])
        print keywords
    return shelf_vect, description, '\n'.join(reviews), list(set(keywords) - set(entities))
    
def similarities(tf_idf):
    """return a (symmetric) matrix
    contains document-wise similarities
    """
    dist = linear_kernel(tf_idf)
    return dist

def main():
   filenames = ['../data/1.json', '../data/35.json','../data/37.json','../data/101.json','../data/41804.json','../data/120725.json', '../data/77366.json', '../data/9520360.json',  '../data/15872.json']
   _, d, r, voc=get_review_keywords(filenames[0],max_nb_reviews=5,concat_to_extract=False)
   print voc

main()
