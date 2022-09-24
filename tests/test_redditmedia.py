import pytest
from redditmedia import MediaType, SubmissionMedia, get_reddit, get_media
from redditmedia.cli import main
from click.testing import CliRunner
from typing import List


test_cases = [
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
]


@pytest.mark.parametrize('id, expected', test_cases)
async def test_get_media(id: str, expected: List[SubmissionMedia]):
    """ Tests that `get_media` function returns correct output """

    reddit = get_reddit()
    try:
        submission = await reddit.submission(id=id)
        assert get_media(submission) == expected
    finally:
        await reddit.close()


@pytest.mark.parametrize('id, expected', test_cases)
def test_cli_get(id: str, expected: List[SubmissionMedia]):
    """ Tests that CLI `get` command returns correct output """

    runner = CliRunner()
    result = runner.invoke(main, ['-o', 'get', id])
    assert result.exit_code == 0
    assert result.output == ''.join(x.uri + '\n' for x in expected)
