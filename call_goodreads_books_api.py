import goodreads_books_api
import json
import sys

start = int(sys.argv[1])
end = int(sys.argv[2])
for i in range(start, end):
    info = goodreads_books_api.get_information(i, 100)
    with open(str(i) + '.json', 'w') as outfile:
        json.dump(info, outfile)
