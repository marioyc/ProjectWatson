"""given the isbn of a book
fetch basic information including publisher, author(s), description, etc
example
soup = fetch('9781476705583')
info = get_information(soup)
print info
"""

import requests
import pyisbn 
import datetime
import re
from bs4 import BeautifulSoup

def fetch(isbn):
    """fetch raw data of a given isbn
    return a BeautifulSoup object
    """
    if not pyisbn.validate(isbn):
        print 'Oops, the isbn entered seems invalid'
        return
    key = 'C29sMtUMNv1TXwvnvKjw'
    url = 'https://www.goodreads.com/book/isbn?isbn=' + isbn + '&key='+ key
    r = requests.get(url, 'xml')
    if r.status_code != 200:
        print 'Oops, connection failed'
        return
    soup = BeautifulSoup(r.text, 'xml')
    if soup.error:
        print 'Oops, book not found on GoodReads'
        return
    return soup

def get_information(soup):
    """get useful information from a BeautifulSoup object
    """
    info = {}
    info['id'] = int(soup.id.string.strip())
    info['title'] = soup.title.string.strip()
    info['image_url'] = soup.image_url.string.strip()
    info['publisher'] = soup.publisher.string.strip()
    info['publication_date'] = datetime.date(int(soup.publication_year.string.strip()), int(soup.publication_month.string.strip()), int(soup.publication_day.string.strip()))
    info['description'] = remove_html_tags(soup.description.string.strip())
    info['authors'] = get_information_authors(soup.authors) 
    info['avg_rating'] = float(soup.average_rating.string.strip())
    info['num_pages'] = int(soup.num_pages.string.strip()) 
    info['shelves'] = get_information_popular_shelves(soup.popular_shelves)
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

def remove_html_tags(string):
    """delete annoying html tags in the description of a book
    using a regex
    """
    return re.sub('<[^[]+?>', '', string) 
