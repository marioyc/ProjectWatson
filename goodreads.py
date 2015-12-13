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
import json
import re
import sys
from math import ceil
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
from itertools import chain
import os.path
import time

def get_information(number, nb_reviews_limit = None):
    """get and return basic information of a book
    given its isbn number or good reads id
    """
    time.sleep(1)
    print 'processing book No. ' + str(number) + '...'
    soup = fetch(number)
    info = get_information_from_soup(soup, nb_reviews_limit)
    if info:
        with open('data/' + info['id'] + '.json', 'w') as outfile:
            json.dump(info, outfile)

def fetch(number):
    """fetch raw data of a given isbn or GoodReads id
    return a BeautifulSoup object
    """
    s = requests.Session()
    s.mount('https://', HTTPAdapter(max_retries = 5))
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
    s.close()
    return soup

def get_information_from_soup(soup, nb_reviews_limit = None):
    """get useful information from a BeautifulSoup object
    return a dictionary
    """
    info = {}
    if soup.id is None:
        return
    print 'fetching basic information...'
    text_reviews_count = int(soup.text_reviews_count.string)
    nb_reviews_limit = text_reviews_count if nb_reviews_limit is None or nb_reviews_limit > text_reviews_count else nb_reviews_limit
    info['id'] = soup.id.string
    info['isbn'] = soup.isbn.string if soup.isbn else ''
    info['isbn13'] = soup.isbn13.string if soup.isbn13 else ''
    info['title'] = soup.title.string
    info['image_url'] = soup.image_url.string if soup.image_url else ''
    info['publisher'] = soup.publisher.string if soup.publisher else ''
    info['publication_year'] = soup.publication_year.string if soup.publication_year.string else ''
    info['publication_month'] = soup.publication_month.string if soup.publication_month.string else ''
    info['publication_day'] = soup.publication_day.string if soup.publication_day.string else ''
    info['description'] = remove_html_tags(soup.description.string) if soup.description else ''
    authors = get_information_authors(soup.authors) if soup.authors else []
    info['authors'] = [author for author in authors]
    info['avg_rating'] = soup.average_rating.string if soup.average_rating else ''
    info['num_pages'] = soup.num_pages.string if soup.num_pages else ''
    info['shelves'] = get_information_popular_shelves(soup.popular_shelves) if soup.popular_shelves else []
    info['reviews'] = get_reviews(soup.reviews_widget, nb_reviews_limit) if soup.reviews_widget else []
    similar_books_raw = soup.similar_books.find_all('id') if soup.similar_books else []
    info['similar_books'] = [int(id_raw.string) for id_raw in similar_books_raw]
    old.extend(info['similar_books'])
    return info

def get_information_authors(authors):
    """get authors information from a BeautifulSoup tag object
    since a book may have more than one author
    return a list of dictionaries
    """
    print 'fetching author(s) information...'
    authors_clean = [author for author in authors.contents if author != '\n']
    for author in authors_clean:
        info = {}
        info['id'] = author.find('id').string
        info['name'] = author.find('name').string if author.find('name') else ''
        info['avg_rating'] = author.find('average_rating').string if author.find('average_rating') else ''
        info['image_url'] = author.find('image_url').string if author.find('image_url') else ''
        yield info

def get_information_popular_shelves(shelves):
    """return popular shelves information from a BeautifulSoup tag object
    """
    print 'fetching popular shelves information...'
    shelves_clean = [shelf for shelf in shelves.contents if shelf != '\n']
    infos = {}
    for shelf in shelves_clean:
        infos[shelf['name']] = shelf['count']
    return infos

def get_review_single(url):
    s = requests.Session()
    s.mount('https://', HTTPAdapter(max_retries = 5))
    proxies = {'http': 'http://kuzh.polytechnique.fr:8080',
            'https': 'http://kuzh.polytechnique.fr:8080'}
    review = {}
    r_review = s.get(url, proxies = proxies, verify = False)
    soup_review = BeautifulSoup(r_review.text, 'lxml')
    review['body'] = soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewBody').text.strip() if isValid(soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewBody')) else ''
    review['date'] = soup_review.find('span', 'value-title', title = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}'))['title'] if soup_review.find('span', 'value-title', title = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')) is not None else ''
    review['rating'] = soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewRating').text.strip().split()[0] if isValid(soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewRating')) else ''
    review['likes'] = soup_review.find('span', 'likesCount').text.strip().split()[0] if isValid(soup_review.find('span', 'likesCount')) else ''
    s.close()
    return review

def get_reviews_url(url_page):
    proxies = {'http': 'http://kuzh.polytechnique.fr:8080',
            'https': 'http://kuzh.polytechnique.fr:8080'}
    s = requests.Session()
    s.mount('https://', HTTPAdapter(max_retries = 5))
    r_page = s.get(url_page, proxies = proxies, verify = False)
    r_page.raise_for_status()
    soup_page = BeautifulSoup(r_page.text, 'lxml')
    links_raw = soup_page.body.find_all(lambda tag: tag.name == 'a' and tag.has_attr('href') and tag.has_attr('itemprop'))
    links = map(lambda x: x['href'], links_raw)
    s.close()
    return links

def get_reviews(widget, nb_reviews_limit):
    print "fetching users' reviews..."
    soup = BeautifulSoup(widget.text, 'lxml')
    url_basic = soup.body.find('iframe', id = 'the_iframe')['src']
    nb_pages = int(ceil(nb_reviews_limit / 9.0))
    urls = [re.sub('min_rating=&', 'min_rating=&page=' + str(i) + '&', url_basic) for i in range(1, nb_pages+1)]
    pool_reviews = ThreadPool(nb_pages)
    reviews_url = list(chain.from_iterable(pool_reviews.map(get_reviews_url, urls)))[:nb_reviews_limit]
    pool_reviews.close()
    pool_reviews.join()
    pool_reviews = ThreadPool(nb_pages)
    reviews = pool_reviews.map(get_review_single, reviews_url)
    pool_reviews.close()
    pool_reviews.join()
    return reviews

def remove_html_tags(string):
    """delete annoying html tags in the description of a book
    using a regex
    """
    return re.sub('<[^[]+?>', '', string) if string else ''

def isValid(tag):
    return tag is not None and tag.text.strip()

assert len(sys.argv) > 2
start_id = int(sys.argv[1])
end_id = int(sys.argv[2])
max_depth = int(sys.argv[3]) if len(sys.argv) > 3 else 1
max_nb_reviews = int(sys.argv[4]) if len(sys.argv) > 4 else 99
pool = ThreadPool()
old = range(start_id, end_id)
new = []
depth = 0
while len(old) > 0 and depth < max_depth+1:
    new = filter(lambda x: not os.path.isfile('data/' + str(x) + '.json'), old)
    old[:] = []
    pool.map(lambda x: get_information(x, 99), new)
    depth += 1
pool.close()
pool.join()