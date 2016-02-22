import sys
import codecs
import os.path
from multiprocessing import Pool
import numpy as np
import json
import pymongo

from tf_idf import *

os.environ['HTTP_PROXY'] = "http://kuzh.polytechnique.fr:8080"
os.environ['HTTPS_PROXY'] = "http://kuzh.polytechnique.fr:8080"

def save_vocabulary(db, nb_doc_to_extract):
    """given a list of book ids
    check if it is already processed
    if not, extract keywords by Alchemy 
    and save keywords to a file
    """
    cursor = db.books.find(no_cursor_timeout=True)
    nb = 0
    docs = []
    for doc in cursors:
        if nb >= nb_doc_to_extract:
            break
        if doc.has_key('keywords'):
            continue
        docs.extend(doc)
        nb += 1

    for doc in docs:
        _, _, vocabulary = get_review_keywords(db, doc['_id'], concat_to_extract = False)
        if len(vocabulary):
            nb += 1
            result = db.books.update_one(
                    {'_id': str(doc['_id'])}, 
                    {
                        "$set":{
                            'keywords': vocabulary
                            }
                    }
            )
            print doc['_id'] + ' updated'

if __name__ == '__main__':
    random = True
    client = pymongo.MongoClient()
    if random:
        nb_doc_to_extract = 100
        save_vocabulary(client.app, nb_doc_to_extract)
