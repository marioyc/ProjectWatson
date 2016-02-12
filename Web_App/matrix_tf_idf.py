# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 11:19:32 2016
@author: Ana-Maria, Baoyang
"""
from tf_idf import *
import string
import codecs
import os.path
from query_tf_idf import cos
from functools import partial

def load_tf_idf():
    """load tf_idf matrix from file"""
    f = open(path + 'tf_idf.json', 'r')
    res = json.load(f)
    return res

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

def generate_matrix(path_json, coeff_d, coeff_r, coeff_s):
    #Fetching the ids that have already been processed
    processed_ids = set()
    if os.path.isfile(path_json + 'alchemy_tentative.txt'):
        f = open(path_json + 'alchemy_tentative.txt')
        for line in f:
            processed_ids.add(int(line.strip()))
        f.close()
    #Keeping only those ids that correspond to an existing .json file
    processed_ids = filter(lambda x: os.path.isfile(path_json+str(x)+'.json'), processed_ids)
    
    #keeping only those filenames that exist
    filenames=[path_json+str(x)+'.json' for x in processed_ids]

    #Loading the description and the corpus of reviews
    shelf_vectors,descriptions,reviews,_= build_corpus(filenames, extract_keywords = False, concat_to_extract = False)
    
    #Reading the vocabulary
    vocabulary = set()
    if os.path.isfile(path_json + 'vocabulary.txt'):
        f = codecs.open(path_json + 'vocabulary.txt', 'r', 'utf-8')
        for line in f:
            vocabulary.add(line[:-2].lower().encode('utf-8').translate(None,string.punctuation))
        f.close()
    #Building the vectorizer for reviews
    vectorizer_r=build_tf_idf(reviews,vocabulary)
    matrix_r=vectorizer_r.fit_transform(reviews).toarray()
    dist_r=similarities(matrix_r)
    
    #Building the vectorizer for descriptions
    vectorizer_d=build_tf_idf(descriptions)
    matrix_d=vectorizer_d.fit_transform(descriptions).toarray()
    dist_d=similarities(matrix_d)
    
    #Building the cosine similarity matrix for the shelf vectors
    sv_size = len(shelf_vectors)
    sv=np.zeros((sv_size,sv_size))
    for i in range(sv_size):
        for j in range(sv_size):
            sv[i,j] = cos(shelf_vectors[i],shelf_vectors[j])
            
    print sv_size
    
    coeff_rr=coeff_r/(coeff_r+coeff_d+coeff_s)
    coeff_dd=coeff_d/(coeff_r+coeff_d+coeff_s)
    coeff_ss=coeff_s/(coeff_r+coeff_d+coeff_s)

    print coeff_rr, coeff_dd, coeff_ss
    return processed_ids, coeff_rr*dist_r+coeff_dd*dist_d+coeff_ss*sv

def main():
    proc_ids, dist_r = generate_matrix(path,5.0,2.0,1.0)
    write_tf_idf(dist_r, proc_ids)

main()