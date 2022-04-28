import praw  # type: ignore
from typing import Any, Dict, List, Iterable, Optional, Sequence, Tuple
from enum import Enum, auto
from dataclasses import dataclass


class MediaType(Enum):
    """ Enum of type of media of Reddit submission """
    image = auto()
    video = auto()


@dataclass
class SubmissionMedia:
    """ Container class for submission media """
    uri: str
    type: MediaType


def get_media(submission: praw.reddit.Submission) -> List[SubmissionMedia]:
    """ Returns list of media URLs of the submission and its MediaType """
    media = []

    if submission.is_video:
        media.append(SubmissionMedia(
            submission.media['reddit_video']['fallback_url'],
            MediaType.video
        ))
    elif hasattr(submission, 'is_gallery') and submission.is_gallery:
        # As for now, Reddit only supports images in galleries
        for x in submission.gallery_data['items']:
            media_id = x['media_id']
            *_, extension = submission.media_metadata[media_id]['m'].split('/')
            media.append(SubmissionMedia(
                f'https://i.redd.it/{media_id}.{extension}',
                MediaType.image
            ))
    elif hasattr(submission, 'post_hint') and submission.post_hint == 'image':
        media.append(SubmissionMedia(
            submission.url,
            MediaType.image
        ))

    return media


def download(submissions: Iterable[praw.reddit.Submission], path: str = None, separate: bool = False):
    """ Downloads all media files of given submission into given folder path """
    path = path or './reddit-media-downloads'  # Default path value


def get_args(manual_args: Optional[Sequence[str]] = None) -> Tuple[Dict[str, str], Optional[List[str]], Dict[str, Any]]:
    import argparse

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


if __name__ == '__main__':
    credidentials, submission_ids, kwargs = get_args()
    reddit = praw.Reddit(**credidentials, user_agent="Script/0.0.1")

    if submission_ids is None:
        submission_ids = reddit.subreddit('axolotls').hot(limit=5)
    submissions = [reddit.submission(x) for x in submission_ids]

    download(submissions, **kwargs)  # TODO: Add progress bar
