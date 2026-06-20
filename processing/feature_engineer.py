""" 
The purpose of this file is the creation of new and derived features.
Here exist the creation of the following features:

TEXT FEATURES
    1. n_emojis : number of emojis in text 
    2. emoji_list : keeps track of every emoji in text and the number of times it was used - REMOVED
    3. capital_ratio : uppercase letters / alphabetical letters 
    4. exclamation_marks: number of '!' chars in text
    5. question_marks: number of '?' and greek ';' chars in text
    6. n_chars: number of characters in post
    7. n_words: number of words in post's text
    8. emoji_category_count: label of what category of emoji was used and how many times
USER FEATURES
    1. followers_following_ratio : followers/following
    2. activity: average number of statuses per day

"""

import emoji
import re
from collections import Counter


'''TEXT FEATURES'''

#number of emojis  : integer ∃[0,10]
#counter of emojis : dictionary { emoji_char : integer (frequency of emoji in text) }
def get_n_emojis(tweet):
    emoji_list = emoji.emoji_list(tweet.get("text")) #dictionary with emoji positions and emojis
    emoji_list = [e["emoji"] for e in emoji_list] #convert to list with only the emojis
    emoji_count_capped = min(len(emoji_list), 10) #Note 1

    tweet["n_emojis"]=emoji_count_capped
    tweet["emoji_list"] = Counter(emoji_list)

    return tweet

#ratio of capital letters : float ∃[0.00, 1.00]
def get_capital_ratio(tweet):
    text=tweet.get("text")

    #capital ratio needs to be calculated only for the text the poster wrote
    # '<URL>' and '@ΧΡΗΣΤΗΣ' should be excluded 
    text= text.replace('@ΧΡΗΣΤΗΣ','')
    text= text.replace('<URL>','')

    capital_letters = list(filter(str.isupper, text))
    alphabetical_letters = list(filter(str.isalpha, text))

    #sometimes the post has no written text
    if alphabetical_letters:
        ratio= round(len(capital_letters)/len(alphabetical_letters),2)
        #rounding precision with 2 decimal places
    else:
        ratio=0.00 #note 2
    
    tweet["capital_ratio"]= ratio

    return tweet

#exclamation_marks: integer
#question_marks:    integer
def get_punctuation(tweet):
    text=tweet.get("text")

    question_mark=r'[;,?]'
    exclamation_mark='!'

    tweet["question_marks"]=min(len(re.findall(question_mark,text)),10) #note 3
    tweet["exclamation_marks"]=min(len(re.findall(exclamation_mark,text)),5)
    return tweet

#Features that need to be calculated before normalization!
def add_features_bn(tweet):
    tweet=get_n_emojis(tweet)
    tweet=get_capital_ratio(tweet)
    tweet=get_punctuation(tweet)
    return tweet

#feature calculated during preprocessing of text
#n_chars: integer
def get_n_chars(tweet):
    tweet["n_chars"]=len(tweet.get('text'))
    return tweet

#feature after complete preprocessing
#n_words: integer
def get_n_words(tweet):
    tweet["n_words"]=len(tweet["text"].split())
    return tweet


#EMOJI CATEGORIES FOUND IN OUR DATASET
# categories may be different for other datasets
# emojis found that do not exist in these categories where mostly neutral 
emoji_categories = {
    "vaccine": {"💉", "💊", "🦇", "🦠"},
    "id": {"🪪", "🆔", "📲", "📱", "🫆"},
    "ridicule": {"😂", "🤣", "🤡", "😜", "😁", "☺️", "🐑", "🙄", "😏", "😀", "😅", "😭", "🤪", "🍿", "🤦", "🤭", "🥳", "🤑", "👑", "😘", "😹", "🐒", "🤫", "🌟", "😍", "🙂", "🦧", "🤦‍♀️", "😄", "🥸", "😆", "👺", "🤦🏽‍♀️", "🐄", "🐵", "🐍", "🤴", "🤌🏻", "🤦‍♂️", "💖", "🥒", "🤦🏻", "👻", "💕", "💓", "❤️‍🔥", "💞", "🌹", "🫶🏼", "☺", "😛", "🫶🏻", "🥱", "🤗"},
    "alert": {"🚨", "❗", "🆘", "‼️", "🔥", "⚠️", "❓", "⏰", "🫵", "ℹ", "🗣️", "📢", "💥", "🛑", "📣", "🔊", "👂", "⁉️", "🕒", "⁉"},
    "direction": {"👇", "👉", "➡️", "👇🏻", "⏬", "⬇️", "➡", "🔗", "⤵️", "👈", "⬆️", "🌐", "👇🏽", "👆", "🔁", "⏩", "⤵", "◀️"},
    "hostility": {"🖕", "🤮", "😡", "❌", "🖐️", "🤬", "👿", "😈", "⛔", "🖐", "⭕",  "🚫", "🍒"},
    "identity": {"🇬🇷", "🇬🇧", "☦️", "🇪🇺", "🇫🇷", "✝️", "🇺🇸", "🇵🇸", "🇪🇸", "☦", "🇸🇻", "🇮🇱", "🇮🇹", "🇨🇾", "🇷🇺"},
    "thinking": {"🤔", "🤨", "🧠", "👀", "🤷🏼‍♀️", "🤷‍♀️", "🤷"},
    "support": {"👏", "🤝", "👍", "👊",  "✌️",  "🙏", "💪", "💯", "👌", "🥂", "💙", "✊", "🤘", "🥇", "🍺", "🙏🏻", "💫", "👍🏼", "👌🏼", "🌺", "🎉" "😇"},
    "smugness": {"😎", "🤠", "😋", "😉"},
    "negative": {"😱", "🙈", "🫣", "😬", "🙃", "😵‍💫", "😲", "😳", "🤯", "😔", "🥹" "😶" "😶‍🌫️", "🫠", "🥺", "🥴", "🥲", "😢", "😤", "😵", "😣", "😐", "💀", "😰", "🫤", "🫥" "🐉", "🔒"}
}

#emoji_category_count : integer
def emoji_sentiment(tweet):
    emojis = tweet.get("emoji_list",{})

    for category in emoji_categories:
        tweet[f"emoji_{category}_count"] = 0

    for emoji,count in emojis.items():
        for category, emoji_set in emoji_categories.items():
            if emoji in emoji_set:
                tweet[f"emoji_{category}_count"] += count
                break
    del tweet["emoji_list"]
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

Note 2
If the text body of a post has only lowercase letters, ratio equals 0
The same happens if there was no text at all, ratio equals 0
The instances for the latter were minimal, so we did not handle it 
differently than a text with no uppercase letters!

Note 3
Just like in Note 1, we capped the results because after certain number
of punctuation marks the instances become pretty sparse.
'''

###############################################################################
'''USER FEATURES'''

#followers/following : float ∃[0.00, infinity)
def get_followers_following_ratio(author):
    followers=author['followers']
    following=author['following']
    if following:
        ratio=round(followers/following,2)
    else:
        ratio=0
    author["followers_following_ratio"]=ratio
    return author

#posts/day : float ∃[0.0, infinity)
def get_activity(author):
    posts=author["statusesCount"]
    days=author["account_age_days"]
    #we dont check for division by zero since days>0 always
    author["activity"]=round(posts/days,1)
    return author