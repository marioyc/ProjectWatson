import json
import goodreads_books_api
number = '1'
info = goodreads_books_api.get_information(number, 20)
with open(str(number) + '.json', 'w') as outfile:
    json.dump(info, outfile)
