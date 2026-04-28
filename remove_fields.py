"""This python script is created for the purposes of "cleaning" the .json data
   that contain information about X.com posts. 
   Specifically it will remove unnecessary fields and change/rename some other fields.
   This will all be according to the readme file were you can see the changes
   to be made. 

   This "clean up" is part of a bigger analysis of X posts that were obtained from 
   an Apify actor: https://apify.com/apidojo/tweet-scraper.
   The changes are curated for the specific analysis. 
"""

import json 
from additional.professional_cluster import get_profession

def get_author_entities(entities):
     description_urls=[]
     linked_urls=[]

     #get description urls
     description= entities.get("description")
     if description.get("urls"):
        for url in description.get("urls"):
            description_urls.append(url.get("expanded_url"))

     linked=entities.get("url")
     if linked:
          for url in linked.get("urls"):
               linked_urls.append(url.get("expanded_url"))

     return [description_urls, linked_urls]

def extract_author(author):
    profession= get_profession(author.get("professional"))
    entities= get_author_entities(author.get("entities"))

    cleaned_author={
        "userName": author.get("userName"),
        "profile_url": author.get("url"),
        "user_id": author.get("id"),
        "isBlueVerified":author.get("isBlueVerified"),
        "description": author.get("description"),
        "followers": author.get("followers"),
        "following": author.get("following"),
        "createdAt": author.get("createdAt"),
        "description_urls": entities[0],
        "linked_urls": entities[1],
        "favouritesCount": author.get("favouritesCount"),
        "mediaCount": author.get("mediaCount"),
        "statusesCount": author.get("statusesCount"),
        "professional_category": profession[0],
        "professional_type": profession[1]
    }        

    return cleaned_author

#Extract string values with key: description, domain or title from card/legacy/binding_values
def extract_card(card):
    article_description=None
    article_domain=None
    article_title=None

    if card!={}:
        binding_values=card["legacy"]["binding_values"]
        for b_value in binding_values:
            key=b_value.get("key")
            if key=="description":
                article_description=b_value["value"]["string_value"]
            elif key=="domain":
                article_domain=b_value["value"]["string_value"]
            elif key=="title":
                article_title=b_value["value"]["string_value"]

    return {"article_description":article_description,
             "article_domain":article_domain, 
             "article_title":article_title}

def get_media(entities):
    media=[]

    if entities.get("media"):
        for post_media in entities.get("media"):
            media.append(post_media.get("type"))
    return media

def extract_entities(entities, tweet):
    hashtags=[]
    urls=[]
    user_mentions=[]

    #Get the hashtags used in text of the post 
    if entities.get("hashtags"):
        for hashtag in entities["hashtags"]:
            hashtags.append(hashtag.get("text"))

    #Get the number of media used in the post
    if tweet.get("extendedEntities"):
        #only quotes in tweet data have the field of extendedEntities in our dataset
        media=len(get_media(tweet.get("extendedEntities")))
    else:
        media=len(get_media(entities))

    #Get the URLs in the text of the post
    if entities.get("urls"):
        for url in entities["urls"]:
            urls.append(url.get("expanded_url"))

    #Get the user mentions written in the tweeter post
    if entities.get("user_mentions"):
        for mention in entities["user_mentions"]:
            user_mentions.append(mention.get("screen_name"))

    return [hashtags, media, urls, user_mentions]

"""def get_text_and_id(tweet):
    tweet_info= [tweet.get("text"), tweet.get("id")]
    return tweet_info
"""

def clean_tweet(tweet, are_quote_data):  
    entities=extract_entities(tweet.get("entities"), tweet)

    cleaned_tweet={
        "id": tweet.get("id"),
        "text":tweet.get("text"),
        "retweetCount":tweet.get("retweetCount"),
        "replyCount": tweet.get("replyCount"),
        "likeCount": tweet.get("likeCount"),
        "quoteCount": tweet.get("quoteCount"),
        "viewCount": tweet.get("viewCount"),
        "createdAt": tweet.get("createdAt"),
        "bookmarkCount": tweet.get("bookmarkCount"),
        "author" : extract_author(tweet.get("author")),
        "linked_article_values": extract_card(tweet.get("card")),
        "hashtags": entities[0],
        "media": entities[1],
        "urls": entities[2],
        "user_mentions": entities[3]
    }

    #If the data we are handling are not of the quote then we shall include
    # "isReply", "url", "isQuote" fields
    #Otherwise, those fields do not exist in the data of the quotes
    if not are_quote_data:
        cleaned_tweet["isReply"] = tweet.get("isReply")
        if tweet.get("isReply"):
            cleaned_tweet["inReplyToId"]=tweet.get("inReplyToId")
            cleaned_tweet["inReplyToUserId"] = tweet.get("inReplyToUserId")
            cleaned_tweet["inReplyToUsername"] = tweet.get("inReplyToUsername")

        cleaned_tweet["url"] = tweet.get("url")

    # quoted tweet
    cleaned_quote={} #return empty quote if no quote was included
    if tweet.get("isQuote"):
        if "quote" in tweet:
            #we only keep the text and id of the quote as context
            cleaned_tweet["quoted_text"] = tweet.get("quote").get("text")
            cleaned_tweet["quoted_tweet_id"] = tweet.get("quote").get("id")
    
            #quote_info = get_text_and_id(tweet["quote"])

            #keep quote as a SEPARATE tweet
            cleaned_quote = clean_tweet(tweet["quote"], are_quote_data=True)

    if are_quote_data :
        #basically returns only the quote data without the empty dict cleaned_quote 
        return cleaned_tweet 

    return cleaned_tweet, cleaned_quote
