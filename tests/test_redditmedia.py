from typing import List
import pytest
import praw  # type: ignore
from redditmedia import MediaType, SubmissionMedia, get_media
from redditmedia.cli import get_args


@pytest.mark.parametrize('id, expected', [
    ('pdyqot', []),
    ('ud3rtw', [SubmissionMedia('https://v.redd.it/vp01yto5r2w81/DASH_1080.mp4?source=fallback', MediaType.mp4)]),
    ('uct2zu', [SubmissionMedia('https://i.redd.it/r85g3v27fzv81.jpg', MediaType.jpg)]),
    ('udjs7k', [SubmissionMedia('https://i.redd.it/5hqmcunoj3w81.gif', MediaType.gif)]),
    ('ucz2uh', [
        SubmissionMedia('https://i.redd.it/rdmzmqgrc1w81.jpg', MediaType.jpg),
        SubmissionMedia('https://i.redd.it/zgwy5jnrc1w81.jpg', MediaType.jpg),
    ]),
])
def test_get_media(reddit: praw.Reddit, id: str, expected: List[SubmissionMedia]):
    """ Tests that `get_media` function returns correct output """
    submission = reddit.submission(id=id)
    assert get_media(submission) == expected


def test_invalid_args():
    """ Tests that `get_args` function does not allow invalid CLI arguments """
    with pytest.raises(SystemExit) as excinfo:
        get_args(manual_args=[])

    assert excinfo.value.code == 2
