import praw  # type: ignore
import argparse
import os
from redditmedia import download
from typing import Any, Dict, List, Optional, Sequence, Tuple
from tqdm import tqdm  # type: ignore


description = '''
    Downloads specified reddit submissions media into local folder `reddit-media-downloads`
    (or specified using --path option). For accessing Reddit API credentials should be provided,
    for details go to package page: https://github.com/capsey/reddit-media-py
'''


def get_args(manual_args: Optional[Sequence[str]] = None) -> Tuple[Dict[str, str], Optional[List[str]], Dict[str, Any]]:
    """ Parses CLI arguments and returns parsed arguments using `argparse` """
    # Parsing command-line arguments
    parser = argparse.ArgumentParser(prog='redditmedia', add_help=True, description=description)
    parser.add_argument(
        '-p', '--path', help='path to folder for downloaded media')
    parser.add_argument(
        '-s', '--separate', help='download media to separate folders for each submission', action='store_true')
    parser.add_argument(
        '-c', '--credentials', help='explicitly pass Reddit API credentials', nargs=2)
    parser.add_argument(
        'ids', help='IDs of submissions to download media from', nargs='+')

    parsed = parser.parse_args(args=manual_args)

    # Setting credentials
    credentials = {}

    if parsed.credentials:
        credentials['client_id'] = parsed.credentials[0]
        credentials['client_secret'] = parsed.credentials[1]
    else:
        credentials['site_name'] = 'redditmedia'

    credentials['user_agent'] = 'Script/0.0.1',

    # Setting positional arguments
    submissions = parsed.ids or None

    # Setting keyword arguments
    kwargs = {}

    kwargs['path'] = parsed.path
    kwargs['separate'] = parsed.separate

    return credentials, submissions, kwargs


def main() -> None:
    """ Entrypoint of standalone CLI app """
    credentials, submission_ids, kwargs = get_args()
    reddit = praw.Reddit(**credentials, user_agent='Script/0.0.1')

    if submission_ids is None:
        submission_ids = reddit.subreddit('axolotls').hot(limit=5)
    submissions = [reddit.submission(x) for x in submission_ids]

    progressbar = tqdm(submissions, desc='Downloading...', colour='green', ascii=True)
    download(progressbar, **kwargs)
