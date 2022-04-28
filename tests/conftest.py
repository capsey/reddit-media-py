import os
import pytest
import praw  # type: ignore


@pytest.fixture(scope='session')
def reddit():
    reddit = praw.Reddit(
        client_id=os.environ['REDDIT_CLIENT_ID'],
        client_secret=os.environ['REDDIT_CLIENT_SECRET'],
        username=os.environ['REDDIT_USERNAME'],
        password=os.environ['REDDIT_PASSWORD'],
        user_agent="Script/0.0.1",
    )
    return reddit
