import praw
from typing import List
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


def run(reddit: praw.Reddit, submission_id: str, path: str = './reddit-media-downloads'):
    """ Downloads all media files of given submission into local folder """
    pass


if __name__ == '__main__':
    reddit = praw.Reddit(
        client_id="client_id",
        client_secret="client_secret",
        password="password",
        user_agent="Script/0.0.1",
        username="username",
    )

    run(reddit)
