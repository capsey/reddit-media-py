import praw
from typing import List, Iterable
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


def run(reddit: praw.Reddit, submission_ids: Iterable[str], path: str = './reddit-media-downloads', separate: bool = False):
    """ Downloads all media files of given submission into given folder path """
    pass


if __name__ == '__main__':
    import argparse

    # Getting arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--Credidentials", help="Client ID, Client Secret, Username and Password for Reddit API", nargs='4')
    parser.add_argument(
        "-s", "--Submissions", help="Submissions IDs to download", nargs='+', required=False)
    parser.add_argument(
        "-p", "--Path", help="Path to downloaded media folder", required=False)
    parser.add_argument(
        "-e", "--Each", help="Download media to separate folders for each submission", action='store_true')

    args = parser.parse_args()

    # Authenticating into Reddit API
    client_id, client_secret, username, password = args.Credidentials

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent="Script/0.0.1",
    )

    # Getting submissions list
    submissions = args.Submissions

    if not submissions:
        subreddit = reddit.subreddit("axolotls")
        submissions = subreddit.hot(limit=5)

    # Runs downloading
    kwargs = dict(path=args.Path) if args.Path else {}
    run(reddit, submissions, **kwargs, separate=args.e)  # TODO: Add progress bar
