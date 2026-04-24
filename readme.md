# Cleaned Tweet Dataset Structure

This document describes the process of a **cleaning X(formerly Twitter) post data**. 

The cleaning process removes unnecessary metadata from the raw X/Twitter response and irrelevant X posts, keeping only the fields and posts relevant for analysis. Specifically these data were obtained through [Apify](https://apify.com/) actor [🏯 Tweet Scraper V2 - X / Twitter Scraper](https://apify.com/apidojo/tweet-scraper).

---
# Process of Removing Irrelevant Posts (remove_posts.py)

---

## Duplicate and Language Filtering

A preprocessing script was implemented to remove **noisy or irrelevant tweets** from the dataset before further analysis.

The script performs the following cleaning steps:

### 1. Duplicate Removal

Duplicate tweets are removed based on their **unique tweet ID**.

If multiple entries with the same `id` exist, only the **last occurrence** is kept.

This is implemented using a dictionary where the tweet `id` is used as the key:

```
unique_data = {tweet["id"]: tweet for tweet in data}.values()
```

This ensures that the dataset contains **only one instance of each tweet**.

---

### 2. Language Filtering

Tweets that are **not related to the Greek language** are removed.

A tweet is considered valid if at least one of the following conditions is met:

1. **The tweet text contains Greek characters**

The script detects Greek characters using a regular expression:

```
[α-ωΑ-Ω]
```

This captures tweets written in Greek.

---

2. **The tweet links to a Greek domain**

Some tweets may contain only a URL without text.
In these cases, the script checks whether the linked domain ends with:

```
.gr
```

If the link belongs to a Greek domain, the tweet is preserved.

---

### 3. Tweets with no useful context

Some tweets that contain only a URL without text, may also have no additional context from the `url` or the `expanded_ul` making the tweet irrelevant. These kinds of tweets are disregarded. In this category posts with only a photo or video are included, but since we do not make a multi-modal analysis they are deleted. 

---

### 4. Manual Review of Uncertain Cases

If a tweet:

* does not contain Greek characters
* does not link to a `.gr` domain
* but `url` or `expanded_url` are not empty

the script **prompts the user for manual confirmation** before deletion.

The following information is displayed:

* Tweet text
* Tweet URL
* Referenced URL

The user can then choose whether to keep or delete the tweet.

Example prompt:

```
--- POSSIBLE NON-GREEK TWEET ---
Text: ...
Tweet URL: ...
Referenced URL: ...

Delete this tweet? (y/n)
```

This step ensures that **tweets with Greek context are not mistakenly removed**.
This step was firstly included for Greeklish representations, but since only one post was found with this representation, it was deemed an unnecessary check.
---

### Result

After applying this script:

* Duplicate tweets are removed
* Non-Greek tweets are filtered
* Tweets with no useful context are removed
* Ambiguous cases are manually reviewed

This produces a **cleaner dataset focused on Greek-language content**, which is required for our task.

---
# Process of Cleaning Post Metadata (remove_fields.py)
## Example Cleaned Tweet

```json
{
  "id": "post id",
  "text": "post text",
  "retweetCount": 0,
  "replyCount": 0,
  "likeCount": 0,
  "quoteCount": 0,
  "viewCount": 58,
  "bookmarkCount": 0,
  "createdAt": "Thu Mar 27 15:50:14 +0000 2025",
  "isReply": false,
  "author": {
    "userName": "string",
    "profile_url": "url",
    "user_id": "user id",
    "isBlueVerified": false,
    "description": "text",
    "followers": 22939,
    "following": 2054,
    "createdAt": "Sat Dec 19 13:38:54 +0000 2009",
    "description_urls": ["http://facebook.com/example"],
    "linked_urls": ["http://example.com"],
    "favouritesCount": 98,
    "mediaCount": 259429,
    "statusesCount": 414885,
    "professional_category": "Journalist",
    "professional_type": "Creator"
  },
  "linked_article_values": {
    "article_description": "text",
    "article_domain": "www.example.com",
    "article_title": "text"
  },
  "hashtags": ["hashtag1", "hashtag2"],
  "media": integer,
  "urls": ["expanded_url1", "expanded_url2"],
  "user_mentions": ["username1", "username2"],
  "isQuote": false,
  "isConversationControlled": false
}
```

---

## Reply Information

If `"isReply": true`, the following fields are included:

```
"inReplyToId": "post id"
"inReplyToUserId": "user id"
"inReplyToUsername" "username string"
```

These fields identify the **tweet and user being replied to**.

---

## Author Information

The `"author"` object contains metadata about the user that posted the tweet.

| Field           | Description                     |
| --------------- | ------------------------------- |
| userName        | Twitter/X username              |
| profile_url     | Profile URL                     |
| id              | Unique user ID                  |
| isBlueVerified  | Whether the account is verified |
| description     | Profile biography               |
| followers       | Number of followers             |
| following       | Number of accounts followed     |
| createdAt       | Account creation date           |
| favouritesCount | Total likes by the user         |
| mediaCount      | Total media posted              |
| statusesCount   | Total tweets posted             |

Additional fields extracted from the raw API:

| Field                 | Description                              | Extracted from original API response   |
| --------------------- | ---------------------------------------- | -------------------------------------- |
| description_urls      | URLs found in the profile description    | entities.description.urls.expanded_url |
| linked_urls           | External URLs listed in the profile      | entities.url.urls.expanded_url         |
| professional_category | Professional category (e.g. Journalist)  | professional.category.name             |
| professional_type     | Professional account type (e.g. Creator) | professional.professional_type         |

---

## Linked Article Information

If a tweet contains a **link preview card**, metadata is extracted and stored under:

```
linked_article_values
```

Fields include:

| Field               | Description                  |
| ------------------- | ---------------------------- |
| article_title       | Title of the linked article  |
| article_description | Article preview description  |
| article_domain      | Domain of the linked website |

These values are extracted from the `card` object in the raw tweet response.

---

## Entities Field

The `entities` object contains structured elements present in the tweet.

| Field         | Description                               
|
| ------------- | ----------------------------------------- |
| hashtags      | List of hashtags used                     |
| media         | number of media attachments (photo/video) |
| urls          | External links                            |
| user_mentions | Mentioned usernames                       |

---

## Entities Cleaning Process

The raw Twitter API response contains extensive metadata that is removed during preprocessing.

For example:

### Raw Entities Object

```json
"entities": {
    "hashtags": [
        {
            "indices": [
                143,
                162
            ],
            "text": "someHashtags"
        },
        {
            "indices": [
                218,
                229
            ],
            "text": "someOtherHashtag"
        }
    ],
    "media": [ 
        {
            "display_url": "https://example.com",
            "expanded_url": "https://example.com",
            "ext_media_availability": {
                "status": "Available"
            },
            "features": { ... },
            "id_str": "various numbers",
            "indices": [
                274,
                297
            ],
            "media_key": "various numbers",
            "media_results": { ... },
            "media_url_https": "https://example.com",
            "original_info": { ... },
            "sizes": { ... },
            "type": "video",
            "url": "https://example.com"
        },
        {
            "display_url": "https://example.com",
            "expanded_url": "https://example.com",
            "ext_media_availability": {
                "status": "Available"
            },
            "features": { ... },
            "id_str": "various numbers",
            "indices": [
                274,
                297
            ],
            "media_key": "various numbers",
            "media_results": { ... },
            "media_url_https": "https://example.com",
            "original_info": { ... },
            "sizes": { ... },
            "type": "photo",
            "url": "https://example.com"
        }
    ],
    "symbols": [],
    "timestamps": [],
    "urls": [
        {
            "display_url": "example.com",
            "expanded_url": "https://example.com",
            "indices": [
                119,
                142
            ],
            "url": "https://t.co/code"
        }
    ],
    "user_mentions": [
        {
            "id_str": "various numbers",
            "indices": [
                6,
                22
            ],
            "name": "name in greek letters",
            "screen_name": "someScreenName"
        },
        {
            "id_str": "1458387965395230724",
            "indices": [
                23,
                34
            ],
            "name": "name",
            "screen_name": "someScreenName2"
        }
    ]
},
```

After cleaning:

```json
"entities": {
  "hashtags": ["someHashtags","someOtherHashtag"],
  "media": 2,
  "urls": ["https://example.com"],
  "user_mentions": ["someScreenName","someScreenName2"]
}
```


Only the **number of media type, hashtag name, urls expanded_url** and **user mentions screen_name** is preserved.

---

## Removed Fields

Some fields were removed because they were either unused or always empty in the dataset.

Removed fields include:

```
symbols
timestamps
```

These were consistently empty across the collected tweets.

---

## Quote and Retweet Handling

### Quoted Tweets

If `"isQuote": true`, the quoted tweet originally appears under:

```
"quote": { ... }
```

It was decided to separate the original tweet from the quote. So, the tweet that quotes another tweet will have the additional fetures:

```
"quoted_text": text
"quoted_tweet_id": id
```
And the quoted tweet will appear as a separate tweet (unless it appear irrelevant, or it is not in Greek)

This object contains the **same structure as a normal tweet**.

Note:

1. Quoted tweets **do not contain** the following fields:

```
url
isReply
isQuote
```
2. **Media** info are only contained under **extendedEntities**, which we can extract `"type"` the same way as before in **entities**.

---

### Retweets

The field `"isRetweet"` exists in the raw API response.

However, in this dataset:

```
isRetweet was never observed as true
```

Therefore this field was removed from the cleaned dataset.

---

# Dataset Observations

### Dataset Characteristics

Observations from the collected dataset:

* No retweets were observed.
* Some tweets contain article preview cards.
* Media objects may appear in `entities` or `extendedEntities`.

---
# Final Process (openfiles.py)

After removing unnecessary fields and posts, the .json files are merged into one file and sorted according to the latest creation time of the post. 