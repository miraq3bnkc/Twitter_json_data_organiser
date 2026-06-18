"""
This file's purpose is about the required text pre-processing step.

It includes the following:
Basics:
    1. Split came case representation 
    2. Convert to lowercase representation
    3. Replace 'ς' with 'σ'
    4. Remove '#', '_' (for hashtags and word_segmentation)
    5. Remove accents
Rest:
    6. Remove punctuation
    7. Remove stopwords
    8. Remove unnecessary information (like eg "subscribe") -> only for linked_article_text
    9. Lemmatisation

"""
import re
import unicodedata

def normalize_basics(text):

    text=split_camel_case(text)

    text=text.lower()

    text=text.replace('#','')
    text=text.replace('_',' ') #add whitespace for '_'
    text=text.replace('ς','σ')

    #remove accents (greek tonal system)
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

    return text

def split_camel_case(text):
    #E.G. for 'NoIdea' this function returns 'No Idea'
    return re.sub(r'(?<=[a-zα-ω])(?=[A-ZΑ-Ω])', ' ', text)

def remove_punctuation(text): #unfinished
    text = re.sub(r'[^\w\s]', '', text)
    return text
