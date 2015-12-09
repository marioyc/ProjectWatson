"""given the isbn of a book
fetch basic information including publisher, author(s), description, reviews, etc
example using isbn
soup = fetch()
info = get_information('9781476705583', 20)
print info
example using GoodReads id
info = get_information('1', 20)
print info
"""

import requests
from requests.adapters import HTTPAdapter
import Queue
import threading
import sys
import json
import re
from bs4 import BeautifulSoup

s = requests.Session()
s.mount('https://', HTTPAdapter(max_retries = 5))
queue = Queue.Queue()
out_queue = Queue.Queue()
reviews = []

def get_information(number, nb_reviews_limit = None):
    """get and return basic information of a book
    given its isbn number or good reads id
    """
    soup = fetch(number)
    info = get_information_from_soup(soup, nb_reviews_limit)
    return info

def fetch(number):
    """fetch raw data of a given isbn or GoodReads id
    return a BeautifulSoup object
    """
    proxies = {'http': 'http://kuzh.polytechnique.fr:8080',
            'https': 'http://kuzh.polytechnique.fr:8080'}
    key = 'C29sMtUMNv1TXwvnvKjw'
    number = str(number)
    if len(number) == 10 or len(number) == 13:
        url = 'https://www.goodreads.com/book/isbn?isbn=' + number + '&key='+ key
    else:
        url = 'https://www.goodreads.com/book/show/' + number + '?format=xml&key=' + key

    r = s.get(url, proxies = proxies, verify = False)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'xml')
    return soup

def get_information_from_soup(soup, nb_reviews_limit = None):
    """get useful information from a BeautifulSoup object
    return a dictionary
    """
    info = {}
    if soup.id is None:
        return
    info['id'] = int(soup.id.string)
    info['isbn13'] = int(soup.isbn13.string) if isValid(soup.isbn13) else '0'
    info['title'] = soup.title.string.strip()
    info['image_url'] = soup.image_url.string.strip() if isValid(soup.image_url) else ''
    info['publisher'] = soup.publisher.string.strip() if isValid(soup.publisher) else ''
    info['publication_date'] = ''
    if isValid(soup.publication_year):
        info['publication_date'] = soup.publication_year.string.strip()
        info['publication_date'] +=  '-' + soup.publication_month.string.strip().zfill(2) if isValid(soup.publication_month) else '-01'
        info['publication_date'] +=  '-' + soup.publication_day.string.strip().zfill(2) if isValid(soup.publication_day) else '-01'
    info['description'] = remove_html_tags(soup.description.string.strip()) if isValid(soup.description) else ''
    info['authors'] = get_information_authors(soup.authors) if isValid(soup.authors) else [] 
    info['avg_rating'] = float(soup.average_rating.string) if isValid(soup.average_rating) else -1
    info['num_pages'] = int(soup.num_pages.string) if isValid(soup.num_pages) else -1 
    info['shelves'] = get_information_popular_shelves(soup.popular_shelves) if soup.popular_shelves is not None else []
    info['reviews'] = get_information_reviews_multi(soup.reviews_widget, nb_reviews_limit) if isValid(soup.reviews_widget) else []
    return info

def get_information_authors(authors):
    """get authors information from a BeautifulSoup tag object
    since a book may have more than one author
    return a list of dictionaries
    """
    print 'fetching author(s) information...'
    authors_clean = [author for author in authors.contents if author != '\n']
    infos = []
    for author in authors_clean:
        info = {}
        info['id'] = int(author.find('id').string)
        info['name'] = author.find('name').string.strip() if isValid(author.find('name')) else ''
        info['avg_rating'] = float(author.find('average_rating').string.strip()) if isValid(author.find('average_rating')) else -1
        info['image_url'] = author.find('image_url').string.strip() if isValid(author.find('image_url')) else ''
        infos.append(info)
    return infos

def get_information_popular_shelves(shelves):
    """return popular shelves information from a BeautifulSoup tag object
    """
    print 'fetching popular shelves information...'
    shelves_clean = [shelf for shelf in shelves.contents if shelf != '\n']
    infos = {}
    for shelf in shelves_clean:
        infos[shelf['name']] = int(shelf['count'])
    return infos

