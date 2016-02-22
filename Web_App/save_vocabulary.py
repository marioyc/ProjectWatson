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

def save_vocabulary(db, ids):
    """given a list of book ids
    check if it is already processed
    if not, extract keywords by Alchemy 
    and save keywords to a file
    """
    for id in ids:
        _, _, vocabulary = get_review_keywords(db, id, concat_to_extract = False)
        for word in vocabulary:
            if db.vocabulary.find_one({'_id': word}) is None:
                db.vocabulary.insert_one({'_id': word})


if __name__ == '__main__':
    client = pymongo.MongoClient()
    ids = range(403, 404)
    save_vocabulary(client.app, ids)