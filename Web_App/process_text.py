# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 20:52:37 2016

@author: Anca
"""

import re

#Processes a keyword by: splitting it into unique words,
#Removing the proper nouns (too particular to a given book),
#And the punctuation except for the apostrophe
def process_kw(kw):
    keywords=kw.split()
    l=[]
    for word in keywords:
        if ( word.islower() and (not "." in word)):
            l.append(re.sub(ur"[^\w\d'\s]+",'',word))
    return l
    
#Changing the text of a review by removing all punctuation 
#except for the apostrophe and turning everything into lower cases
def process_r(review):
    return re.sub(ur"[^\w\d'\s]+",'',review).lower()
    

#print process_r("Kewyword.s anglasids Harry's pottter*****, I really loved your wife")