import sys
import codecs
import os.path
from multiprocessing import Pool
from functools import partial
import numpy as np
import json

from tf_idf import *

if os.name != 'posix':
    path = 'C:/Users/Anca/Documents/GitHub/ProjectWatson/data/'
else:
    path = './data/'

filetype = '.json'

def save_vocabulary(ids):
    """given a list of book ids
    check if it is already processed
    if not, extract keywords by Alchemy 
    and save keywords to a file
    """
    # set of ids already treated
    # corresponding id.json may not existe
    # this just means that we have "checked" it
    processed = set()
    if os.path.isfile(path + 'processed.txt'):
        f = open(path + 'processed.txt')
        for line in f:
            processed.add(int(line.strip()))
        f.close()
    # filter all ids already processed
    ids = filter(lambda x: x not in processed, ids)

    print ids
    #complete filenames and call function build_corpus to extract vocabulary
    filenames = map(lambda x: path + str(x) + filetype, ids)
    print filenames
    _, _, vocabulary = build_corpus(filenames)
    print vocabulary

    
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
    f1 = open(path + 'processed.txt', 'a')
    f2 = codecs.open(path + 'vocabulary.txt', 'a', 'utf-8')
    map(lambda x: f1.write(str(x) + '\n'), ids)
    map(lambda x: f2.write(x + '\n'), vocabulary)
    f1.close()
    f2.close()

def row_to_dict(tf_idf, ids, index):
    """convert the index_th row of tf_idf matrix to dictionary
    """
    row = {}
    row['id'] = ids[index]
    # an empty table to store similarities with other books
    col = []
    ids_sort = tf_idf[index, :].argsort()[::-1][1:11]
    for i in ids_sort:
        entry = {'id': ids[i], 'value': tf_idf[index][i]}
        col.append(entry)
    row['value'] = col
    return row
        
def write_tf_idf(tf_idf, ids):
    """write tf_idf matrix to a json file
    """
    assert tf_idf.shape[0] == len(ids)
    """
    # use multiprocessing to accelerate
    if __name__ == '__main__':
        pool = Pool(8)
        res = pool.map(partial(row_to_dict, tf_idf, ids), range(len(ids)))
        pool.close()
    with open(path + 'tf_idf.json', 'w') as f:
        json.dump(res, f)
    """
    res = map(partial(row_to_dict, tf_idf, ids), range(len(ids)))
    with open(path + 'tf_idf.json', 'w') as f:
        json.dump(res, f)


def load_tf_idf():
    """load tf_idf matrix from file
    """
    f = open(path + 'tf_idf.json', 'r')
    res = json.load(f)
    return res
"""
def main():
    #ids = range(20)
    #save_vocabulary(ids)
    #write_tf_idf(np.ones((len(ids), len(ids))), ids)
    xxx = load_tf_idf()
    print len(xxx)

main()
"""
