# -*- coding: utf-8 -*-
from bson.code import Code
from pymongo import MongoClient
import scipy.sparse as sps
import numpy as np
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import normalize


def fetch_all(db):
    '''First we fetch all the possible shelves from all the books in the database
    db=database to fetch from
    returns a json object of distinct shelves'''
    
    #Using map reduce - for each unique shelf its number of occurences is counted
    #The map method
    map_f=Code("function() { for (var key in this.shelves) { emit(key, 1); }}")
    #The reduce method
    reduce_f=Code("function(key, stuff) { return Array.sum(stuff) }")
    
    #Fetching the results
    shelves = db.books.map_reduce(map_f,reduce_f,"my results")
    
    #Filtering only the shelves that contain letters and a hyphen (but not at the beginning
    #of the string) and that appear at least 2 times
    shelves=shelves.find({'_id': {'$regex':'^[A-Za-z][A-Za-z\-]+$'},'value':{'$gt':1}})
    
    shelves_dict=dict()
    
    #Adding all the shelves to the dictionary
    #In order to be able to query efficiently the column index of each shelf
    #shelves_dict[s]=column index of shelf s in the sparse matrix
    i=0
    for s in shelves:
        shelves_dict[s['_id']]=i
        i=i+1

    return shelves_dict
  
def create_sparse(db,shelves_dict):
    '''Creates the sparse representation of the matrix
    of the shelves tags of each book''' 
    nrows=2000 #Combien de livres on veut manipuler; a present seulement 2000
    ncols=len(shelves_dict)
    
    #r,c=the row and column indexes of the sparse data
    #data[k]=number of persons having tagged the shelf c[k] for the book r[k]
    r, c, data=[],[],[]
    
    r_index=0
    #Iterating through the (shelf,nb of tags for shelf) pairs of each book
    for doc in db.books.find({'keywords': {'$exists': True}}):
        #Adding the sparse data corresponding to the current book
        for key,value in doc['shelves'].iteritems():
            c_index=shelves_dict.get(key,None)
            if c_index is not None:
                r.append(r_index)
                c.append(int(c_index))
                data.append(int(value)) 
        r_index+=1
        
    #Transforming the data into arrays
    data=np.array(data)
    r=np.array(r)
    c=np.array(c)
    
    #Reading it efficiently into a sparse matrix
    mat_coo= sps.coo_matrix((data, (r, c)),dtype=np.double,shape=(nrows,ncols))
    
    #Converting it to a format that is optimized for computations
    mat_csr=sps.csr_matrix(mat_coo)
    mat_norm=normalize(mat_csr, norm='l2', axis=1)
    '''print 'row 0',mat_norm.getrow(0)
    print 'row 1',mat_norm.getrow(1)'''
    return linear_kernel(mat_norm)


def generate_matr_shelves(db):
    '''Uses the two previous functions to generate the pairwise
    similarity matrix of the books'''
    shelves_dict=fetch_all(db)
    matr_s=create_sparse(db,shelves_dict)
    return matr_s
    
# executable only if called explicitly
if __name__ == '__main__':
    client = MongoClient()
    db=client.app
    shelves_dict=fetch_all(db)
    matr_s=create_sparse(db,shelves_dict)
    print matr_s