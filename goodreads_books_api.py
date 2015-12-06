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
import pyisbn 
import time
import re
from bs4 import BeautifulSoup

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
    key = 'C29sMtUMNv1TXwvnvKjw'
    number = str(number)
    if len(number) == 10 or len(number) == 13:
        assert pyisbn.validate(number), 'Oops, invalid isbn number'
        url = 'https://www.goodreads.com/book/isbn?isbn=' + number + '&key='+ key
    else:
        url = 'https://www.goodreads.com/book/show/' + number + '?format=xml&key=' + key
    proxies = {'http': 'http://kuzh.polytechnique.fr:8080',
            'https': 'http://kuzh.polytechnique.fr:8080'}
    r = requests.get(url, proxies = proxies)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'xml')
    return soup

def get_information_from_soup(soup, nb_reviews_limit = None):
    """get useful information from a BeautifulSoup object
    return a dictionary
    """
    info = {}
    assert soup.id is not None, 'Oops, book not found on GoodReads'    
    info['id'] = int(soup.id.string.strip())
    info['isbn13'] = int(soup.isbn13.string.strip())
    info['title'] = soup.title.string.strip()
    info['image_url'] = soup.image_url.string.strip()
    info['publisher'] = soup.publisher.string.strip()
    info['publication_date'] = soup.publication_year.string.strip() + '-' + soup.publication_month.string.strip().zfill(2) + '-' + soup.publication_day.string.strip().zfill(2)
    info['description'] = remove_html_tags(soup.description.string.strip())
    info['authors'] = get_information_authors(soup.authors) 
    info['avg_rating'] = float(soup.average_rating.string.strip())
    info['num_pages'] = int(soup.num_pages.string.strip()) 
    info['shelves'] = get_information_popular_shelves(soup.popular_shelves)
    info['reviews'] = get_information_reviews(soup.reviews_widget, nb_reviews_limit)
    return info

def get_information_authors(authors):
    """get authors information from a BeautifulSoup tag object
    since a book may have more than one author
    return a list of dictionaries
    """
    authors_clean = [author for author in authors.contents if author != '\n']
    infos = []
    for author in authors_clean:
        info = {}
        info['id'] = int(author.find('id').string.strip())
        info['name'] = author.find('name').string.strip()
        info['avg_rating'] = float(author.find('average_rating').string)
        if author.find('image_url')['nophoto'] == 'false':
            info['image_url'] = author.find('image_url').string.strip()
        infos.append(info)
    return infos

def get_information_popular_shelves(shelves):
    """return popular shelves information from a BeautifulSoup tag object
    """
    shelves_clean = [shelf for shelf in shelves.contents if shelf != '\n']
    infos = {}
    for shelf in shelves_clean:
        infos[shelf['name']] = int(shelf['count'])
    return infos

def get_information_reviews(widget, nb_reviews_limit = None):
    """return reviews of a book
    givien a widget returned by GoodReads API
    if nb_reviews_limit is specified, only first nb_reviews_limit reviews will be returned
    if not, all (MANY!!) reviews will be returned
    """
    soup = BeautifulSoup(widget.text, 'lxml')
    url_basic = soup.body.find('iframe', id='the_iframe')['src']
    r = requests.get(url_basic)
    r.raise_for_status()
    soup2 = BeautifulSoup(r.text, 'lxml')
    nb_pages = int(soup2.find('a', 'next_page').previous_sibling.previous_sibling.string)
    nb_reviews = 0
    reviews = []
    for i in range(nb_pages+1):
        url_page = re.sub('min_rating=&', 'min_rating=&page=' + str(i) + '&', url_basic) 
        r_page = requests.get(url_page)
        r_page.raise_for_status()
        soup_page = BeautifulSoup(r_page.text, 'lxml')
        links = soup_page.body.find_all(lambda tag: tag.name == 'a' and tag.has_attr('href') and tag.has_attr('itemprop'))
        for link_raw in links:
            time.sleep(0.5)
            review = {}
            link_review = link_raw['href']
            r_review = requests.get(link_review)
            soup_review = BeautifulSoup(r_review.text, 'lxml')
            review['body'] = soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewBody').text.strip()
            review['rating'] = int(soup_review.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag.has_attr('itemprop') and tag['itemprop'] == 'reviewRating').text.strip().split()[0])
            review['likes'] = int(soup_review.find('span', 'likesCount').text.strip().split()[0]) 
            review['date'] = soup_review.find('span', itemprop = 'publishDate').next_sibling.next_sibling['title']
            reviews.append(review)
            if nb_reviews_limit and nb_reviews > nb_reviews_limit:
                return reviews
            nb_reviews += 1
    return reviews
def remove_html_tags(string):
    """delete annoying html tags in the description of a book
    using a regex
    """
    return re.sub('<[^[]+?>', '', string) 
