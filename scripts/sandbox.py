from reddit_murmur import reddit_murmur as rm

subreddit_labels = ['ethereum', 'CryptoCurrency', 'cardano', 'politics']
r = rm.Reddit(subreddit_labels)
r.start_streams(keep_alive=True)
