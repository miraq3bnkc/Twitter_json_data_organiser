"""Transforming the raw data extracted from the raw tweet response"""

import hashlib
from datetime import date,datetime
import re

#function for accessing the datetime string existing in "createdAt" field
def parse_date(tweet):
    return datetime.strptime(tweet["createdAt"], "%a %b %d %H:%M:%S %z %Y")

def account_age(tweet):
    creation_date=parse_date(tweet["author"]).date()
    today = date.today()
    #account age in days
    account_age=(today-creation_date).days

    #make new field about age and remove the createdAt
    tweet["author"]["account_age_days"] = account_age
    del tweet["author"]["createdAt"]

    return tweet

#Keep only the mentions that are not the default mention by replying to a post
def transform_mentions(reply_username, mentions):
    new_mentions=[]

    for i in range(len(mentions)):
        if mentions[i]!=reply_username:
            new_mentions.append(mentions[i])
    
    return new_mentions


'''UNUSED FEATURE transform_urls --- WE ONLY KEPT NUMBER OF URLS '''
#Change urls to their article domain if they are linked through a redirecting link
def transform_urls(article_domain,urls):
    redirectors=[
        "dlvr.it",
        "ift.tt",
        "ow.ly",
        "share.google",
        "search.app",
        "bit.ly",
        "disq.us",
        "tinyurl.com"
    ]
    
    for i, url in enumerate(urls):
        for redirector in redirectors:
            if url.find(redirector)!=-1:
                urls[i] = article_domain
                break

    return urls

    
def anonymize_username(username):
    return hashlib.sha256(username.encode()).hexdigest()

"""replace_username_id function would no be needed if we extract in the first place the ids form mentions in the raw"""
irrelevant_users={}
#Replace usernames with user ids
def replace_username_id(tweets,users):
    for j,_ in enumerate(tweets):
        user_mentions=tweets[j]["user_mentions"]
 
        for i,mention in enumerate(user_mentions):
            if mention in users:
                user_mentions[i]=users[mention]
            else:
                #the mentioned user is not in our user list 
                if mention in irrelevant_users:
                    user_mentions[i]=irrelevant_users[mention]            
                else:
                    #if the user is not in our irrelevant list either 
                    new_id=anonymize_username(mention) # create id
                    irrelevant_users[mention]= new_id # add user to irrelevant list
                    user_mentions[i]=new_id #replace username with new id

        tweets[j]["user_mentions"]=user_mentions

        text,num_mentions=remove_mention_text_2(tweets[j])
        if len(tweets[j]["user_mentions"])<num_mentions:
            tweets[j]["user_mentions"].append("forgotten_mention")
        tweets[j]["text"]=text

    return tweets


def remove_mention_text_2(tweet):
    #check also for mentions that were not removed from text with remove_mention_text
    mention_regex=r'^(@[A-Za-z0-9_]+\s)' #check if we have in the beginning of the text only a mention that wasn't removed
    text=tweet['text']
    text=re.sub(mention_regex,'@ΧΡΗΣΤΗΣ',text)
    
    #do the same in repeat for at least two times 
    #just to be sure we got all users from a conversation thread
    end=0
    for i in range(0,2):
        match=re.match('@ΧΡΗΣΤΗΣ ',text[end:])
        if match:
            end=match.end()*(i+1)
            temp=re.sub(mention_regex,'@ΧΡΗΣΤΗΣ ',text[end:])
            text=text[match.start():end]+temp
    
    return text,len(re.findall('@ΧΡΗΣΤΗΣ',text))-1

#Remove mentions from text
def remove_mention_text(text,user_mentions):
    if len(user_mentions)>=1:
        for mention in user_mentions:
            text = text.replace(mention, "ΧΡΗΣΤΗΣ")
    return text

#Remove and Replace Urls from text

#1. Specifically removing media urls 
# (which they exist at the end of the string of feature "text")
#2. Replacing the rest of the urls with "<URL>"
# (those are external and exist also in urls feature)
# (in linked_article_text, urls have different representation
# and do not exist in urls feature)

def remove_replace_url(text,urls,isTweet):
    if isTweet:
        url = r"https://t\.co/\S*"
    else:
        url=r'(https?://[^\sα-ω]+|www\.[^\sα-ω]+)'

    #find urls in the text
    matches = list(re.finditer(url, text))

    #check if urls found aren't just from external urls (from "urls" feature)
    # only for tweet text 
    if len(matches)>len(urls) and isTweet:
        last = matches[-1] #get last occurrence
        #check if last occurrence is at the end of text 
        if last.end()==len(text):
            text = text[:last.start()]
            # recompute matches because text changed
            matches = list(re.finditer(url, text))
    
    if matches:
        #replace url substring in text with <URL>
        text=re.sub(url,"<URL>",text)

    return text


def text_cleanup(text,entities,isTweet):
    [hashtags, media, urls, mentions]=entities
    if text:
        text=remove_mention_text(text,mentions)
        text=remove_replace_url(text,urls,isTweet)
    return text