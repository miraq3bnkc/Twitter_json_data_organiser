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
    6. Remove punctuation and other symbols
    7. Correct some typos
----8. Remove unnecessary information (like eg "subscribe") -> only for linked_article_text----NOT INCLUDED

"""
import json
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
        r'\b[\w.+-]+@[\w.-]+\.\w+\b',        # emails - very few occurrences, maybe it not needed
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
    text = re.sub(r'[^\w\sα-ω]', ' ', text)
    #collapse added whitespace
    text = ' '.join(text.split())

    # Restore protected strings
    for i, value in enumerate(protected):
        text = text.replace(f'__PROTECTED_{i}__', value)

    return text

#Replace words with their correct form from our dictionary
#manual correction -- future steps for a more wholesome and dynamic approach
def correct_words(text,filepath):
    words=text.split()

    with open(filepath, "r", encoding="utf-8") as f:
        correction=json.load(f)

    for i,_ in enumerate(words):
        if words[i] in correction:
            words[i]=correction[words[i]]

    text=' '.join(words)

    return text


#General call function for main
def text_clean_up(tweet):

    fields = [
        "text",
        "quoted_text",
        "linked_article_values"
    ]

    texts = [
        tweet.get(field)
        for field in fields
    ]

    for i,text in enumerate(texts):
        if not text:
            #check that text is not None
            continue

        if i>0:
            #only for quoted text and linked_article_values
            #normalization for post text has already occurred
            text=normalize_basics(text) 
    
        text=remove_symbols(text)
        text=correct_words(text,"general_typo_corrections.json")

        tweet[fields[i]]=text

    return tweet