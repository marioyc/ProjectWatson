# -*- coding: utf-8 -*-
from bson.code import Code
from pymongo import MongoClient
import scipy.sparse as sps
import numpy as np
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import normalize

'''First we fetch all the possible shelves from all the books in the database
db=database to fetch from
returns a list of unique tags'''
def fetch_all(db):
    #The map method
    map_f=Code("function() { for (var key in this.shelves) { emit(key, null); }}")
    #The reduce method
    reduce_f=Code("function(key, stuff) { return null; }")
    
    #Fetching the results
    shelves = db.books.map_reduce(map_f,reduce_f,"my results")
    
    #Filtering only those that contain letters and a hyphen (but not at the beginning
    #of the string)
    shelves=shelves.find({'_id': {'$regex':'^[A-Za-z\-]+$'}})
    
    shelves_dict=dict()
    
    i=0
    for s in shelves:
        shelves_dict[s['_id']]=i
        i=i+1
        
#    print shelves_dict
    
    print len(shelves_dict)
    
    return shelves_dict

'''Creates the sparse representation of the matrix
of shelves tags of each book'''   
def create_sparse(db,shelves_dict):
    nrows=db.tf_idf.find().count()
    ncols=len(shelves_dict)
    print nrows,ncols
    r, c, data=[],[],[]
    r_index=0
    for doc in db.books.find().limit(nrows):
        for key,value in doc['shelves'].iteritems():
            #print key,value
            c_index=shelves_dict.get(key,None)
            if c_index is not None:
                r.append(int(r_index))
                c.append(int(c_index))
                data.append(int(value) ) 
        r_index+=1
    data=np.array(data)
    r=np.array(r)
    c=np.array(c)
    mat= sps.coo_matrix((data, (r, c)),dtype=np.double, shape=(nrows, ncols))
    mat=sps.csr_matrix(mat)
    matar=mat.toarray()
    matarn=normalize(matar, norm='l2', axis=1)
    print linear_kernel(matarn)
    
# executable only if called explicitly
if __name__ == '__main__':
    client = MongoClient()
    db=client.app
    shelves_dict=fetch_all(db)
    create_sparse(db,shelves_dict)