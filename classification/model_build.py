import pandas as pd 
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from time import time

from sklearn.preprocessing import StandardScaler

#Add LABELS
def get_labels(tweets):
    with open("../../apify/labels.txt", "r", encoding="utf-8") as f:
        #loading labels , and dealing with trailing empty lines
        labels = [line.strip() for line in f]

    #We do not have labels for all the posts in our dataset
    #We will fill the unlabeled posts with None
    labeled=len(labels)
    unlabeled= len(tweets)-labeled #number of unlabeled posts
    none_labels=[None]*unlabeled #list with None labels
    labels.extend(none_labels) #add None for the unlabeled to the labels

    tweets['label']=labels

    return tweets, labeled

def build_model(
    use_text=True,
    use_article=False,
    use_quote=False,
    use_text_metadata=False,
    use_engagement=False,
    use_user=False,
    use_network=False
):
    transformers = []

    if use_text:
        transformers.append(
            ("text",
             TfidfVectorizer(max_features=5000),
                "text")
        )

    if use_article:
        transformers.append(
            ("article",
             TfidfVectorizer(max_features=3000),
             "linked_article_values")
        )

    if use_quote:
        transformers.append(
            ("quote",
             TfidfVectorizer(max_features=2000),
             "quoted_text")
        )

    numeric_cols = []
    bool_cols=[]
    if use_text_metadata:
        numeric_cols += text_numeric
        bool_cols+=text_bool
    if use_engagement:
        numeric_cols += ENGAGEMENT

    if use_user:
        numeric_cols += USER
        bool_cols += user_bool

    if use_network:
        numeric_cols += NETWORK

    if numeric_cols:
        transformers.append(
            ("numeric",
             StandardScaler(with_mean=False),
             numeric_cols))
    if bool_cols:
        transformers.append(
             ("boolean",
             "passthrough",
             bool_cols)
        )

    preprocessor = ColumnTransformer(transformers)

    return Pipeline([
        ("features", preprocessor),
        ("clf", LogisticRegression(
            max_iter=5000,
            class_weight="balanced"
        ))
    ])


def print_results(model):
    #print(classification_report(y_test, predictions))

    results = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring={
            "f1": "f1_macro",
            "precision": "precision_macro",
            "recall": "recall_macro"
        }
    )

    for metric in ["test_f1", "test_precision", "test_recall"]:
        print(f"{metric}:")
        print(f"  Scores: {results[metric]}")
        print(f"  Mean:   {results[metric].mean():.4f}")
        print(f"  Std:    {results[metric].std():.4f}")
        print()





#save tweets dataset to a dataframe
all_tweets = pd.read_json("../processed.json") #load tweets to a dataframe
all_tweets, n_labels =get_labels(all_tweets)

#keep only labeled data for training and testing
tweets=all_tweets.head(n_labels)
tweets=tweets.drop(columns=["raw_activity"]) #it was only kept fro reference not for the model


X = tweets.drop(columns=["label"])
y = tweets["label"]

#54 different columns
TEXT_FEATURES = ["text"]
ARTICLE_FEATURES = ["linked_article_text"]
#TEXT_METADATA 
text_numeric=["hashtags","media","urls","user_mentions",
                 "n_emojis","capital_ratio",
                 "question_marks","exclamation_marks","n_chars",
                 "n_words","emoji_vaccine_count","emoji_id_count",
                 "emoji_ridicule_count","emoji_alert_count",
                 "emoji_direction_count","emoji_hostility_count",
                 "emoji_identity_count","emoji_thinking_count",
                 "emoji_support_count","emoji_smugness_count",
                 "emoji_negative_count"]
text_bool=["isReply","isQuote"]
ENGAGEMENT = ["retweetCount", "replyCount","likeCount",
              "quoteCount","viewCount","bookmarkCount","engagement_rate"]
USER = ["followers", "following",
        "favouritesCount","mediaCount","statusesCount",
        "professional_info", "account_age_days",
        "followers_following_ratio","activity","media_ratio"]
user_bool=["isBlueVerified"]
NETWORK = ["betweenness","pagerank", "clustering", 
           "core","indeg","outdeg", 
           "weighted_indeg","weighted_outdeg"]
network_bool=["has_selfloop"]
QUOTE = ["quoted_text"]


#
#X_train, X_test, y_train, y_test = train_test_split(
#    X,
#    y,
#    test_size=0.2,
#    stratify=y,
#    random_state=42
#)

cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )


