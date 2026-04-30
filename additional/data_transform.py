"""Transforming the raw data extracted from the raw tweet response"""

import json

#Keep only the mentions that are not the default mention by replying to a post
def transform_mentions(reply_username, mentions):
    new_mentions=[]

    for i in range(len(mentions)):
        if mentions[i]!=reply_username:
            new_mentions.append(mentions[i])
    
    return new_mentions

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

def get_user_list(tweets):
    users=[]

    for tweet in tweets:
        user_id=tweet.get("author").get("user_id")

        potential_user = {
            "user_id": user_id,
            "userName": tweet.get("author").get("userName") 
        }

        found=0
        for user in users:
            if user["user_id"]==potential_user["user_id"]:
                found=1
                break
        
        if found==1:
            users.append(potential_user)


    # save user list in a file
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False)
    
