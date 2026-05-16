from nltk.stem import  PorterStemmer
from bs4 import BeautifulSoup

def get_raw_text(html_content: str):
    """Given the HTML source of a webpage in html_content, this function returns the raw text from that webpage."""
    soup = BeautifulSoup(html_content)
def extract_important_words(html_content: str):
    """Given the HTML source of a webpage, return the important words on that page."""
    pass
def tokenize(text: str) -> list[str]:
    """Tokenize the text. The search engine specification defines a token as an alphanumeric sequence."""
    tokens = []
    next_token = ""
    for char in str:
        if char.isalnum():
            next_token += char
        else:
            if next_token:
                tokens.append(next_token)
                next_token = ""
    return tokens
def apply_stemming(tokens: list[str]):
    """Stems each token using the Porter Stemmer."""
    stemmer = PorterStemmer()
    return [stemmer.stem(token) for token in tokens]
def normalize_tokens(tokens):
    """Maps each token to some standard form, for example, """
    pass