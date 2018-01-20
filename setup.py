from setuptools import setup

setup(name='reddit-murmur',
        packages=['reddit_murmur'],
        install_requires=[
            'psycopg2',
            'praw',
            'vaderSentiment'
        ]
    )
