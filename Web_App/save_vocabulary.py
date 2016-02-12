import sys
import codecs
import os.path
from multiprocessing import Pool
import numpy as np
import json

from tf_idf import *

if os.name != 'posix':
    path = 'C:/Users/Anca/Documents/GitHub/ProjectWatson/data/'
else:
    path = './data/'

filetype = '.json'

os.environ['HTTP_PROXY']="http://kuzh.polytechnique.fr:8080"
os.environ['HTTPS_PROXY']="http://kuzh.polytechnique.fr:8080"

def save_vocabulary(ids):
    """given a list of book ids
    check if it is already processed
    if not, extract keywords by Alchemy 
    and save keywords to a file
    """
    # set of ids already treated
    # corresponding id.json may not exist
    # this just means that we have "checked" it
    processed = set()
    if os.path.isfile(path + 'alchemy_tentative.txt'):
        f = open(path + 'alchemy_tentative.txt')
        for line in f:
            processed.add(int(line.strip()))
        f.close()
    # filter all ids already processed
    ids = filter(lambda x: x not in processed, ids)

    """
    #complete filenames and call function build_corpus to extract vocabulary
    filenames = map(lambda x: path + str(x) + filetype, ids)
    _, _, _, vocabulary = build_corpus(filenames)

    # load existing vocabulary
    vocabulary_existed = set()
    if os.path.isfile(path + 'vocabulary.txt'):
        f = codecs.open(path + 'vocabulary.txt', 'r', 'utf-8')
        for line in f:
            vocabulary_existed.add(line)
        f.close()
    
    # filter all existing vocabulary from that is just obtained
    vocabulary = filter(lambda x: x not in vocabulary_existed, vocabulary)
    # write to file, update
    f1 = open(path + 'alchemy_tentative.txt', 'a')
    f2 = codecs.open(path + 'vocabulary.txt', 'a', 'utf-8')
    map(lambda x: f1.write(str(x) + '\n'), ids)
    map(lambda x: f2.write(x + '\n'), vocabulary)
    f1.close()
    f2.close()
    """
    for id in ids:
        filename = path + str(id) + filetype
        _, _, _, vocabulary = get_review_keywords(filename, concat_to_extract=False)
        # load existing vocabulary
        vocabulary_existed = set()
        if os.path.isfile(path + 'vocabulary.txt'):
            f = codecs.open(path + 'vocabulary.txt', 'r', 'utf-8')
            for line in f:
                vocabulary_existed.add(line)
            f.close()
        # filter all existing vocabulary from that is just obtained
        vocabulary = filter(lambda x: x not in vocabulary_existed, vocabulary)
        vocabulary = list(set(vocabulary))
        # write to file, update
        f1 = open(path + 'alchemy_tentative.txt', 'a')
        f2 = codecs.open(path + 'vocabulary.txt', 'a', 'utf-8')
        f1.write(str(id) + '\n')
        map(lambda x: f2.write(x + '\n'), vocabulary)
        f1.close()
        f2.close()
"""
def main():
    ids = range(403, 404)
    save_vocabulary(ids)
    #write_tf_idf(np.ones((len(ids), len(ids))), ids)

main()
"""