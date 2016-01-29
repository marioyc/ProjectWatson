import re
import sys
import json
import time
import os
import platform
import requests
from math import ceil
from bs4 import BeautifulSoup
from itertools import chain
from requests.adapters import HTTPAdapter
from multiprocessing.dummy import Pool as ThreadPool

if re.search('.polytechnique.fr', platform.node()):
    from langid import LanguageIdentifier, model
else:
    from langid.langid import LanguageIdentifier, model

def in_english(text, threshold = 0.5):
    """determine if a given text is in English
    with a given probability
    """
    if text is None:
        return False
    identifier = LanguageIdentifier.from_modelstring(model, norm_probs = True)
    flag = identifier.classify(text)
    return flag[0] == 'en' and flag[1] > threshold

def has_enough_words(text, threshold = 50):
    """determine if a given text has enough words
    """
    if text is None:
        return False
    return len(text.split()) >= threshold

def text_cleaning(string):
    """delete variable undesirable characters using a regex
    """
    if string is None:
        return ''
    # to lower case
    #string = string.lower()
    # remove raw returns
    string = re.sub('\\n', ' ', string)
    # remove html tags
    string = re.sub('<[^<]+?>', ' ', string)
    # remove strings like ["br"]>["br"]>...
    pattern = re.compile('\[\"br\"\]>+', re.IGNORECASE)
    string = pattern.sub(' ', string)
    # remove "spoiler alter"
    pattern = re.compile('^spoiler alert[^\w|\n]+', re.IGNORECASE)
    string = pattern.sub(' ', string)
    pattern = re.compile('[^\w|\n]spoiler alert[^\w|\n]+', re.IGNORECASE)
    string = pattern.sub(' ', string)
    # remove "***"s, "~~~"s
    string = re.sub('\*|~+', ' ', string)
    # return leadning and trailing non-printable characters
    return string.strip()

def is_valid(tag):
    return tag is not None and tag.text.strip()

def get_information(number, depth, max_depth, nb_reviews_limit = None, processed = set()):
    """get and return basic information of a book
    given its isbn number or good reads id
    """
    time.sleep(1)
    number = str(number)
    print 'processing book No. ' + number + '...'

    """get useful information from a BeautifulSoup object
    return a dictionary
    """
    if depth == max_depth - 1 and number in processed:
        return []

    s = requests.Session()
    s.mount('https://', HTTPAdapter(max_retries = 5))
    proxies = {'http': 'http://kuzh.polytechnique.fr:8080',
            'https': 'http://kuzh.polytechnique.fr:8080'}
    key = 'C29sMtUMNv1TXwvnvKjw'
    if len(number) == 10 or len(number) == 13:
        url = 'https://www.goodreads.com/book/isbn?isbn=' + number + '&key='+ key
    else:
        url = 'https://www.goodreads.com/book/show/' + number + '?format=xml&key=' + key
    r = s.get(url, proxies = proxies)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'xml')
    s.close()

    info = {}
    if soup.id is None:
        return []
    text_reviews_count = int(soup.text_reviews_count.string)
    nb_reviews_limit = text_reviews_count if nb_reviews_limit is None or nb_reviews_limit > text_reviews_count else nb_reviews_limit

    similar_books_raw = soup.similar_books.find_all('id') if soup.similar_books is not None else []

    similar_books = [id_raw.string for id_raw in similar_books_raw] if similar_books_raw is not None else []

    if number in processed:
        return similar_books

    processed.add(number)

    print 'fetching basic information...'

    if soup.description is None:
        return similar_books
    description = text_cleaning(soup.description.string)
    if not has_enough_words(description) or not in_english(description):
        return similar_books
    info['description'] = description
    info['reviews'] = get_reviews(soup.reviews_widget, nb_reviews_limit) if nb_reviews_limit else []
    if len(info['reviews']) == 0:
        return similar_books
    info['id'] = soup.id.string
    info['isbn'] = soup.isbn.string if soup.isbn else ''
    info['isbn13'] = soup.isbn13.string if soup.isbn13 else ''
    info['title'] = soup.title.string
    info['image_url'] = soup.image_url.string if soup.image_url else ''
    info['publisher'] = soup.publisher.string if soup.publisher else ''
    info['publication_year'] = soup.publication_year.string if soup.publication_year.string else ''
    info['publication_month'] = soup.publication_month.string if soup.publication_month.string else ''
    info['publication_day'] = soup.publication_day.string if soup.publication_day.string else ''
    authors = get_information_authors(soup.authors) if soup.authors else []
    info['authors'] = [author for author in authors]
    info['avg_rating'] = soup.average_rating.string if soup.average_rating else ''
    info['num_pages'] = soup.num_pages.string if soup.num_pages else ''
    info['shelves'] = get_information_popular_shelves(soup.popular_shelves) if soup.popular_shelves else []
    info['similar_books'] = similar_books

    if info:
        with open('data/' + info['id'] + '.json', 'w') as outfile:
            json.dump(info, outfile)

    return similar_books

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
    r_review = s.get(url, proxies = proxies)
    soup_review = BeautifulSoup(r_review.text, 'lxml')
    body = soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewBody')
    body = body.text if body is not None else ''
    body = text_cleaning(body)
    if not has_enough_words(body):
        return {}
    if not in_english(body):
        return {}
    review['body'] = body
    date = soup_review.find('span', 'value-title', title = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}'))
    review['date'] = date['title'] if date else ''
    rating = soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewRating')
    rating = rating.find('span').get('title') if rating is not None and rating.find('span') is not None else ''
    review['rating'] = rating
    likes = soup_review.find('span', 'likesCount')
    review['likes'] = likes.text.strip().split()[0] if likes and likes.text.strip() else ''
    s.close()
    return review

