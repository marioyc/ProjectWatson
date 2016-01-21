from tf_idf import *
import sys
import codecs
import os.path

path = 'data/'
filetype = '.json'
def save_vocabulary(ids):
    processed = set()
    if os.path.isfile(path + 'processed.txt'):
        f = open(path + 'processed.txt')
        for line in f:
            processed.add(int(line.strip()))
        f.close()
    ids = filter(lambda x: x not in processed, ids)

    filenames = map(lambda x: path + str(x) + filetype, ids)
    _, _, vocabulary = build_corpus(filenames)

    vocabulary_existed = set()
    if os.path.isfile(path + 'vocabulary.txt'):
        f = codecs.open(path + 'vocabulary.txt', 'r', 'utf-8')
        for line in f:
            vocabulary_existed.add(line) 
        f.close()

    vocabulary = filter(lambda x: x not in vocabulary_existed, vocabulary)
    f1 = open(path + 'processed.txt', 'a')
    f2 = codecs.open(path + 'vocabulary.txt', 'a', 'utf-8')
    map(lambda x: f1.write(str(x) + '\n'), ids)
    map(lambda x: f2.write(x + '\n'), vocabulary)
    f1.close()
    f2.close()
def main():
    ids = range(50)
    save_vocabulary(ids)
main()
