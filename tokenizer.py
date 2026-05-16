import re
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning


_stemmer = PorterStemmer()

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
    return tokens

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
    return [_stemmer.stem(token) for token in tokens]
