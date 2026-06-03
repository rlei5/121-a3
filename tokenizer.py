import re
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning


_stemmer = PorterStemmer()
def tokenize_query(query: str) -> list[str]:
    query = query.lower()
    tokens = []
    next_token = ""

    for char in query:
        if char.isalnum():
            next_token += char
        else:
            if next_token:
                tokens.append(next_token)
                next_token = ""

    if next_token:
        tokens.append(next_token)

    tokens = stem_tokens(tokens)
    return add_bigrams(tokens)

def tokenize(html_content: str) -> list[str]:
    soup = BeautifulSoup(html_content, "lxml")
    text = soup.get_text(separator=" ")
    tokens = []
    next_token = ""
    for char in text:
        if char.isalnum():
            next_token += char
        else:
            if next_token:
                tokens.append(next_token)
                next_token = ""

    if next_token:
        tokens.append(next_token)

    return tokens

def add_bigrams(tokens: list[str]) -> list[str]:
    return tokens + [f"{tokens[i]} {tokens[i + 1]}" for i in range(len(tokens) - 1)]

def get_important_tokens(html_content: str) -> list[str]:
    soup = BeautifulSoup(html_content, "lxml")
    important_text = []
    if soup.title:
        important_text.append(soup.title.get_text())
    for tag in soup.find_all(['h1', 'h2', 'h3', 'b', 'strong']):
        if tag.string:
            important_text.append(tag.string)
    return re.findall(r'[a-zA-Z0-9]+', " ".join(important_text))

def stem_tokens(tokens: list[str]) -> list[str]:
    return [_stemmer.stem(token.lower()) for token in tokens]

def get_simhash(tokens: list[str]) -> int:
    from collections import Counter
    def _hash_word(word):
        h = 0
        for char in word:
            h = (h * 31 + ord(char)) % (2**64)
        return h
    weights = Counter(tokens)
    v = [0] * 64
    for word, weight in weights.items():
        word_hash = _hash_word(word)
        for i in range(64):
            if (word_hash >> i) & 1:
                v[i] += weight
            else:
                v[i] -= weight
    fingerprint = 0
    for i in range(64):
        if v[i] > 0:
            fingerprint |= (1 << i)
    return fingerprint

if __name__ == "__main__":
    print(add_bigrams(['University', 'of', 'California', 'Irvine']))