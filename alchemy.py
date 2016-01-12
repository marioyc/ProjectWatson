# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 10:59:22 2015

@author: Anca
"""


from alchemyapi import AlchemyAPI
import json
import os


alchemyapi = AlchemyAPI()

with open('data/1.json') as data1_file:    
    data1 = json.load(data1_file)
    
with open('data/77366.json') as data2_file:
    data2 = json.load(data2_file)

os.environ['HTTP_PROXY']="http://kuzh.polytechnique.fr:8080"
os.environ['HTTPS_PROXY']="http://kuzh.polytechnique.fr:8080"
#os.environ['NO_PROXY'] = '127.0.0.1,localhost'

#proxies = {'http': 'http://kuzh.polytechnique.fr:8080',
#            'https': 'http://kuzh.polytechnique.fr:8080'}

reviews1=data1['reviews']

reviews2=data2['reviews']

print data1['similar_books']

final_keywords=[]

for i in range(1):
    response_entities=alchemyapi.entities("text",reviews2[i]['body'])  
    entities=[]
    #print response_entities
    for ety in response_entities['entities']:
        entities.append(ety['text'])
       # print entities
    
    response_keywords=alchemyapi.keywords("text",reviews2[i]['body'])
    if response_keywords['language']=='english':
        keywords=[]
        for kw in response_keywords['keywords']:
            keywords.append(kw['text'])
           # print keywords
        final_keywords+=(list(set(keywords) - set(entities)))
        
print final_keywords

with open(r'D:\Laptop vechi\Desktop laptop vechi\Cursuri Polytechnique\Info\Projet 3A\output\output3.txt',"a") as thefile:
    for item in final_keywords:
        thefile.write("%s \n " % item.encode('utf8'))

#keywords=list(set(keywords) - set(entities))
#print "Final unique keywords:", final_keywords
#remarque: les mots sont assez pertinents mais il faudrait enlever les noms 
#propres

    

