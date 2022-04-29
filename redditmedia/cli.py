import praw  # type: ignore
import argparse
import os
from redditmedia import download
from typing import Any, Dict, List, Optional, Sequence, Tuple
from tqdm import tqdm


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
        '-c', '--credentials', help='use specified credentials for Reddit API instead', action='store_true')
    parser.add_argument(
        'ids', help='IDs of submissions to download media from', nargs='+')

    parsed = parser.parse_args(args=manual_args)

    # Setting credentials
    if parsed.credentials:
        credentials = dict(
            client_id=input('- Reddit API Client ID:     '),
            client_secret=input('- Reddit API Client Secret: '),
            username=input('- Reddit API Username:      '),
            password=input('- Reddit API Password:      '),
        )
    else:
        try:
            credentials = dict(
                client_id=os.environ['REDDIT_CLIENT_ID'],
                client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                username=os.environ['REDDIT_USERNAME'],
                password=os.environ['REDDIT_PASSWORD'],
            )
        except KeyError as e:
            raise Exception('Credentials are not set into environment variables') from e

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
