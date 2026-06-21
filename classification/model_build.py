import pandas as pd 
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline

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

#save tweets dataset to a dataframe
all_tweets = pd.read_json("../processed.json") #load tweets to a dataframe
all_tweets, n_labels =get_labels(all_tweets)

#keep only labeled data for training and testing
tweets=all_tweets.head(n_labels)


###########################################################################################################
X_text = tweets["text"]
Y_label = tweets["label"]

#Model 1: Logistic Regression using only TF-IDF of text with n_grams (1,2)

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=5000,
        min_df=3,
        ngram_range=(1,2)
    )),
    ("clf", LogisticRegression(
        max_iter=5000,
        class_weight="balanced"
    ))
])

X_train, X_test, y_train, y_test = train_test_split(
    X_text,
    Y_label,
    test_size=0.2,
    stratify=Y_label,
    random_state=42
)

model.fit(X_train, y_train)
predictions = model.predict(X_test)

print("########################   MODEL 1 #########################\n")
print(classification_report(y_test, predictions))

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

results = cross_validate(
    model,
    X_text,
    Y_label,
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

print("########################   MODEL 2 #########################\n")
#Model 2: Logistic Regression using only TF-IDF of text and linked_article_values


preprocessor = ColumnTransformer(
    transformers=[
        ("tweet_text",
         TfidfVectorizer(max_features=5000),
         "text"),

        ("article_text",
         TfidfVectorizer(max_features=3000),
         "linked_article_values"),
    ]
)

model = Pipeline([
    ("features", preprocessor),
    ("clf", LogisticRegression(
        max_iter=5000,
        class_weight="balanced"
    ))
])

X = tweets[["text", "linked_article_values"]]
y = tweets["label"]

model.fit(X, y)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=Y_label,
    random_state=42
)

model.fit(X_train, y_train)
predictions = model.predict(X_test)

print(classification_report(y_test, predictions))

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