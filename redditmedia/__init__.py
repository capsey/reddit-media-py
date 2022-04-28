import praw  # type: ignore
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


def get_media(submission: praw.reddit.Submission) -> List[SubmissionMedia]:  # TODO: Add support of reposts
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


def download(submissions: Iterable[praw.reddit.Submission], path: str = None, separate: bool = False) -> None:
    """ Downloads all media files of given submission into given folder path """
    path = path or './reddit-media-downloads'  # Default path value


if __name__ == '__main__':
    from . import cli
    cli.main()
