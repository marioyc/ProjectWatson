# -*- coding: utf-8 -*-
"""
Created on Tue Jan 05 10:55:23 2016

@author: Anca
"""
import json
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
  

def main_1():
    file_path1=r'data/1.json'
    file_path2=r'data/120725.json'
    final_reviews1=read_reviews_from_file(file_path1)
    final_reviews2=read_reviews_from_file(file_path2)
    
    final_reviews=final_reviews1+'\t'+final_reviews2
    
    tfidf = TfidfVectorizer().fit_transform(final_reviews.split('\t'))
    
    cosine_similarities = linear_kernel(tfidf[0:1], tfidf).flatten()
    
    print cosine_similarities

def read_keywords_from_reviews(file_path):
    with open(file_path) as data_file:
        data=json.load(data_file)
    reviews=data['reviews']
    final_keywords=[]
    for i in range(25):
         response_entities=alchemyapi.entities("text",reviews[i]['body'])  
         entities=[]
         
         for ety in response_entities['entities']:
             entities.append(ety['text'])
    
         response_keywords=alchemyapi.keywords("text",reviews[i]['body'])
         if response_keywords['language']=='english':
             keywords=[]
         for kw in response_keywords['keywords']:
             keywords.append(kw['text'])
             
         final_keywords+=list(set(keywords) - set(entities))
         
         final_keywords1=""
         
         for s in final_keywords:
            final_keywords1+=s+' '
    
    return final_keywords1
   

def read_reviews_from_file(file_path):
    with open(file_path) as data_file:
        data=json.load(data_file)
    reviews=data['reviews']
    final_reviews=""
    for i in range(25):
        final_reviews+=reviews[i]['body']
    return final_reviews

main_2()