def get_information_reviews_single(widget, nb_reviews_limit = None):
    """return reviews of a book
    givien a widget returned by GoodReads API
    if nb_reviews_limit is specified, only first nb_reviews_limit reviews will be returned
    if not, all (MANY!!) reviews will be returned
    """
    proxies = {'http': 'http://kuzh.polytechnique.fr:8080',
            'https': 'http://kuzh.polytechnique.fr:8080'}
    soup = BeautifulSoup(widget.text, 'lxml')
    url_page = soup.body.find('iframe', id = 'the_iframe')['src']
    nb_reviews = 0
    reviews = []
    while url_page is not None:
        r_page = requests.get(url_page, proxies = proxies, verify = False)
        r_page.raise_for_status()
        soup_page = BeautifulSoup(r_page.text, 'lxml')
        links = soup_page.body.find_all(lambda tag: tag.name == 'a' and tag.has_attr('href') and tag.has_attr('itemprop'))
        for link_raw in links:
            print 'fetching review No.' + str(nb_reviews) + '...'
            review = {}
            link_review = link_raw['href'].strip()
            r_review = requests.get(link_review, proxies = proxies, verify = False)
            soup_review = BeautifulSoup(r_review.text, 'lxml')
            review['body'] = soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewBody').text.strip() if isValid(soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewBody')) else ''
            review['date'] = soup_review.find('span', 'value-title', title = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}'))['title'] if soup_review.find('span', 'value-title', title = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')) is not None else ''
            review['rating'] = int(soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewRating').text.strip().split()[0]) if isValid(soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewRating')) else -1
            review['likes'] = int(soup_review.find('span', 'likesCount').text.strip().split()[0]) if isValid(soup_review.find('span', 'likesCount')) else -1
            reviews.append(review)
            nb_reviews += 1
            if nb_reviews_limit and nb_reviews >= nb_reviews_limit:
                return reviews
        url_page = 'https://www.goodreads.com' + soup_page.body.find('a', 'next_page', rel='next')['href'] if soup_page.body.find('a', 'next_page', rel='next') is not None else None
    return reviews
def get_information_reviews_multi(widget, nb_reviews_limit = None):
    """return reviews of a book
    givien a widget returned by GoodReads API
    if nb_reviews_limit is specified, only first nb_reviews_limit reviews will be returned
    if not, all (MANY!!) reviews will be returned
    """
    proxies = {'http': 'http://kuzh.polytechnique.fr:8080',
            'https': 'http://kuzh.polytechnique.fr:8080'}
    soup = BeautifulSoup(widget.text, 'lxml')
    url_page = soup.body.find('iframe', id = 'the_iframe')['src']
    nb_reviews = 0
    url_reviews = []
    flag = False
    while url_page is not None:
        r_page = s.get(url_page, proxies = proxies, verify = False)
        r_page.raise_for_status()
        soup_page = BeautifulSoup(r_page.text, 'lxml')
        links = soup_page.body.find_all(lambda tag: tag.name == 'a' and tag.has_attr('href') and tag.has_attr('itemprop'))
        for link_raw in links:
            url_reviews.append(link_raw['href'])
            nb_reviews += 1
            if nb_reviews_limit and nb_reviews >= nb_reviews_limit:
                flag = True 
                break
        if flag:
            break
        url_page = 'https://www.goodreads.com' + soup_page.body.find('a', 'next_page', rel='next')['href'] if soup_page.body.find('a', 'next_page', rel='next') is not None else None
    print 'fetching reviews...'
    reviews = fetch_reviews_multi_threading(url_reviews)
    return reviews

def remove_html_tags(string):
    """delete annoying html tags in the description of a book
    using a regex
    """
    return re.sub('<[^[]+?>', '', string) 

def isValid(tag):
    return tag is not None and tag.text.strip()

class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue, out_queue1):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue

    def run(self):
        while True:
            #grabs host from queue
            proxies = {'http': 'http://kuzh.polytechnique.fr:8080',
            'https': 'http://kuzh.polytechnique.fr:8080'}
            host = self.queue.get()
            
            #grabs urls of hosts and then grabs chunk of webpage

            #place chunk into out queue
            self.out_queue.put(s.get(host, proxies = proxies, verify = False))

            #signals to queue job is done
            self.queue.task_done()

class DatamineThread(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, out_queue):
        threading.Thread.__init__(self)
        self.out_queue = out_queue

    def run(self):
        while True:
            #grabs host from queue
            raw = self.out_queue.get()
            #parse the raw
            soup_review = BeautifulSoup(raw.text, 'lxml')
            review = {}
            review['body'] = soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewBody').text.strip() if isValid(soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewBody')) else ''
            review['date'] = soup_review.find('span', 'value-title', title = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}'))['title'] if soup_review.find('span', 'value-title', title = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')) is not None else ''
            review['rating'] = int(soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewRating').text.strip().split()[0]) if isValid(soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewRating')) else -1
            review['likes'] = int(soup_review.find('span', 'likesCount').text.strip().split()[0]) if isValid(soup_review.find('span', 'likesCount')) else -1
            reviews.append(review)
            #signals to queue job is done
            self.out_queue.task_done()

def fetch_reviews_multi_threading(links_clean):

    #spawn a pool of threads, and pass them queue instance
    for i in range(4):
        t = ThreadUrl(queue, out_queue)
        t.setDaemon(True)
        t.start()

    #populate queue with data
    for link in links_clean:
        queue.put(link)

    for i in range(4):
        dt = DatamineThread(out_queue)
        dt.setDaemon(True)
        dt.start()

    #wait on the queue until everything has been processed
    queue.join()
    out_queue.join()
    with queue.mutex:
        queue.queue.clear
    with out_queue.mutex:
        out_queue.queue.clear
    return reviews
number = int(sys.argv[1])
limit = int(sys.argv[2])
info = get_information(number, limit)
if not info:
    print 'book not found on GoodReads'
else:
    with open('data/' + str(number) + '.json', 'w') as outfile:
        json.dump(info, outfile)
print 'done'
s.close()
