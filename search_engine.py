from tokenizer import stem_tokens

def get_all_documents_with_token(index_file: str, token: str):
    """Given the path to the inverted index stored in JSON,
    return a list of all the document IDs containing a certain token."""
    with open(index_file, "r", encoding="utf-8") as f:
        index = json.load(f)
    postings = index[token]
    return [posting[0] for posting in postings]

def intersect(doc_list_1: list[int], doc_list_2: list[int]):
    """Given a list of document IDs and a token,
    return all document IDs in the list containing the token."""
    # For this functiom, we assume that both lists are stored.
    # Otherwise, this function will not work properly.
    index1 = 0
    index2 = 0
    docs = []
    while (index1 < len(doc_list_1) and index2 < len(doc_list_2)):
      if doc_list_1[index1] == doc_list[index2]:
        docs.append(doc_list_1[index1])
        index1 += 1
        index2 += 1
      if doc_list_1[index1] > doc_list[index2]:
        index2 += 1
      if doc_list_1[index1] < doc_list[index2]:
        index1 += 1
    return docs

def boolean_query(index_file: str, query: str):
    """Given a query and the path to the inverted index stored in JSON,
    return all results matching the query."""
    query_tokens = stem_tokens(query.split())
    if query_tokens:
        results = get_all_documents_with_token(index_file, query_tokens[0])
        if len(query_tokens) > 1:
            for token in query_tokens[1:]
                results = intersect(results, get_all_documents_with_token(index_file, token))
        return results
    else:
        return []
