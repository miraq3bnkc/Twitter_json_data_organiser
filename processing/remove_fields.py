"""This python script is created for the purposes of "cleaning" the .json data
   that contain information about X.com posts. 
   Specifically it will remove unnecessary fields and change/rename some other fields.
   This will all be according to the readme file were you can see the changes
   to be made. 

   This "clean up" is part of a bigger analysis of X posts that were obtained from 
   an Apify actor: https://apify.com/apidojo/tweet-scraper.
   The changes are curated for the specific analysis. 
"""
from processing.data_transform import transform_mentions, text_cleanup
from processing.feature_engineer import account_age

"""Profession Data not included after all
These metadata were defined only on 19.5% of our dataset.
Most of this values were user defined, so the categories were inconsistent
Instead, a simplified binary indicator denoting the presence of professional 
account metadata was retained.
"""
def get_profession(professional):
    #initialization
    professional_category=None
    professional_type=None

    #change values only if they exist in .json 
    if professional:
        professional_type = professional.get("professional_type")
        if professional.get("category"):
             professional_category = professional["category"][0]["name"]

    #Defining and returning binary indicator 
    if professional_category or professional_type:
        return 1  
    else:
        return 0
            
def extract_author(author):
    profession= get_profession(author.get("professional"))

    cleaned_author={
        "user_id": author.get("id"),
        "isBlueVerified":author.get("isBlueVerified"),
        "followers": author.get("followers"),
        "following": author.get("following"),
        "account_age_days": account_age(author.get("createdAt")),
        "favouritesCount": author.get("favouritesCount"),
        "mediaCount": author.get("mediaCount"),
        "statusesCount": author.get("statusesCount"),
        "professional_info": profession
    }        
    
    #needed for creation of user list
    user_info=[author.get("userName"), author.get("id")]

    return cleaned_author,user_info

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
    
    #concatenate the title with the description of the link
    article_text=[ article_title, article_description ]

    if article_description or article_title:
        linked_article_info = '\n'.join(filter(None,article_text))
    else:
        linked_article_info = ""

    return linked_article_info, article_domain

def get_media(entities):
    media=0
    if entities.get("media"):
        media= len(entities.get("media"))
    
    return media

def extract_entities(entities, tweet):
    hashtags=0
    urls=[]
    user_mentions=[]

    #Get the hashtags used in text of the post 
    if entities.get("hashtags"):
        for hashtag in entities["hashtags"]:
            hashtags=len(hashtag)

    #Get the number of media used in the post
    if tweet.get("extendedEntities"):
        #only quotes in tweet data have the field of extendedEntities in our dataset
        media=get_media(tweet.get("extendedEntities"))
    else:
        media=get_media(entities)

    #Get the URLs in the text of the post
    if entities.get("urls"):
        for url in entities["urls"]:
            urls.append(url.get("expanded_url"))

    #Get the user mentions written in the tweeter post
    if entities.get("user_mentions"):
        for mention in entities["user_mentions"]:
            user_mentions.append(mention.get("screen_name"))

    return [hashtags, media, urls, user_mentions]

def clean_tweet(tweet, are_quote_data):  
    entities=extract_entities(tweet.get("entities"), tweet)
    linked_info, article_domain = extract_card(tweet.get("card"))
    author_element,user_info=extract_author(tweet.get("author"))

    """UNUSED FEATURE -- WE ONLY KEPT NUMBER OF URLS
    #If article domain exists then transform urls if needed
    if article_domain:
        entities[2]=transform_urls(article_domain,entities[2])
    """
    
    cleaned_tweet={
        "id": tweet.get("id"),
        "text": text_cleanup(tweet.get("text"),entities,True),
        "retweetCount":tweet.get("retweetCount"),
        "replyCount": tweet.get("replyCount"),
        "likeCount": tweet.get("likeCount"),
        "quoteCount": tweet.get("quoteCount"),
        "viewCount": tweet.get("viewCount",0),
        "createdAt": tweet.get("createdAt"),
        "bookmarkCount": tweet.get("bookmarkCount"),
        "linked_article_values": text_cleanup(linked_info,entities,False),
        "hashtags": entities[0],
        "media": entities[1],
        "urls": len(entities[2]),
        "user_mentions": entities[3],
        "isReply": tweet.get("isReply",False),
        "isQuote": tweet.get("isQuote",False)
    }

    cleaned_tweet.update(author_element)

    #If the data we are handling are not of the quote then we shall include
    # "isReply" fields
    #since reply fields do not exist in quote data
    if not are_quote_data:
        if tweet.get("isReply"):
            cleaned_tweet["inReplyToId"]=tweet.get("inReplyToId")
            cleaned_tweet["inReplyToUserId"] = tweet.get("inReplyToUserId")

            #Update mentions list if needed
            cleaned_tweet["user_mentions"]=transform_mentions(tweet.get("inReplyToUsername"),cleaned_tweet["user_mentions"])

    # quoted tweet
    cleaned_quote={} #return empty quote if no quote was included
    quote_user=[]
    if tweet.get("isQuote"):
        if "quote" in tweet:    
            #keep quote as a SEPARATE tweet
            #for quotes, isReply and isQuotes are undefined , so they have a False label
            cleaned_quote,quote_user = clean_tweet(tweet["quote"], are_quote_data=True)

            #we only keep the text and id of the quote as context
            cleaned_tweet["quoted_text"] = cleaned_quote.get("text")
            cleaned_tweet["quoted_tweet_id"] = tweet.get("quote").get("id")
            cleaned_tweet["quoted_user_id"] = tweet.get("quote").get("author").get("id")
            #add in number of media of the post also the number of media from the quote
            cleaned_tweet["media"]+=cleaned_quote.get("media")
    else:
        cleaned_tweet["quoted_text"]=""

    if are_quote_data :
        #basically returns only the quote data and user_info 
        #without the empty dict cleaned_quote and quote_user
        #those will be filled after the return
        return cleaned_tweet , user_info

    return cleaned_tweet, user_info, cleaned_quote, quote_user
