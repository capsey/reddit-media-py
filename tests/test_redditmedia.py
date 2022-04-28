from typing import Any, Dict, List, Optional, Sequence, Tuple
import pytest
import praw  # type: ignore
from redditmedia import MediaType, SubmissionMedia, get_media
from redditmedia.cli import get_args


@pytest.mark.parametrize('id, expected', [  # udjs7k, hyts0n
    ('pdyqot', []),
    ('ud3rtw', [SubmissionMedia('https://v.redd.it/vp01yto5r2w81/DASH_1080.mp4?source=fallback', MediaType.mp4)]),
    ('uct2zu', [SubmissionMedia('https://i.redd.it/r85g3v27fzv81.jpg', MediaType.jpg)]),
    ('ucz2uh', [
        SubmissionMedia('https://i.redd.it/rdmzmqgrc1w81.jpg', MediaType.jpg),
        SubmissionMedia('https://i.redd.it/zgwy5jnrc1w81.jpg', MediaType.jpg),
    ]),
])
def test_get_media(reddit: praw.Reddit, id: str, expected: List[SubmissionMedia]):
    """ Tests that `get_media` function returns correct output """
    submission = reddit.submission(id=id)
    assert get_media(submission) == expected


@pytest.mark.parametrize('args, expected', [
    ([],                                     (None,          dict(separate=False))),
    (['-s', 'a'],                            (['a'],         dict(separate=False))),
    (['-s', 'a', 'b'],                       (['a', 'b'],    dict(separate=False))),
    (['-p', './haha'],                       (None,          dict(separate=False, path='./haha'))),
    (['-s', 'a', 'b', '-p', './haha'],       (['a', 'b'],    dict(separate=False, path='./haha'))),
    (['-e'],                                 (None,          dict(separate=True))),
    (['-e', '-s', 'a'],                      (['a'],         dict(separate=True))),
    (['-e', '-s', 'a', 'b'],                 (['a', 'b'],    dict(separate=True))),
    (['-e', '-p', './haha'],                 (None,          dict(separate=True, path='./haha'))),
    (['-e', '-s', 'a', 'b', '-p', './haha'], (['a', 'b'],    dict(separate=True, path='./haha'))),
])
def test_get_args(args: List[str], expected: Tuple[Optional[List[str]], Dict[str, Any]]):
    """ Tests that `get_args` function parses CLI arguments correctly """
    # TODO: https://stackoverflow.com/questions/13493288/python-cli-program-unit-testing
    full_args = ['-c', '1', '2', '3', '4', *args]
    full_expected = dict(client_id='1', client_secret='2', username='3', password='4'), *expected

    assert get_args(manual_args=full_args) == full_expected


@pytest.mark.parametrize('args', [
    None,
    [],
    ['-s', 'a'],
    ['hello?'],
    ['-c', 'huh?'],
])
def test_invalid_args(args: Optional[Sequence[str]]):
    """ Tests that `get_args` function does not allow invalid CLI arguments """
    with pytest.raises(SystemExit) as excinfo:
        get_args(manual_args=args)

    assert excinfo.value.code == 2
