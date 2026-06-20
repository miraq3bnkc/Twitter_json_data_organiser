import pandas as pd 


tweets = pd.read_json("../processed.json") #load tweets to a dataframe
print(tweets.iloc[10])