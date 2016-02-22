#!/bin/bash
path='static/json/'
extension='json'
filenames=$(find $path -name '*.'$extension)
for filename in $filenames
do
    mongoimport --db midnight --collection books --file ${filename}
done
