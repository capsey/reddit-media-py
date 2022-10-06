import pytest
from redditmedia import MediaType, SubmissionResult, SubmissionFile, get_reddit, get_media
from redditmedia.cli import main
from aiohttp import ClientSession
from click.testing import CliRunner
from typing import List, Tuple


test_cases = [
    ('xkztsb', []),
    ('vphwx7', [('https://v.redd.it/gk0cnafxk2991/DASH_720.mp4?source=fallback', MediaType.mp4)]),
    ('xi0mkn', [('https://i.redd.it/7wixq0lg0so91.jpg', MediaType.jpg)]),
    ('udjs7k', [('https://i.redd.it/5hqmcunoj3w81.gif', MediaType.gif)]),
    ('wepuys', [
        ('https://i.redd.it/1turjpf3rdf91.jpg', MediaType.jpg),
        ('https://i.redd.it/5p3xojf3rdf91.jpg', MediaType.jpg),
        ('https://i.redd.it/xunukif3rdf91.jpg', MediaType.jpg),
        ('https://i.redd.it/nmem2hf3rdf91.jpg', MediaType.jpg),
        ('https://i.redd.it/ljw17if3rdf91.jpg', MediaType.jpg),
        ('https://i.redd.it/c87gbof3rdf91.jpg', MediaType.jpg),
        ('https://i.redd.it/6cibmjf3rdf91.jpg', MediaType.jpg),
    ]),
]


@pytest.mark.parametrize('id, expected', test_cases)
async def test_get_media(id: str, expected: List[Tuple[str, MediaType]]):
    """ Tests that `get_media` function returns correct output """

    async with get_reddit() as reddit:
        submission = await reddit.submission(id=id)
        assert get_media(submission) == SubmissionResult([SubmissionFile(*x) for x in expected], id)


async def test_valid_url():
    """ Tests that `get_media` function returns valid URLs """

    async with ClientSession() as session:
        async with get_reddit() as reddit:
            subreddit = await reddit.subreddit('cute')
            async for submission in subreddit.hot(limit=100):
                for media in get_media(submission).media:
                    head = await session.head(media.uri)
                    assert head.status == 200
                    assert head.content_type == media.type.content_type


@pytest.mark.parametrize('id, expected', test_cases)
def test_cli_get(id: str, expected: List[Tuple[str, MediaType]]):
    """ Tests that CLI `get` command returns correct output """

    runner = CliRunner()
    result = runner.invoke(main, ['-o', 'get', id])
    assert result.exit_code == 0
    assert result.output == ''.join('%s\n' % x[0] for x in expected)
