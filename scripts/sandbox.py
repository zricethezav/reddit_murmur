from reddit_murmur import reddit_murmur as rm
import time

subreddit_labels = ['ethereum', 'CryptoCurrency', 'cardano', 'politics']
r = rm.Reddit(subreddit_labels)
r.start_streams()

"""
while True:
    time.sleep(1)
    for sr in r.subreddits.values():
        print sr.comments
"""

p = r.subreddits_dao['politics']
print p.traffic_timeseries('1d')
sr = r.subreddits['politics']




