"""This python script is created for the purposes of "cleaning" the .json data
   that contain information about X.com posts. 
   Specifically it will remove unnecessary fields and change/rename some other fields.
   This will all be according to the readme file were you can see the changes
   to be made. 

   This "clean up" is part of a bigger analysis of X posts that were obtained from 
   an Apify actor: https://apify.com/apidojo/tweet-scraper.
   The changes are curated for the specific analysis. 
"""

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
        "professional_info": profession
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
             "article_title":article_title}, article_domain

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


def clean_tweet(tweet, are_quote_data):  
    entities=extract_entities(tweet.get("entities"), tweet)
    linked_info, article_domain = extract_card(tweet.get("card"))

    if article_domain:
        entities[2]=transform_urls(article_domain,entities[2])

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
        "linked_article_values": linked_info,
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
