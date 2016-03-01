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
        if ( not "." in word):
            l.append(re.sub(ur"[^\w\d'\s]+",'',word))
    return l
    
if __name__ == '__main__':
    print process_kw("Kewyword.s anglasids Harry's pottter*****, I really loved your movie")
