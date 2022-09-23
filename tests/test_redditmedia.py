from typing import List
import pytest
import praw  # type: ignore
from redditmedia import MediaType, SubmissionMedia, get_media


@pytest.mark.parametrize('id, expected', [
    ('xkztsb', []),
    ('vphwx7', [SubmissionMedia('https://v.redd.it/gk0cnafxk2991/DASH_720.mp4?source=fallback', MediaType.mp4)]),
    ('xi0mkn', [SubmissionMedia('https://i.redd.it/7wixq0lg0so91.jpg', MediaType.jpg)]),
    ('udjs7k', [SubmissionMedia('https://i.redd.it/5hqmcunoj3w81.gif', MediaType.gif)]),
    ('wepuys', [
        SubmissionMedia('https://i.redd.it/1turjpf3rdf91.jpg', MediaType.jpg),
        SubmissionMedia('https://i.redd.it/5p3xojf3rdf91.jpg', MediaType.jpg),
        SubmissionMedia('https://i.redd.it/xunukif3rdf91.jpg', MediaType.jpg),
        SubmissionMedia('https://i.redd.it/nmem2hf3rdf91.jpg', MediaType.jpg),
        SubmissionMedia('https://i.redd.it/ljw17if3rdf91.jpg', MediaType.jpg),
        SubmissionMedia('https://i.redd.it/c87gbof3rdf91.jpg', MediaType.jpg),
        SubmissionMedia('https://i.redd.it/6cibmjf3rdf91.jpg', MediaType.jpg),
    ]),
])
def test_get_media(reddit: praw.Reddit, id: str, expected: List[SubmissionMedia]):
    """ Tests that `get_media` function returns correct output """
    submission = reddit.submission(id=id)
    assert get_media(submission) == expected