def get_reviews_url(url_page):
    proxies = {'http': 'http://kuzh.polytechnique.fr:8080',
            'https': 'http://kuzh.polytechnique.fr:8080'}
    s = requests.Session()
    s.mount('https://', HTTPAdapter(max_retries = 5))
    r_page = s.get(url_page, proxies = proxies)
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
    reviews = []
    start = 1
    while True:
        nb_pages = int(ceil((nb_reviews_limit - len(reviews)) / 7.0))
        urls = [re.sub('min_rating=&', 'min_rating=&page=' + str(i) + '&', url_basic) for i in range(start, nb_pages + start)]
        start += nb_pages
        pool_reviews = ThreadPool(4)
        reviews_url = list(chain.from_iterable(pool_reviews.map(get_reviews_url, urls)))
        pool_reviews.close()
        pool_reviews.join()
        reviews_url = set(reviews_url)
        pool_reviews = ThreadPool(4)
        reviews_this = pool_reviews.map(get_review_single, reviews_url)
        pool_reviews.close()
        pool_reviews.join()
        if reviews_this is None:
            break
        reviews_this_non_empty = filter(lambda x: x != {}, reviews_this)
        if len(reviews_this_non_empty) == 0:
            break
        reviews.extend(reviews_this_non_empty)
        if len(reviews) >= nb_reviews_limit:
            break
    return reviews

def processed_books():
    if os.name != 'posix':
        path = 'C:/Users/Anca/Documents/GitHub/ProjectWatson/'
    else:
        path = './data/'
    if os.path.isfile(path + 'processed_books.txt'):
        f = open(path + 'processed_books.txt', 'r')
        processed = [str(line.strip()) for line in f]
        f.close()
    else:
        processed = []
    return set(processed)

def main():
    assert len(sys.argv) > 2
    start_id = int(sys.argv[1])
    end_id = int(sys.argv[2])
    max_depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    max_nb_reviews = int(sys.argv[4]) if len(sys.argv) > 4 else 99
    processed = processed_books()
    pool = ThreadPool(4)
    old = range(start_id, end_id)
    depth = 0
    while len(old) > 0 and depth < max_depth:
        new = old[:]
        old[:] = []
        old.extend(set(list(chain.from_iterable(pool.map(lambda x: get_information(x, depth, max_depth, max_nb_reviews, processed), new)))))
        depth += 1
    pool.close()
    pool.join()

    if os.name != 'posix':
        path = 'C:/Users/Anca/Documents/GitHub/ProjectWatson/data/'
    else:
        path = './data/'
    f = open(path + 'processed_books.txt', 'w')
    map(lambda x: f.write(str(x) + '\n'), processed)
    f.close()
main()
