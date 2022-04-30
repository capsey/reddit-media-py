import pytest
import praw  # type: ignore


@pytest.fixture(scope='session')
def reddit():
    reddit = praw.Reddit(
        site_name='redditmedia',
        user_agent='Script/0.0.1',
    )
    return reddit
