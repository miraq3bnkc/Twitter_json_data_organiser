import os
import json
from processing.remove_posts import de_duplicate,delete_tweets
from processing.remove_fields import clean_tweet
from datetime import datetime


#function for accessing the datetime string existing in "createdAt" field
def parse_date(tweet):
    return datetime.strptime(tweet["createdAt"], "%a %b %d %H:%M:%S %z %Y")


def load_data(path):
    data=[] #Load all data in the files

    for file in os.scandir(path):
        if file.is_file():
            with open(file.path, "r",encoding="utf-8") as f:
                data.extend(json.load(f)) # Load .json file for clean up

    #De-duplicate json data (remove duplicate tweets by id)
    data = de_duplicate(data)
    
    return data
        

def extract_transform(data):
    cleaned_tweets=[]
    cleaned_quotes=[]
    users={}

    #Loop through all tweets and clean them
    for tweet in data:
        #Delete noise (non-greek or non-greeklish tweets)
        kept=delete_tweets(tweet)
        
        #if the tweet post was kept (was not deleted)
        if kept:
            
            #removing unnecessary fields in tweet data
            #And separating quotes from tweets
            potential_tweet,user_info, potential_quote, quote_user=clean_tweet(tweet,False)
            cleaned_tweets.append(potential_tweet)

            #create users list file
            users[user_info[0]] = user_info[1]

            if potential_quote:
                #filter out irrelevant quotes
                relevant_quote=delete_tweets(potential_quote)
                if relevant_quote and quote_user[0]!="grok": 
                    users[quote_user[0]] = quote_user[1]
                    cleaned_quotes.append(potential_quote)
        
    print("\n=====================================================\n")

    return cleaned_tweets,cleaned_quotes,users
        

def merge_quotes(cleaned_quotes,cleaned_tweets):
    #de-duplicate quotes
    unique_quotes=de_duplicate(cleaned_quotes)

    #checking if the quotes do not already exist in the set of tweets
    #We are not using de_duplicate because that keeps the last instance
    #but we prefer the instance of the cleaned tweet than of quote
    existing_ids = {t["id"] for t in cleaned_tweets}

    for quote in unique_quotes:
        if quote.get("id") not in existing_ids:
            cleaned_tweets.append(quote)  #adding quotes to the collection of tweets as separate entities
            existing_ids.add(quote.get("id"))
    
    # sort tweets by createdAt
    tweets_sorted = sorted(cleaned_tweets, key=parse_date,reverse=True)

    return tweets_sorted


# save user list in a file
def save_file(filename,data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
