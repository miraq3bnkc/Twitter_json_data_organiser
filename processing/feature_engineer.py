""" 
The purpose of this file is the creation of new and derived features.
Here exist the creation of the following features:

TEXT FEATURES
    1. emojis : number of emojis in text

"""

import emoji

def get_n_emojis(tweet):
    emoji_list = emoji.emoji_list(tweet.get("text"))

    emoji_count_capped = min(len(emoji_list), 10) #Note 1

    tweet["emojis"]=emoji_count_capped

    return tweet

''' 
Note 1
E.g. in the dataset we are working with we had the following:
    total dataset post : 7970
    3 posts with 10  emojis     1 post with 23  emojis
    5 posts with 11  emojis     1 post with 34  emojis
    1 post  with 13  emojis     1 post with 177 emojis
    2 posts with 14  emojis
    1 post  with 15  emojis

    These were all grouped together (since they are outliers)
'''