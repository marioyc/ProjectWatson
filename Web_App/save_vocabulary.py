import sys
import codecs
import os.path
from multiprocessing import Pool
import numpy as np
import json
import pymongo

from tf_idf import *


def save_vocabulary(db, nb_id_to_extract):
    """extract key words of nb_id_to_extract documents
    only documents not proceeded before count
    results are written to data base
    we add a field 'keywords' to documents in books collections which contains keywords (broken into single words) of every book
    later when we want to calculate the tf-idf matrix
    we only have to visit all documents with this field
    """
    # get a cursor that goes through books collection
    cursor = db.keywords.find()

    # in order to prevent cursor stays a very long time alive
    # we select in advance the documents to explore
    # and store them in docs
    # every entry of docs is a dictionary
    nb = 0
    docs = []
    for doc in cursor:
        if nb >= nb_id_to_extract:
            break
        docs.append(doc['keywords'])
        nb += 1

    # loop over documents, extract keywords one by one
    # can be optimized by not calling get_review_keywords function
    for doc in docs:
        _, _, vocabulary = extract_keywords_each(db, doc['_id'], concat_to_extract = False)
        # if keywords extracted, update corresponding documents
        if len(vocabulary):
            result = db.books.update_one(
                    {'_id': str(doc['_id'])},
                    {
                        "$set":{
                            'keywords': vocabulary
                            }
                    }
            )
            print doc['_id'] + ' updated'

# executable only if called explicitly
if __name__ == '__main__':
    # initialize an instance
    client = pymongo.MongoClient()
    # number of documents to be proceeded
    nb_doc_to_extract = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    # save vocabulary to database
    save_vocabulary(client.app, nb_doc_to_extract)
