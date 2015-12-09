#!/bin/bash
start=${1}
end=${2}
interval=$(seq $1 $2 | shuf)
succ=0
skip=0
for i in $interval
do
    if [ -f 'data/'$i'.json' ]
    then
        echo 'local data exists, skip'
        skip=$((skip + 1))
        continue
    fi
    echo 'processing book No.'$i
    python2 goodreads_books_api.py $i 99
    succ=$((succ + 1))
done
echo $succ' succes'$skip' skip'
