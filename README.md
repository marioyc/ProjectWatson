# ProjectWatson

Projet3A - IBM Watson

# MongoDB

In order to simplify data processing (playing with thousands of json files is a nightmare) and to optimize scripts, we have decided to immigrate data storage to MongoDB.

For running `app.py`, the package `flask-pymongo` is needed. It provide an interface for Flask (and python) to communicate with MongoDB. 

Moreover, make sure that **mongod** is running on `localhost:27017` with a `--dbpath` correctly configured. 

>   --dbpath could be anywhere on your disk, as long as the directory exists.

If `mongod` runs correctly, you can type `mongo` in the console to connect to MongoDB. Before starting `app.py`, make sure the data are imported by following commands:

    mongoimport --db app --collection books --file books.json --jsonArray
    mongoimport --db app --collection vocabulary --file vocabulary.json --jsonArray
    mongoimport --db app --collection tf_idf --file tf_idf.json --jsonArray

>   we name the database **app** in order to be coherent with Flask convention

For more details, please refer to [official tutorial of flask-pymongo](https://flask-pymongo.readthedocs.org/en/latest/) if play with Flask, or [official tutorial of pymongo](http://api.mongodb.org/python/current/tutorial.html) if play with a single script. 

# Data

All data are disponible on [Google Drive](https://drive.google.com/file/d/0B2byUnoZLvgHZ0xwcWtVdENDeEE/view?usp=sharing)

If you just look for tf_idf.json, it is also in [data](./data) directory. 

# Final Report

The LaTeX project of final report is hosted on [Overleaf](https://www.overleaf.com/4259520qtrvss). The advantage of this site is that we can modify documents **at the same time**, no risk of merge conflicts. 

For now its layout is not very fancy, but we can improve these things later. An alternative is to use [Binet Typographics' Template](http://typographix.binets.fr/files/polytechnique-LaTeX.zip), but it's maybe tooooo fancy. 

## Convetion

### TF-IDF Matrix

TF-IDF matrix is store in a json file in following form:

```json
[
    {
        'id': 1,
        'value': [
                    {
                        'id': 2,
                        'value': 0.9
                    },
                    {
                        'id': 3,
                        'value': 0.1
                    }
                ]
    }, 
    {
        'id': 2,
        'value': [
                    {
                        'id': 1,
                        'value': 0.9
                    },
                    {
                        'id': 3,
                        'value': 0.1
                    }
                ]
    }
]
```

**Only** n.json with **n < 5000** are treated (about 500 books, since not all json exists), we can process more after demo. However, we should keep in mind that a matrix 10000 \* 10000 would barely contained in memory, so a MySQL-like **database** maybe needed. 

##  Data

Data under reconstruction, coming soon....

Old data (not maintained anymore) are available at [Google Drive](https://drive.google.com/folderview?id=0B2byUnoZLvgHcTFEeVdwaGR4dEk&usp=sharing)

Algorithm of Similarity Calculation: [Google Drive again](https://docs.google.com/document/d/1uBQvfAvx66lFaVzDRO9rpLlacqVh4ZsDetHcyuuRsUg/edit?usp=sharing)

##  Abstract

Recommendation is a hot topic in data mining and has vaste application
in day life. However, there is no satisfactory recommendation system
nowadays available for books, which is desired by many people. We wish
to design and implement a better system recommending books according to
user’s profile by exploring information associated to each book. Our
goal is to use IBM Watson’s efficient tools for keywords and concepts
extraction and sentiment analysis in order to build a strong similarity
criteria. The information on books shall be stored in a graph database
which is most suited for our problem.

Our project is challenging since natural language processing is a
relatively immature domaine, many researches are still ongoing.
Moreover, because of the nature of books, we do not have the access to
the entire, which means that all of our analysis will be based on a
small piece of description and comments of the readers. Though
challenging, our project will interest many people especially book
lovers. By navigating through our graph database, they could take an
interactive walk in the books’ network and find their next book to read.

Up to now, we have identified the data source (Goodreads.com) and the
method to get access to them. We have fetched information of thousands
of books so far by using Goodreads API and Python along with Scrapy and
BeautifulSoup libraries. Besides basic information, we mainly collected
description, rating, users’ tags and reviews of a book. All of which are
stored in JSON to facilitate further exploration. Also, we did a
research on the use of the IBM Graph Data Store which will play an
essential role in our project.

We are going to use Alchemy API for extracting concepts about texts and
Graph Data Store to create relevant links between books.

A detailed schedule is as following:

-   today - 18 December 2015 : finalization of data collection and begin
    of filling graph database (only the vertices).

-   21 December 2015 - 8 January 2016: state of the art of the
    techniques used to compute the similarity between books using users’
    tags/ text/ description/ reviews; decision of which Bluemix tool
    will be more appropriate to implement one of these methods.

-   8 January 2016 - 22 January 2016: implementation of an efficient
    method to compute similarity.

-   25 January 2016 - 1 February: creation of edges in the
    graph database.

-   From 1 February 2016: creation and design of a user interface and
    preparation of demo.

Division of work:

-   Graph data store and visualization: Mario <span
    style="font-variant:small-caps;">Ynocente Castro</span>, Jianyang
    <span style="font-variant:small-caps;">Pan</span>

-   Computation of similarity: Ana-Maria <span
    style="font-variant:small-caps;">Cretu</span>, Baoyang <span
    style="font-variant:small-caps;">Song</span>

-   User interface: Jingtao <span
    style="font-variant:small-caps;">Han</span>


