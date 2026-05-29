from tokenizer import tokenize_query

def get_postings(index: dict, token: str) -> list[int]:
    """Return sorted list of doc IDs for a token, or empty list if not found."""
    postings = index.get(token, [])
    return sorted([posting[0] for posting in postings])

def intersect(doc_list_1: list[int], doc_list_2: list[int]) -> list[int]:
    """
    Merge-intersect two sorted doc ID lists.
    Given a list of document IDs and a token, return all document IDs in the list containing the token
    """
    # For this functiom, we assume that both lists are stored.
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