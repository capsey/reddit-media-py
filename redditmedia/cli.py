import praw  # type: ignore
import argparse
from redditmedia import download
from typing import Any, Dict, List, Optional, Sequence, Tuple


def get_args(manual_args: Optional[Sequence[str]] = None) -> Tuple[Dict[str, str], Optional[List[str]], Dict[str, Any]]:
    """ Parses CLI arguments and returns parsed arguments using `argparse` """
    # Parsing command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--Credidentials", help="Client ID, Client Secret, Username and Password for Reddit API", nargs=4, required=True)
    parser.add_argument(
        "-s", "--Submissions", help="Submissions IDs to download", nargs='+', required=False)
    parser.add_argument(
        "-p", "--Path", help="Path to downloaded media folder", required=False)
    parser.add_argument(
        "-e", "--Each", help="Download media to separate folders for each submission", action='store_true')

    parsed = parser.parse_args(args=manual_args)

    # Setting credidentials
    credidentials = dict(
        client_id=parsed.Credidentials[0],
        client_secret=parsed.Credidentials[1],
        username=parsed.Credidentials[2],
        password=parsed.Credidentials[3],
    )

    # Setting positional arguments
    submissions = parsed.Submissions or None

    # Setting keyword arguments
    kwargs = {}

    if parsed.Path:
        kwargs['path'] = parsed.Path
    kwargs['separate'] = parsed.Each

    return credidentials, submissions, kwargs


def main() -> None:
    """ Entrypoint of standalone CLI app """
    credidentials, submission_ids, kwargs = get_args()
    reddit = praw.Reddit(**credidentials, user_agent="Script/0.0.1")

    if submission_ids is None:
        submission_ids = reddit.subreddit('axolotls').hot(limit=5)
    submissions = [reddit.submission(x) for x in submission_ids]

    download(submissions, **kwargs)  # TODO: Add progress bar
