from tokenizer import tokenize_query
import math
from functools import cache

@cache
def get_postings(index: dict, token: str) -> list[int]:
    """Return sorted list of doc IDs for a token, or empty list if not found."""
    postings = index.get(token["postings"], [])
    return sorted([posting[0] for posting in postings])

def get_df(index: dict, token: list[str]):
    """Returns a list of corresponding doc frequencies from a list of tokens."""
    return index.get(token["doc_freq"], 0)

@cache
def get_idf(index: dict, token: list[str]):
    """Gets the inverse document frequency of a token in the index."""
    df = get_df(index, token)
    # For whatever reason, log10 is faster than all the other logarithm functions.
    # The base for the logarithm does not matter, which is why we can choose log10.
    # (according to page 118 of Manning, Raghavan, and Schutze)
    return math.log10(len(index) / df) if df != 0 else 0

def get_tf(index: dict, token: list[str], doc_id: int, important=False):
    """Gets the term frequency of a token in doc_id in the index."""
    postings = index.get(token["postings"], [])
    for post in postings:
        if post[0] == doc_id:
            return post[2] if important else post[1]
    return 0
    
def intersect(doc_list_1: list[int], doc_list_2: list[int]) -> list[int]:
    """
    Merge-intersect two sorted doc ID lists.
    Given a list of document IDs and a token, return all document IDs in the list containing the token
    """
    # For this function, we assume that both lists are sorted.
    # Otherwise, this function will not work properly.
    index1 = 0
    index2 = 0
    docs = []
    while index1 < len(doc_list_1) and index2 < len(doc_list_2):
        if doc_list_1[index1] == doc_list_2[index2]:
            docs.append(doc_list_1[index1])
            index1 += 1
            index2 += 1
        elif doc_list_1[index1] > doc_list_2[index2]:
            index2 += 1
        else:
            index1 += 1
    return docs

def boolean_query(index: dict, query: str) -> list[int]:
    """Return top 5 doc IDs matching all query terms (AND logic)."""
    query_tokens = tokenize_query(query)
    if not query_tokens:
        return []

    results = get_postings(index, query_tokens[0])
    for token in query_tokens[1:]:
        results = intersect(results, get_postings(index, token))

    return results[:5]

def scored_query()
    pass
