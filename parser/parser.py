import nltk
import sys
import re

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | NP VP NP | VP NP PP | VP DetP ConjP | VP DetP | DetP DetP | VP DetP PP | VP ConjP DetP | VP NP PP ConjP PP 
AdvP -> Adv | Adv AdvP
AdjP -> Adj | Adj AdjP
NP -> N | N P | AdjP NP | NP Adv
PP -> P NP | P DetP | PP PP
DetP -> Det | Det NP | Det VP | DetP Adv
ConjP -> Conj | Conj VP | Conj NP | Conj PP | ConjP DetP
VP -> V | N VP | V P | Adv V | V Adv | V N | V Det
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        l = parser.parse(s)
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    nltk.download('punkt')
    sentence = sentence.lower()
    tokens = nltk.word_tokenize(sentence)
    tokens_copy = tokens.copy()
    
    for token in tokens_copy:
        if token.isalpha() is False:
            tokens.remove(token)

    return tokens

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    chunks = []
    for chunk in tree.subtrees():
        if chunk.label == "NP":
            counter = 0
            for sub_chunck in chunk.subtrees():
                if sub_chunck.label() == "NP":
                    counter += 1
            if counter < 2:
                chunks.append(chunk)
    return chunks


if __name__ == "__main__":
    main()
