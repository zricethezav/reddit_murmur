import datetime
import copy
import psycopg2
import settings


def db_conn():
    """returns db conn"""

    conn = psycopg2.connect(
        'dbname=%s user=%s password=%s' % (settings.PG_DB,
            settings.PG_USER, settings.PG_PW)
    )
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS comments
                 (id text PRIMARY KEY, subreddit text, body text, created_at text, pos real , neu real, neg real)'''
    )
    conn.commit()
    cur.close()
    return conn


def unix_to_iso(unix_time):
    """returns iso formatted timestamp"""
    return datetime.datetime.fromtimestamp(
            int(unix_time)).strftime('%Y-%m-%d %H:%M:%S')


def insert_comment(subreddit, comment, conn, analyser):
    """insert comment body and sentiment into db"""
    sentiment = analyser.polarity_scores(comment.body)
    cur = conn.cursor()
    cur.execute("INSERT INTO comments VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
          (comment.id, subreddit, comment.body, unix_to_iso(comment.created_utc), sentiment['pos'],
           sentiment['neu'], sentiment['neg']))
    conn.commit()
    cur.close()


def intervals(start, end, delta):
    """time interval strings for query, returns tuple"""
    intervals = []
    current = copy.deepcopy(start)
    while current < end:
        intervals.append((unix_to_iso(current.strftime('%s')),
                          unix_to_iso((current + delta).strftime('%s'))))
        current += delta
    return intervals
