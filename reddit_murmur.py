import os
import praw
from threading import Thread
import utils
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import datetime

REDDIT_CLIENT = os.getenv('REDDIT_CLIENT')
REDDIT_SECRET = os.getenv('REDDIT_SECRET')
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')

reddit_client = praw.Reddit(
        client_id=REDDIT_CLIENT,
        client_secret=REDDIT_SECRET,
        password=REDDIT_PASSWORD,
        username=REDDIT_USERNAME,
        user_agent='hype-stream by /u/pr0tocol_7')


class Reddit(object):
    """parent for subreddit threads. holds db conn for data access"""
    def __init__(self, subreddit_names):
        self.num_active_threads = 0
        self.subreddit_names = subreddit_names
        self.subreddits = {}
        self.subreddits_dao = {}
        self.index = 0
        self.conn = utils.db_conn()
        for _subreddit in subreddit_names:
            self.add_subreddit(_subreddit)

    def __getitem__(self, index):
        result = self.subreddits.values()[index]
        return result

    def subreddit_dao(self, subreddit_name):
        return self.subreddits_dao.get(subreddit_name)

    def subreddit(self, subreddit_name):
        return self.subreddits.get(subreddit_name)

    def add_subreddit(self, subreddit_name):
        self.subreddits[subreddit_name] = SubReddit(subreddit_name)
        self.subreddits_dao[subreddit_name] = SubRedditDAO(self.conn, subreddit_name)

    def start_stream(self, subreddit_name):
        self.subreddits[subreddit_name].setDaemon(True)
        self.subreddits[subreddit_name].start()

    def start_streams(self):
        for subreddit in self.subreddits.values():
            if not subreddit.streaming:
                subreddit.setDaemon(True)
                subreddit.start()

    def kill_subreddit(self, subreddit_name):
        self.subreddits[subreddit_name].kill()
        del self.subreddits[subreddit_name]

    def __del__(self):
        for sr in self.subreddits.values():
            sr.kill()


class SubReddit(Thread):
    """SubReddit needs to monitor comment growth, subscriber growth, sentiment score at different durations"""
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name
        self.comments = 0
        self.conn = None
        self.subreddit = reddit_client.subreddit(name)
        self.streaming = False
        self.analyser = SentimentIntensityAnalyzer()
        self.created_at = datetime.datetime.now()
        self.create_at_iso = utils.unix_to_iso(self.created_at.strftime('%s'))

    def run(self):
        self.conn = utils.db_conn()
        self.stream()
        self.conn.close()

    def kill(self):
        self.streaming = False

    def stream(self):
        self.streaming = True
        for comment in self.subreddit.stream.comments():
            if not self.streaming:
                break
            self.comments += 1
            utils.insert_comment(self.name, comment, self.conn, self.analyser)


class SubRedditDAO(object):
    """SubRedditDAO is the data access object providing a persistent interface to the database"""
    def __init__(self, conn, name):
        self.conn = conn
        self.name = name

    @staticmethod
    def times():
        now = datetime.datetime.now()
        min_30 = utils.unix_to_iso((now - datetime.timedelta(minutes=30)).strftime('%s'))
        hour = utils.unix_to_iso((now - datetime.timedelta(hours=1)).strftime('%s'))
        day = utils.unix_to_iso((now - datetime.timedelta(days=1)).strftime('%s'))
        week = utils.unix_to_iso((now - datetime.timedelta(weeks=1)).strftime('%s'))
        return {
            '30m': min_30,
            '1h': hour,
            '1d': day,
            '1wk': week
        }

    @property
    def now(self):
        return utils.unix_to_iso(datetime.datetime.now().strftime('%s'))

    @property
    def subscribers(self):
        # TODO
        times = self.times()
        sql = "SELECT * FROM comments WHERE created_at BETWEEN '%s' and '%s'"
        return times

    @property
    def sentiment(self):
        """sentiment retrieves sentiment timeseries"""
        times = self.times()
        cursor = self.conn.cursor()
        resp = {}
        for k, v in times.iteritems():
            sql = "SELECT * FROM comments WHERE subreddit='%s' and created_at BETWEEN '%s' and '%s'" % (self.name, v, self.now)
            cursor.execute(sql)
            resp[k] = cursor.fetchone()
        cursor.close()
        return resp

    @property
    def volume(self):
        times = self.times()
        cursor = self.conn.cursor()
        resp = {}
        for k, v in times.iteritems():
            sql = "SELECT Count() FROM comments WHERE subreddit='%s' and created_at BETWEEN '%s' and '%s'" % (self.name, v, self.now)
            cursor.execute(sql)
            resp[k] = cursor.fetchone()[0]
        cursor.close()
        return resp

    def traffic_timeseries(self, duration):
        """retrieve traffic timeseries from db"""
        cursor = self.conn.cursor()
        t1 = datetime.datetime.now()
        if duration == '1d':
            t0 = t1 - datetime.timedelta(days=1)
            delta = datetime.timedelta(minutes=15)
        elif duration == '15m':
            t0 = t1 - datetime.timedelta(minutes=15)
            delta = datetime.timedelta(seconds=15)
        elif duration == '30m':
            t0 = t1 - datetime.timedelta(minutes=30)
            delta = datetime.timedelta(seconds=30)
        elif duration == '1wk':
            t0 = t1 - datetime.timedelta(weeks=1)
            delta = datetime.timedelta(hours=2)
        elif duration == '1hr':
            t0 = t1 - datetime.timedelta(hours=1)
            delta = datetime.timedelta(minutes=1)
        else:
            return {}
        print t0, t1
        intervals = utils.intervals(t0, t1, delta)
        sql = ' UNION ALL '.join(["SELECT Count() " \
                                  "FROM comments WHERE subreddit='%s'  " \
                                  "and created_at BETWEEN '%s' and '%s'" \
                     % (self.name, _t0, _t1) for _t0, _t1 in intervals])
        cursor.execute(sql)
        timeseries = cursor.fetchall()
        flatten_timeseries = [item for sublist in timeseries for item in sublist]
        return {
            'timeseries': flatten_timeseries,
            'start': t0,
            'end': t1,
            'intervals': len(intervals)
        }




