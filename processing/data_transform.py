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

    return tweets

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
#

def remove_replace_url(text,urls):
    url = r"https://t\.co/\S*"
    matches = list(re.finditer(url, text))

    #check if urls found aren't just from external urls (from "urls" feature) 
    if len(matches)>len(url):
        last = matches[-1] #get last occurrence
        #check if last occurrence is at the end of text 
        if last.end()==len(text):
            text = text[:last.start()]
    elif matches:
        #replace url substring in text with <URL>
        text=re.sub(url,"<URL>",text)

    return text


def text_cleanup(text,entities):
    [hashtags, media, urls, mentions]=entities
    text=remove_mention_text(text,mentions)
    text=remove_replace_url(text,urls)
    return text