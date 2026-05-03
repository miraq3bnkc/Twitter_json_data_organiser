from graph_structure.network_graph import create_DiGraph, plot_graph
from processing.openfiles import load_data,save_file,extract_transform,merge_quotes
from processing.data_transform import replace_username_id


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
plot_graph(G,1,12)
