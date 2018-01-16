import sqlite3
import datetime


def db_conn():
    """
    body: contains the actual text of the comment
    created_at: YYYY-MM-DD HH:MM:SS date format
    pos: positive sentiment score
    neu: neutral sentiment score
    neg: negative sentiment score
    """
    conn = sqlite3.connect('reddit_murmur.db')
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS comments
                 (subreddit text, body text, created_at text, pos real , neu real, neg real)'''
    )
    return conn


def unix_to_iso(unix_time):
    """convert unix time to iso"""
    return datetime.datetime.fromtimestamp(
            int(unix_time)).strftime('%Y-%m-%d %H:%M:%S')


def insert_comment(subreddit, comment, conn, analyser):
    sentiment = analyser.polarity_scores(comment.body)
    conn.execute("INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?)",
          (subreddit, comment.body, unix_to_iso(comment.created_utc), sentiment['pos'],
           sentiment['neu'], sentiment['neg']))
    conn.commit()

