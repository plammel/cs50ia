import token
from typing import Dict
import nltk
import sys
import os
import math
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

FILE_MATCHES = 1
SENTENCE_MATCHES = 5


def main():

    # Check command-line arguments
    # if len(sys.argv) != 2:
    #     sys.exit("Usage: python questions.py corpus")

    # # Calculate IDF values across files
    # files = load_files(sys.argv[1])
    files = load_files("corpus")
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".txt"):
            continue
        with open(os.path.join(directory, filename)) as f:
            content = f.read()
            files[filename] = content

    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(document)
    tokens = [token.lower() for token in tokens]
    tokens = [token for token in tokens if not token in nltk.corpus.stopwords.words('english')]

    return tokens

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    words = set()
    for filename in documents:
        words.update(documents[filename])

    # Calculate IDF values
    idfs = dict()
    for word in words:
        f = sum(word in documents[filename] for filename in documents)
        idf = math.log(len(documents) / f)
        idfs[word] = idf

    return idfs
    
    # # Calculate TF-IDF values
    # tfidfs = dict()
    # for filename in documents:
    #     tfidfs[filename] = []
    #     file = documents[filename]
    #     for word in file:
    #         tf = documents[filename][word]
    #         # tf = documents[filename].index(word)
    #         tfidfs[filename].append((word, tf * idfs[word]))

    # return tfidfs
    # words = set()

    # for filename in documents:
    #     words.update(documents[filename])
    # print(len(words))
    # tr_idf_model  = TfidfVectorizer(norm='l2',min_df=0, use_idf=True, smooth_idf=True, stop_words='english', sublinear_tf=True)
    # tf_idf_vector = tr_idf_model.fit_transform(words)
    # print("Feature Names n",tf_idf_vector.get_feature_names_out())
    # indices = np.argsort(tf_idf_vector.idf_)[::-1]
    
    # for word in words:
    #     tf_idf_vector.todense()

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tfidfs = {}

    for file in files:
        tfidfs[file] = 0
        tokens_in_files = len(files[file])
        for word in query:
            if word in files[file]:
                frecuency = files[file].count(word) + 1
            else:
                frecuency = 1
            tf = frecuency/tokens_in_files
            if word in idfs.keys():
                idf = idfs[word]
            else:
                idf = 1
            tfidfs[file] += idf * tf

    sorted_list = sorted(tfidfs, key= tfidfs.get, reverse=True)

    top_files = sorted_list[:n]
    return top_files

def top_sentences(query, sentences, idfs, n):
    sentence_stats = {}

    
    for sentence in sentences:
        sentence_stats[sentence] = {}
        sentence_stats[sentence]['idf'] = 0
        sentence_stats[sentence]['word_count'] = 0
        sentence_length = len(sentences[sentence])

        for word in query:
            if word in sentences[sentence]:
                sentence_stats[sentence]['idf'] = idfs[word]
                sentence_stats[sentence]['word_count'] += 1
        sentence_stats[sentence]['QTD'] = float(sentence_stats[sentence]['word_count'] / sentence_length)

    sorted_list = sorted(sentence_stats, key=lambda sentence: (
        sentence_stats[sentence]['idf'], 
        sentence_stats[sentence]['word_count'],
        sentence_stats[sentence]['QTD']), reverse=True)

    # for s in sorted_list:
    #     print(s)
    #     print(len(sentences[sentence]))
    #     print(sentence_stats[s])
    return sorted_list[:n]


if __name__ == "__main__":
    main()
