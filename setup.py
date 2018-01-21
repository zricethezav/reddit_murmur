import setuptools

setuptools.setup(name='reddit_murmur',
      packages=setuptools.find_packages(),
        install_requires=[
            'psycopg2',
            'praw',
            'vaderSentiment',
            'flask'
        ]
    )
