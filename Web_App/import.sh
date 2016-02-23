#!/bin/bash
# import single json file to MongoDB
path='static/json/'
extension='json'
filenames=$(find $path -name '*.'$extension)
for filename in $filenames
do
    mongoimport --db app --collection books --file ${filename}
done
