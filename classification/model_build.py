from matplotlib import pyplot as plt
import numpy as np
import pandas as pd 
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, classification_report
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from time import time
from collections import Counter
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

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
    classifier=None,
    use_text=True,
    use_article=False,
    use_quote=False,
    use_text_metadata=False,
    use_engagement=False,
    use_user=False,
    use_network=False
):
    transformers = []
    if classifier is None:
        classifier = LogisticRegression(
            max_iter=5000,
            class_weight="balanced"
        )

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
        ("clf", classifier)
    ])

def ablation(configs):
    results = []
    models = {}

    for cfg in configs:
        print(f"\nRunning: {cfg['name']}")

        model = build_model(
            use_text=cfg["use_text"],
            use_article=cfg["use_article"],
            use_quote=cfg["use_quote"],
            use_text_metadata=cfg["use_text_metadata"],
            use_engagement=cfg["use_engagement"],
            use_user=cfg["use_user"],
            use_network=cfg["use_network"],
        )

        scores = get_results(model)  # ideally return metrics instead of printing

        results.append({
            "model": cfg["name"],
            **scores
        })
        models[cfg["name"]]=model

    return results,models

def get_results(model):
    #print(classification_report(y_test, predictions))


    start = time()
    results = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring={
            "accuracy": "accuracy",
            "f1": "f1_macro",
            "precision": "precision_macro",
            "recall": "recall_macro"
        },
        n_jobs=-1
    )
    print("5-Fold Cross Validation time : ",time() - start)

    return {
        "accuracy_mean" : results["test_accuracy"].mean(), 
        "f1_mean": results["test_f1"].mean(),
        "f1_std": results["test_f1"].std(),
        "precision_mean": results["test_precision"].mean(),
        "recall_mean": results["test_recall"].mean(),
        }




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


ablation_configs = [
    {"name": "text_only", "use_text": True, "use_article": False, "use_quote": False, "use_text_metadata": False, "use_engagement": False, "use_user": False, "use_network": False},
    {"name": "text_meta", "use_text": True, "use_article": False, "use_quote": False, "use_text_metadata": True, "use_engagement": False, "use_user": False, "use_network": False},
    {"name": "text_article", "use_text": True, "use_article": True, "use_quote": False, "use_text_metadata": False, "use_engagement": False, "use_user": False, "use_network": False},
    {"name": "text_article_quote", "use_text": True, "use_article": True, "use_quote": True, "use_text_metadata": False, "use_engagement": False, "use_user": False, "use_network": False},
    {"name": "text_all", "use_text": True, "use_article": True, "use_quote": True, "use_text_metadata": True, "use_engagement": False, "use_user": False, "use_network": False},    
    {"name": "text_user", "use_text": True, "use_article": False, "use_quote": False, "use_text_metadata": False, "use_engagement": False, "use_user": True, "use_network": False},
    {"name": "text_network", "use_text": True, "use_article": False, "use_quote": False, "use_text_metadata": False, "use_engagement": False, "use_user": False, "use_network": True},
    {"name": "text_user_network_engagement", "use_text": True, "use_article": False, "use_quote": False, "use_text_metadata": False, "use_engagement": True, "use_user": True, "use_network": True},    
    {"name": "without_meta", "use_text": True, "use_article": True, "use_quote": True, "use_text_metadata": False, "use_engagement": True, "use_user": True, "use_network": True},
    {"name": "without_texts", "use_text": False, "use_article": False, "use_quote": False, "use_text_metadata": True, "use_engagement": True, "use_user": True, "use_network": True},
    {"name": "full", "use_text": True, "use_article": True, "use_quote": True, "use_text_metadata": True, "use_engagement": True, "use_user": True, "use_network": True},
]


cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

results,models = ablation(ablation_configs)

df = pd.DataFrame(results)
print(df)


#Get all the coefficients in the full model
models["full"].fit(X, y)

clf = models["full"].named_steps["clf"]
feature_names = models["full"].named_steps["features"].get_feature_names_out()
importance = np.mean(np.abs(clf.coef_), axis=0)

coef_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importance
}).sort_values("importance", ascending=False)

coef_df.to_csv("feature_importance.csv", index=False)


#Use the best model for comparisons with other models
comparisons=[ results[3]]

print("\nRunning: Linear Support Vector Classification")
linear = build_model(
    classifier=LinearSVC(
        class_weight="balanced",
        max_iter=5000
    ),
    use_text=True,
    use_article=True,
    use_quote=True
)

comparisons.append({"model":"linearSVC",**get_results(linear)})

print("\nRunning: Multinomial Naive Bayes")
Naive_bayes = build_model(
    classifier=MultinomialNB(),
    use_text=True,
    use_article=True,
    use_quote=True
)

comparisons.append({"model":"Naive Bayes",**get_results(Naive_bayes)})

y_pred = cross_val_predict(Naive_bayes, X, y, cv=cv)
print(Counter(y_pred))

print("\nRunning: Random Forest")
Rforest = build_model(
    classifier= RandomForestClassifier(),
    use_text=True,
    use_article=True,
    use_quote=True
)
comparisons.append({"model":"Random Forest",**get_results(Rforest)})

print("\n\nRESULTS\n\n")
df = pd.DataFrame(comparisons)
print(df)

models = df["model"]
f1 = df["f1_mean"]

plt.figure(figsize=(6,4))
plt.bar(models, f1, color="steelblue")

plt.title("Model comparison (Macro F1)")
plt.ylabel("Macro F1")
plt.ylim(0, 1)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

#Now that we have found our best model lets get more info
y_pred = cross_val_predict(
    linear,
    X,
    y,
    cv=cv,
    n_jobs=-1
)

print("\n\nClassification report\n\n",classification_report(y, y_pred))

disp = ConfusionMatrixDisplay.from_predictions(y, y_pred, cmap="Blues")
plt.title("LinearSVC Confusion Matrix (CV Predictions)")
plt.tight_layout()
plt.show()


"""Added deleted hyperparameter experiment for reproducability"""

#Use the best model for comparisons with other models
hyperparameter_comp=[ results[3]]

saga= build_model(
    classifier=LogisticRegression(
        solver="saga",
        class_weight="balanced",
        max_iter=5000,
    ),
    use_text=True,
    use_article=True,
    use_quote=True
)

hyperparameter_comp.append({"model":"saga",**get_results(saga)})

lbfgs_10 = build_model(
    classifier=LogisticRegression(
        class_weight="balanced",
        C=0.1,
        max_iter=5000,
    ),
    use_text=True,
    use_article=True,
    use_quote=True
)

hyperparameter_comp.append({"model":"lbfgs_10",**get_results(lbfgs_10)})

saga_10 = build_model(
    classifier=LogisticRegression(
        class_weight="balanced",
        solver="saga",
        C=0.1,
        max_iter=5000,
    ),
    use_text=True,
    use_article=True,
    use_quote=True
)
hyperparameter_comp.append({"model":"saga_10",**get_results(saga_10)})

print("\n\nRESULTS\n\n")
df = pd.DataFrame(hyperparameter_comp)
print(df)
