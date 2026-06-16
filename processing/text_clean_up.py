"""
This file's purpose is about the required text pre-processing step.

It includes the following:
    1. Convert to lowercase representation
    2. Normalize hashtags (remove '#', '_' and separate words)
    3. Remove punctuation
    4. Remove stopwords
    5. Remove unnecessary information (like eg "subscribe") -> only for linked_article_text
    6. Lemmatisation

"""

def normalize(text):
    text=text.lower()

    text=text.replace('#','')
    text=text.replace('_',' ') #add whitespace for '_'
    return text