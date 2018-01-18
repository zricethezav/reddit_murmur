import sqlite3
import datetime
import copy


def db_conn():
    """returns db conn"""
    conn = sqlite3.connect('reddit_murmur.db')
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS comments
                 (subreddit text, body text, created_at text, pos real , neu real, neg real)'''
    )
    return conn


def unix_to_iso(unix_time):
    """returns iso formatted timestamp"""
    return datetime.datetime.fromtimestamp(
            int(unix_time)).strftime('%Y-%m-%d %H:%M:%S')


def insert_comment(subreddit, comment, conn, analyser):
    """insert comment body and sentiment into db"""
    sentiment = analyser.polarity_scores(comment.body)
    conn.execute("INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?)",
          (subreddit, comment.body, unix_to_iso(comment.created_utc), sentiment['pos'],
           sentiment['neu'], sentiment['neg']))
    conn.commit()

def intervals(start, end, delta):
    """time interval strings for query, returns tuple"""
    intervals = []
    current = copy.deepcopy(start)
    while current < end:
        intervals.append((unix_to_iso(current.strftime('%s')),
                          unix_to_iso((current + delta).strftime('%s'))))
        current += delta
    return intervals
