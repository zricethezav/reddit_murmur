# Reddit Murmur
## Reddit Things.

#### Features:
 * Store reddit comment text
 * Web server to query reddit comments
 * Ipython notebook example in `scripts/`

#### Installing:
Set reddit env vars in current shell or bashrc/profile
```
export REDDIT_MURMUR_PG_USER
export REDDIT_MURMUR_PG_PW
export REDDIT_MURMUR_DB
export REDDIT_CLIENT
export REDDIT_SECRET
export REDDIT_USERNAME
export REDDIT_PASSWORD
```
Create reddit database and reddit user. Sample install script in `scripts/postgres.sh`

Once Postgres is all setup: `pip install -e .`


### Usage: 

##### Gathering Comments

```
from reddit_murmur import reddit_murmur as rm
import matplotlib.pyplot as plt

subreddit_labels=['pics', 'politics']
r = rm.Reddit(subreddit_labels)

# NOTE: streams will run as long as reddit object is in context
import time
r.start_streams()

while True:
	# gather comments
	time.sleep(1)
```
##### Querying Comments
```
from reddit_murmur import reddit_murmur as rm

subreddit_labels=['pics', 'politics']
r = rm.Reddit(subreddit_labels)

pics_subreddit_dao = r.subreddits_dao['pics']

# traffic timeseries options: 15m, 30m, 1hr, 1d, 1wk 
pics_timeseries = pics_subreddit_dao.traffic_timeseries('15m')

# plot timeseries
time_x = [pics_timeseries['start'] + datetime.timedelta(
    seconds=i * pics_timeseries['delta'].seconds) for i in range(pics_timeseries['intervals'])]
comments_y = pics_timeseries['timeseries']
plt.plot(time_x, comments_y)
plt.ylabel('comments')
plt.xlabel('time (utc)')
plt.gcf().autofmt_xdate()
plt.show()
```

##### API
start server
```
$ python reddit_murmur/server.py
```
GET
* `/list` list of subreddits being monitored 
* `/r/<subreddit>/add` add subreddit to monitor

TODO:
* finish out API
