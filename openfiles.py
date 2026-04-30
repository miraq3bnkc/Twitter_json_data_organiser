import os
import json
from remove_posts import de_duplicate,delete_tweets
from remove_fields import clean_tweet
from datetime import datetime
from additional.data_transform import get_user_list

path = r"../apify/digital_ids (Copy)" #path that includes the .json files (only) 

#function for accessing the datetime string existing in "createdAt" field
def parse_date(tweet):
    return datetime.strptime(tweet["createdAt"], "%a %b %d %H:%M:%S %z %Y")

all_tweets=[]
all_quotes=[]
#Loop through all files in folder and clean them
for file in os.scandir(path):
    if file.is_file():
        data=[] # initialization of the data in the .json file 

        with open(file.path, "r",encoding="utf-8") as f:
            print("Cleaning ", file.name, ":")
            data = json.load(f) # Load .json file for clean up
        
        #De-duplicate json data (remove duplicate tweets by id)
        unique_data = de_duplicate(data)

        #Delete noise (non-greek or non-greeklish tweets)
        denoised_data=delete_tweets(unique_data)
        
        #removing unnecessary fields in tweet data
        #And separating quotes from tweets
        cleaned_tweets=[]
        cleaned_quotes=[]
        for tweet in denoised_data:
            potential_tweet, potential_quote=clean_tweet(tweet,False)
            
            cleaned_tweets.append(potential_tweet)
            if potential_quote:
                cleaned_quotes.append(potential_quote)

        all_tweets.extend(cleaned_tweets) #merging all the tweets together via extend
        all_quotes.extend(cleaned_quotes) #the same for quotes
        
        
#delete noisy and duplicated quotes
unique_quotes=de_duplicate(all_quotes)
final_quotes=delete_tweets(unique_quotes)

#checking if the quotes do not already exist in the set of tweets
existing_ids = {t["id"] for t in all_tweets}

for quote in final_quotes:
    if quote.get("id") not in existing_ids:
        all_tweets.append(quote)  #adding quotes to the collection of tweets as separate entities
        existing_ids.add(quote.get("id"))

# sort tweets by createdAt
tweets_sorted = sorted(all_tweets, key=parse_date,reverse=True)


# save merged file
with open("merged.json", "w", encoding="utf-8") as f:
    json.dump(tweets_sorted, f, ensure_ascii=False, indent=2)

#create users list file
get_user_list(tweets_sorted)
