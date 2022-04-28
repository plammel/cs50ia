import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    tm = {}
    rank = 0
    
    for other_page in corpus:
        if len(corpus[page]) == 0:
            rank = 1/len(corpus)
        else:
            rank = (1 - damping_factor) / len(corpus)
            if other_page in corpus[page]:
                rank += (damping_factor/len(corpus[page]))
        tm[other_page] = rank

    return tm


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    sample_pageranks = {}
    for page in corpus:
        sample_pageranks[page] = 0

    sample = None

    for i in range(n):
        if sample is None:
            sample = random.choice(list(corpus))
        else:
            tm = transition_model(corpus, sample, damping_factor)
            keys = list(corpus)
            values = []
            for key in keys:
                values.append(tm[key])
            sample = random.choices(keys, values).pop()
        sample_pageranks[sample] += 1

    for entry in sample_pageranks:
        sample_pageranks[entry] = sample_pageranks[entry]/n
        
    return sample_pageranks

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    ranking_dict = {}
    for page in corpus:
        ranking_dict[page] = 1 / len(corpus)

    variation =  1
    while variation > 0.000001:
        variation = 0
        ranking_dict_copy = ranking_dict.copy()
        for page in corpus:
            oldRank = ranking_dict[page]
            outbound = 0
            for other_page in corpus:
                if page in corpus[other_page]:
                    outbound += ranking_dict_copy[other_page]/len(corpus[other_page])
            newRank = ((1 - damping_factor) / len(corpus)) + damping_factor * outbound
            ranking_dict[page] = newRank
            change = abs(oldRank - newRank)

            if (change > variation):
                variation = change
    return ranking_dict


if __name__ == "__main__":
    main()
