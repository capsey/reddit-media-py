import pytest
import praw  # type: ignore
from redditmedia import __version__


@pytest.fixture(scope='session')
def reddit():
    reddit = praw.Reddit(
        site_name='redditmedia',
        user_agent=f'Script/{__version__}',
    )
    return reddit
