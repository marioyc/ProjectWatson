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

#import codecs

#with codecs.open(r'D:\Laptop vechi\Desktop laptop vechi\Cursuri Polytechnique\Info\Projet 3A\output\output3.txt', 'r','utf-8') as myfile:
  #  data=myfile.read()

#print data 
def main_2():
    file_path1=r'data/1.json'
    file_path2=r'data/77366.json'
    final_keywords1=read_keywords_from_reviews(file_path1)
    final_keywords2=read_keywords_from_reviews(file_path2)
    print final_keywords2
    final_keywords=final_keywords1+'\t'+final_keywords2
    tfidf = TfidfVectorizer().fit_transform(final_keywords.split('\t'))
    cosine_similarities = linear_kernel(tfidf[0:1], tfidf).flatten()
    print cosine_similarities
  
def build_tf_idf(corpus, voc = None, preprocessed = True):
    if not preprocessed:
        vectorizer = TfidfVectorizer(stop_words = 'english', lowercase = True)
    else: 
        vectorizer = TfidfVectorizer(vocabulary = voc)
    vectorizer.fit(corpus)
    return vectorizer

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

def main_1():
    file_path1=r'data/1.json'
    file_path2=r'data/120725.json'
    final_reviews1=read_reviews_from_file(file_path1)
    final_reviews2=read_reviews_from_file(file_path2)
    final_reviews=final_reviews1+'\t'+final_reviews2
    tfidf = TfidfVectorizer().fit_transform(final_reviews.split('\t'))
    cosine_similarities = linear_kernel(tfidf[0:1], tfidf).flatten()
    print cosine_similarities

def get_review_keywords(filename, max_nb_reviews = 25):
    with open(filename) as infile:
        data = json.load(infile)
    reviews_raw = data.get('reviews')
    if reviews_raw is None:
        return 
    nb_reviews = min(max_nb_reviews, len(reviews_raw))
    reviews = ' '.join(reviews[:nb_reviews])
    response_entities = alchemyapi.entities("text", reviews)  
    entities = [i.get('text') for i in response_entities.get('entities')]
    response_keywords = alchemyapi.keywords("text", reviews)
    if not response_keywords['language'] == 'english':
        return
    keywords = [i.get('text') for i in response_keywords.get('keywords')]
    return reviews_raw, list(set(keywords) - set(entities))
    
   
def main():
    if len(sys.argv) < 2:
        return
    filenames = str(sys.argv)[1:]
    corpus, vocabulary = build_corpus(filenames)
    tf_idf = build_tf_idf(corpus, vocabulary)
    print tf_idf.get_feature_names()

main()