print("########################   MODEL 1 #########################\n")
model1 = build_model(
    use_text=False,
    use_text_metadata=True
)
#model1.fit(X_train, y_train)
#predictions1 = model1.predict(X_test)
start = time()
results = cross_validate(
    model1,
    X,
    y,
    cv=cv,
    scoring={
        "f1": "f1_macro",
        "precision": "precision_macro",
        "recall": "recall_macro"
    },
    n_jobs=-1
)

for metric in ["test_f1", "test_precision", "test_recall"]:
    print(f"{metric}:")
    print(f"  Scores: {results[metric]}")
    print(f"  Mean:   {results[metric].mean():.4f}")
    print(f"  Std:    {results[metric].std():.4f}")
    print()

print(time() - start)

print("########################   MODEL 2 #########################\n")
model2 = build_model(
    use_text=True
)
#model2.fit(X_train, y_train)
#predictions2 = model2.predict(X_test)
start = time()
results = cross_validate(
    model2,
    X,
    y,
    cv=cv,
    scoring={
        "f1": "f1_macro",
        "precision": "precision_macro",
        "recall": "recall_macro"
    },
    n_jobs=-1
)

for metric in ["test_f1", "test_precision", "test_recall"]:
    print(f"{metric}:")
    print(f"  Scores: {results[metric]}")
    print(f"  Mean:   {results[metric].mean():.4f}")
    print(f"  Std:    {results[metric].std():.4f}")
    print()

print(time() - start)

print("########################   MODEL 3 #########################\n")
model3 = build_model(
    use_text=True,
    use_text_metadata=True
)
#model3.fit(X_train, y_train)
#predictions3 = model3.predict(X_test)
start = time()
results = cross_validate(
    model3,
    X,
    y,
    cv=cv,
    scoring={
        "f1": "f1_macro",
        "precision": "precision_macro",
        "recall": "recall_macro"
    },
    n_jobs=-1
)

for metric in ["test_f1", "test_precision", "test_recall"]:
    print(f"{metric}:")
    print(f"  Scores: {results[metric]}")
    print(f"  Mean:   {results[metric].mean():.4f}")
    print(f"  Std:    {results[metric].std():.4f}")
    print()


print(time() - start)


print("########################   MODEL 4 #########################\n")
model4 = build_model( 
    use_text=True,
    use_article=True
    )
#model3.fit(X_train, y_train)
#predictions3 = model3.predict(X_test)
start = time()
results = cross_validate(
    model4,
    X,
    y,
    cv=cv,
    scoring={
        "f1": "f1_macro",
        "precision": "precision_macro",
        "recall": "recall_macro"
    },
    n_jobs=-1
)

for metric in ["test_f1", "test_precision", "test_recall"]:
    print(f"{metric}:")
    print(f"  Scores: {results[metric]}")
    print(f"  Mean:   {results[metric].mean():.4f}")
    print(f"  Std:    {results[metric].std():.4f}")
    print()


print(time() - start)

print("########################   MODEL 5 #########################\n")
model5 = build_model(
    use_text=True,
    use_article=True,
    use_text_metadata=True
)
#model3.fit(X_train, y_train)
#predictions3 = model3.predict(X_test)
start = time()
results = cross_validate(
    model5,
    X,
    y,
    cv=cv,
    scoring={
        "f1": "f1_macro",
        "precision": "precision_macro",
        "recall": "recall_macro"
    },
    n_jobs=-1
)

for metric in ["test_f1", "test_precision", "test_recall"]:
    print(f"{metric}:")
    print(f"  Scores: {results[metric]}")
    print(f"  Mean:   {results[metric].mean():.4f}")
    print(f"  Std:    {results[metric].std():.4f}")
    print()


print(time() - start)

print("########################   MODEL 6  #########################\n")
model6 = build_model(
    use_text=True,
    use_engagement=True
)
#model3.fit(X_train, y_train)
#predictions3 = model3.predict(X_test)
start = time()
results = cross_validate(
    model6,
    X,
    y,
    cv=cv,
    scoring={
        "f1": "f1_macro",
        "precision": "precision_macro",
        "recall": "recall_macro"
    },
    n_jobs=-1
)

for metric in ["test_f1", "test_precision", "test_recall"]:
    print(f"{metric}:")
    print(f"  Scores: {results[metric]}")
    print(f"  Mean:   {results[metric].mean():.4f}")
    print(f"  Std:    {results[metric].std():.4f}")
    print()


print(time() - start)