import goodreads_books_api
from random import shuffle
import os.path
import time
import json
import sys

start = int(sys.argv[1])
end = int(sys.argv[2])
interval = range(start, end)
shuffle(interval)
skipped = 0
successed = 0
for i in interval:
    if os.path.exists('data/' + str(i) + '.json'):
        print 'local data exists, skip'
        skipped += 1
        continue
    print 'processing book No. ' + str(i)
    time.sleep(1)
    info = goodreads_books_api.get_information(i, 99)
    if info is None:
        print 'book not found on GoodReads'
        skipped += 1
        continue
    successed += 1
    with open('data/' + str(i) + '.json', 'w') as outfile:
        json.dump(info, outfile)
print 'job finished...' + str(successed) + 'successed, ' + str(skipped) + 'skipped.'
