from collections import namedtuple, Counter
import json


INVERTED_INDEX = {}

# based on general specs, certain words are more important and used in search somehow in a later milestone
# note that the frequency of the token is the sum of regular_freq and important_freq
Posting = namedtuple('Posting', ['doc_id', 'regular_freq', 'important_freq'])

# doc_id will have to be created beforehand based on the URL
def update_inverted_index(doc_id: int, tokens: list[str], important_tokens: list[str]) -> None:
    global INVERTED_INDEX

    # takes a list and converts to a dictionary where the key, value is token, frequency
    tokens = Counter(tokens)
    important_tokens = Counter(important_tokens)

    for token, frequency in tokens.items():
        if token not in INVERTED_INDEX:
            INVERTED_INDEX[token] = []

        if token in important_tokens:
            INVERTED_INDEX[token].append(Posting(doc_id, frequency - important_tokens[token], important_tokens[token]))
        else:
            INVERTED_INDEX[token].append(Posting(doc_id, frequency, 0))

    for token, frequency in important_tokens.items():
        if token not in INVERTED_INDEX:
            INVERTED_INDEX[token] = []

        # if the token is in both lists, then it was already covered in the previous loop
        if token not in tokens:
            INVERTED_INDEX[token].append(Posting(doc_id, 0, frequency))

def offload_to_disk(file_name) -> None:
    global INVERTED_INDEX

    serializable = {
        token: {"doc_freq": len(postings), "postings": [list(p) for p in postings]}
        for token, postings in INVERTED_INDEX.items()
    }

    with open(file_name, 'w') as file:
        json.dump(serializable, file)

    INVERTED_INDEX.clear()


# if __name__ == '__main__':
#     update_inverted_index(1, ['a', 'a', 'a', 'b', 'b', 'c'], ['b'])
#     update_inverted_index(2, ['a'], ['a'])
#     update_inverted_index(3, ['y'], ['z'])
#
#     print(INVERTED_INDEX)
#     offload_to_disk('example_file.json')