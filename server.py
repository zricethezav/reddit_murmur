from flask import Flask, json
from reddit_murmur import Reddit

app = Flask(__name__)


crypto_list = ['ethereum', 'CryptoCurrency', 'cardano', 'politics']
r = Reddit(crypto_list)
r.start_streams()


@app.route("/r/<subreddit>")
def _subreddit(subreddit):
    sr = r.subreddit(subreddit)
    return json.jsonify(
        created_at=sr.created_at,
        comments_total=sr.comments,
        comments_day=sr.comments,
        comments_week=sr.comments,
        comments_hour=sr.comments,
        subscribers_total=sr.subscribers
    )


@app.route("/r/<subreddit>/volume")
def volume(subreddit):
    sr = r.subreddit_doa(subreddit)
    return json.jsonify(volume=sr.volume)


@app.route("/r/<subreddit>/sentiment")
def sentiment(subreddit):
    sr = r.subreddit(subreddit)
    return json.jsonify(sentiment=sr.sentiment)


@app.route("/r/<subreddit>/subscribers")
def subscribers(subreddit):
    sr = r.subreddit(subreddit)
    return json.jsonify(subscribers=sr.subscribers)


@app.route("/r/<subreddit>/add")
def add(subreddit):
    r.add_subreddit(subreddit)
    r.start_stream(subreddit)
    return json.jsonify(
        message='added %s' % subreddit,
        sucess=True
    )


@app.route("/list")
def list_subreddits():
    return json.jsonify(subreddits=[sr.name for sr in r])



if __name__ == "__main__":
    app.run()
