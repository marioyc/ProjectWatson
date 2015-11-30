import json
import urllib2

books_api_key = "56cbffa8d95785ef06c310c4251c187a:11:73514871"

def best_sellers(list_name):
    url = "http://api.nytimes.com/svc/books/v3/lists/" + list_name + "?api-key=" + books_api_key
    print "url :", url
    return json.load(urllib2.urlopen(url))

print json.dumps(best_sellers("manga"), indent=4, separators=(',', ': '))
