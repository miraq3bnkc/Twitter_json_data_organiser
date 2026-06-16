from graph_structure.network_graph import add_graph_features, create_DiGraph, plot_graph, get_graph_features
from processing.openfiles import load_data,save_file,extract_transform,merge_quotes
from processing.data_transform import replace_username_id, account_age
from processing.feature_engineer import get_n_emojis


path = r"../apify/digital_ids (Copy)" #path that includes the .json files (only) 

tweets=load_data(path)
cleaned_tweets,clean_quotes,users=extract_transform(tweets)
tweets=merge_quotes(clean_quotes,cleaned_tweets)

#Now that we have all the users, let's erase usernames from data
tweets=replace_username_id(tweets,users)

# save all cleaned tweets in file
save_file("merged.json",tweets)
#save users in a file
save_file("users.json",users)


#Create Network graph of user interconnection in the dataset
G=create_DiGraph(users,tweets)
#plot_graph(G,1,12)


features,degrees=get_graph_features(G)

processed_tweets=[]

for tweet in tweets:
    tweet=account_age(tweet)
    
    #Adding graph features
    tweet=add_graph_features(G,tweet,features,degrees)

    #now that graph features are added we transform user_mentions to an integer
    tweet["user_mentions"]=len(tweet.get("user_mentions"))

    tweet=get_n_emojis(tweet)

    processed_tweets.append(tweet)


save_file("processed.json",processed_tweets)
