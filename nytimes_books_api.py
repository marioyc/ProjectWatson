import json
import urllib2

books_api_key = "56cbffa8d95785ef06c310c4251c187a:11:73514871"

def best_sellers(list_name):
    url = "http://api.nytimes.com/svc/books/v3/lists/" + list_name + "?api-key=" + books_api_key
    print "url :", url
    return json.load(urllib2.urlopen(url))

def best_sellers_history(isbn=None, author=None, publisher=None, title=None):
    url = "http://api.nytimes.com/svc/books/v3/lists/best-sellers/history?"
    url += "api-key=" + books_api_key
    if isbn is not None:
        url += "&isbn=" + isbn
    if publisher is not None:
        url += "&publisher=" + publisher
    if author is not None:
        url += "&author=" + author
    if title is not None:
        url += "&title=" + title
    print "url : ", url
    return json.load(urllib2.urlopen(url))

print json.dumps(best_sellers("manga"), indent=4, separators=(',', ': '))

print json.dumps(best_sellers_history("9781421585659"), indent=4, separators=(',', ': '))

print json.dumps(best_sellers_history(None, "ONE", "VIZ"), indent=4, separators=(',', ': '))
