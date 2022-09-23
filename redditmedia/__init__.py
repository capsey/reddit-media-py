from typing import List
from asyncpraw import Reddit  # type: ignore
from asyncpraw.reddit import Submission  # type: ignore
import os
import requests
from enum import Enum, auto
from dataclasses import dataclass


__version__ = '0.0.2'


class MediaType(Enum):
    """ Enum of type of media of Reddit submission """

    jpg = auto()
    png = auto()
    gif = auto()
    mp4 = auto()


@dataclass
class SubmissionMedia:
    """ Container class for submission media """

    uri: str
    type: MediaType


def get_reddit(**kwargs: dict) -> Reddit:
    """ Returns Reddit instance """

    return Reddit(**kwargs, site_name='redditmedia', user_agent='redditmedia v' + __version__)


def get_media(submission: Submission) -> List[SubmissionMedia]:
    """ Returns list of media URLs of the submission and its MediaType """

    media = []

    if submission.is_video:
        media.append(SubmissionMedia(
            submission.media['reddit_video']['fallback_url'],
            MediaType.mp4
        ))
    elif hasattr(submission, 'is_gallery') and submission.is_gallery:
        # As for now, Reddit only supports images in galleries
        for x in submission.gallery_data['items']:
            media_id = x['media_id']
            extension = submission.media_metadata[media_id]['m'].split('/')[-1]
            media.append(SubmissionMedia(
                f'https://i.redd.it/{media_id}.{extension}',
                MediaType[extension]
            ))
    elif hasattr(submission, 'post_hint') and submission.post_hint == 'image':
        media.append(SubmissionMedia(
            submission.url,
            MediaType[submission.url.split('.')[-1]]
        ))

    return media


async def download_async(submission_media: List[SubmissionMedia], id: str, path: str, separate: bool = False) -> None:
    """ Downloads all media files of given submission into given folder path """

    for i, media in enumerate(submission_media):
        # Requests media data
        response = requests.get(media.uri)

        if not response.ok:
            raise Exception(response)

        img_data = response.content

        # File path
        folder = f'{path}/{id}' if separate else path
        file = i if separate else f'{id}_{i}'

        if not os.path.exists(folder):
            os.makedirs(folder)

        # Writing into file
        with open(f'{folder}/{file}.{media.type.name}', 'wb') as handler:
            handler.write(img_data)
