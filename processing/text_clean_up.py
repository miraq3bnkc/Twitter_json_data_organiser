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

def remove_symbols(text): 
    # Things containing @ that should be preserved
    protected = []

    patterns = [
        r'https?://[^\s]+',                  # URLs --> maybe i will handle it like the rest of urls
        r'\b[\w.+-]+@[\w.-]+\.\w+\b',        # emails --> i will handle it like urls
        r'(?<!\w)@[A-Za-z][A-Za-z0-9_-]*',   # @handles starting with English letter - some cases that stayed unresolved
        '@χρηστησ',                          # the replaced mentions tokens
        '<url>',                             # tokens used for url replacement 
    ]

    for pattern in patterns:
        def save(m):
            protected.append(m.group(0))
            return f'__PROTECTED_{len(protected)-1}__'

        text = re.sub(pattern, save, text)

    # Replace remaining @
    text = text.replace('@', 'α')
    #replace the rest of the symbols
    text = re.sub(r'[^\w\s[α-ω]<>]', ' ', text)
    #collapse added whitespace
    text = ' '.join(text.split())

    # Restore protected strings
    for i, value in enumerate(protected):
        text = text.replace(f'__PROTECTED_{i}__', value)

    return text
