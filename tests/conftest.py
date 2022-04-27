import pytest
import praw


@pytest.fixture(scope='session')
def reddit():
    reddit = praw.Reddit(
        client_id="client_id",
        client_secret="client_secret",
        username="username",
        password="password",
        user_agent="Script/0.0.1",
    )
    return reddit
