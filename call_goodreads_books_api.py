import goodreads_books_api
from random import shuffle
import os.path
import json
import sys

start = int(sys.argv[1])
end = int(sys.argv[2])
interval = range(start, end)
shuffle(interval)

for i in interval:
    if os.path.exists(str(i) + '.json'):
        continue
    print 'Processing book No. ' + str(i)
    info = goodreads_books_api.get_information(i, 100)
    if info is None:
        print 'Attention: book not found on GoodReads'
        continue
    with open(str(i) + '.json', 'w') as outfile:
        json.dump(info, outfile)
