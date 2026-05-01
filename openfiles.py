import os
import json
from remove_posts import de_duplicate,delete_tweets
from remove_fields import clean_tweet
from datetime import datetime
from additional.data_transform import replace_username_id

path = r"../apify/digital_ids (Copy)" #path that includes the .json files (only) 

#function for accessing the datetime string existing in "createdAt" field
def parse_date(tweet):
    return datetime.strptime(tweet["createdAt"], "%a %b %d %H:%M:%S %z %Y")

all_tweets=[]
all_quotes=[]
users={}
#Loop through all files in folder and clean them
for file in os.scandir(path):
    if file.is_file():
        data=[] # initialization of the data in the .json file 

        with open(file.path, "r",encoding="utf-8") as f:
            print("Cleaning ", file.name, ":")
            data = json.load(f) # Load .json file for clean up
        
        #De-duplicate json data (remove duplicate tweets by id)
        unique_data = de_duplicate(data)


        cleaned_tweets=[]
        cleaned_quotes=[]

        for tweet in unique_data:
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

        all_tweets.extend(cleaned_tweets) #merging all the tweets together via extend
        all_quotes.extend(cleaned_quotes) #the same for quotes
        
        
#de-duplicate quotes
unique_quotes=de_duplicate(all_quotes)


#checking if the quotes do not already exist in the set of tweets
existing_ids = {t["id"] for t in all_tweets}

for quote in unique_quotes:
    if quote.get("id") not in existing_ids:
        all_tweets.append(quote)  #adding quotes to the collection of tweets as separate entities
        existing_ids.add(quote.get("id"))

# sort tweets by createdAt
tweets_sorted = sorted(all_tweets, key=parse_date,reverse=True)


# save user list in a file
with open("users.json", "w", encoding="utf-8") as f:
    json.dump(users, f, ensure_ascii=False, indent=2)

#Now that we have all the users, let's erase usernames from data
for i,tweet in enumerate(tweets_sorted):
    #Step 1: erase usernames from mentions--> replace them with user ids
    tweets_sorted[i]["user_mentions"]=replace_username_id(tweet["user_mentions"],users)

# save merged file
with open("merged.json", "w", encoding="utf-8") as f:
    json.dump(tweets_sorted, f, ensure_ascii=False, indent=2)