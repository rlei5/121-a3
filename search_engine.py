import math
from functools import lru_cache, cache
import numpy as np
import json
from tokenizer import tokenize_query

class SearchEngine:
    """Class that allows you to search through the index of a search engine."""
    def __init__(self, index_path, seek_table, metadata, doc_id_map, simhash_map):
        self.index_path = index_path
        with open(seek_table, "r", encoding="utf-8") as f:
            self.seek_table = json.load(f)
        with open(metadata, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
            self.metadata['log_2_doc_dount'] = math.log2(self.metadata['doc_count'])
        with open(doc_id_map, "r", encoding="utf-8") as f:
            self.doc_id_map = json.load(f)
        with open(simhash_map, "r", encoding="utf-8") as f:
            self.simhash_map = json.load(f)
    
    @cache
    def get_doc_count(self):
        """Returns the number of documents indexed."""
        return self.metadata['doc_count']
    
    @lru_cache(maxsize=1024)
    def get_token_dict(self, token: str) -> dict[str]:
        """Returns the infomation about the token."""
        if token not in self.seek_table:
            return {}
        with open(self.index_path, "r", encoding="utf-8") as f:
            f.seek(self.seek_table[token])
            line = f.readline()
            token_dict = json.loads(line)
        entry = token_dict[token]
        # convert postings list to a dict keyed by doc_id for O(1) lookup in get_tf
        entry["postings"] = {p[0]: p for p in entry.get("postings", [])}
        return entry

    @lru_cache(maxsize=1024)
    def get_doc_ids(self, token: str) -> list[int]:
        """Return sorted list of doc IDs for a token, or empty list if not found."""
        token_dict = self.get_token_dict(token)
        return list(token_dict.get("postings", {}).keys())

    def get_df(self, token: str) -> int:
        """Gets the document frequency of the specified token."""
        return self.get_token_dict(token).get("doc_freq", 0)

    @lru_cache(maxsize=1024)
    def get_idf(self, token: str):
        """Gets the inverse document frequency of a token in the index."""
        df = self.get_df(token)
        # For whatever reason, log2 is faster than all the other logarithm functions (on the OpenLab machines)
        # The base for the logarithm does not matter, which is why we can choose log2.
        # (according to page 118 of Manning, Raghavan, and Schutze)
        return self.metadata['log_2_doc_dount'] - math.log2(df) if df != 0 else 0

    def get_highest_idf(self, tokens):
        """Returns the token that has the highest inverse document frequency"""
        return max(tokens, key=self.get_idf)

    def get_tf(self, token: str, doc_id: int, important=False):
        """Gets the term frequency of a token in doc_id in the index."""
        token_dict = self.get_token_dict(token)
        post = token_dict.get("postings", {}).get(doc_id)
        if post is None:
            return 0
        return post[2] if important else post[1]

    # Returns a document vector whose components are the scores based on a modified tf-idf system
    def modified_doc_tf_idf(self, tokens, doc_id):
        vector = []
        for token in tokens:
            post = self.get_token_dict(token).get("postings", {}).get(doc_id)
            if post is None:
                vector.append(0)
                continue
            idf = self.get_idf(token)
            vector.append((post[1] + 10 * post[2]) * idf)
        return np.array(vector)

    def intersect(self, doc_list_1: list[int], doc_list_2: list[int]) -> list[int]:
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

    def boolean_query(self, query: str) -> list[int]:
        """Return top 5 doc IDs matching all query terms (AND logic)."""
        query_tokens = tokenize_query(query)
        if not query_tokens:
            return []

        results = self.get_doc_ids(query_tokens[0])
        for token in query_tokens[1:]:
            results = self.intersect(results, self.get_doc_ids(token))

        return results[:5]

    def is_junk_url(self, url: str) -> bool:
        junk_extensions = ('.txt', '.bib', '.csv', '.log')
        junk_substrings = ('/datasets/', '/raw-attachment/')
        return url.endswith(junk_extensions) or any(s in url for s in junk_substrings)

    def is_near_duplicate(self, doc_id: int, seen: list[int], threshold: int = 3) -> bool:
        fingerprint = self.simhash_map.get(str(doc_id), -1)
        return any(bin(fingerprint ^ h).count('1') < threshold for h in seen)

    def scored_query(self, query: str) -> list[int]:
        """Return top 5 doc IDs ranked by TF-IDF, seeded from highest-IDF token."""
        query_tokens = tuple(sorted(tokenize_query(query)))
        if not query_tokens:
            return []

        candidates = self.get_doc_ids(self.get_highest_idf(query_tokens))

        def similarity(doc_id):
            return np.sum(self.modified_doc_tf_idf(query_tokens, doc_id)) / len(query_tokens)

        ranked = sorted(candidates, key=similarity, reverse=True)

        # filter junk URLs and near-duplicate content from top candidates
        results = []
        seen_fingerprints = []
        for doc_id in ranked:
            url = self.doc_id_map.get(str(doc_id), "")
            if self.is_junk_url(url):
                print(f"JUNK: {url}")
                continue
            if self.is_near_duplicate(doc_id, seen_fingerprints):
                print(f"DUPE: {url}")
                continue
            seen_fingerprints.append(self.simhash_map.get(str(doc_id), -1))
            results.append(doc_id)
            if len(results) == 5:
                break
        return results