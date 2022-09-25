import os
import aiofiles
import asyncio
from asyncio import Semaphore
from aiohttp import ClientSession
from typing import List, Optional
from asyncpraw import Reddit  # type: ignore
from asyncpraw.models import Submission  # type: ignore
from enum import Enum, auto
from dataclasses import dataclass
from contextlib import asynccontextmanager


__version__ = '0.0.2'


class MediaType(Enum):
    """ Enum of type of media of Reddit submission """

    jpg = auto()
    png = auto()
    gif = auto()
    mp4 = auto()

    def assert_head(self, type: str):
        if self == MediaType.jpg:
            assert type == 'image/jpeg'
        elif self == MediaType.png:
            assert type == 'image/png'
        elif self == MediaType.gif:
            assert type == 'image/gif'
        elif self == MediaType.mp4:
            assert type == 'video/mp4'


@dataclass
class SubmissionFile:
    """ Container class for submission media """

    uri: str
    type: MediaType
    size: Optional[int] = None

    async def get_size(self) -> None:
        async with ClientSession() as session:
            head = await session.head(self.uri)
            self.type.assert_head(head.content_type)
            self.size = head.content_length


@dataclass
class SubmissionResult:
    """ Represents result of `get_media` function, containing list of media """

    media: List[SubmissionFile]
    id: str


@asynccontextmanager
async def get_reddit(**kwargs: str) -> Reddit:
    """
    Returns Reddit instance as Context Manager:
    ```
    async with get_reddit(...) as reddit:
        # your code goes here
    ```
    """

    reddit = Reddit(**kwargs, site_name='redditmedia', user_agent='redditmedia v' + __version__)
    try:
        yield reddit
    finally:
        await reddit.close()


def get_media(submission: Submission) -> SubmissionResult:
    """ Returns list of media URLs of the submission and its MediaType """

    media = []

    if submission.is_video:
        media.append(SubmissionFile(
            submission.media['reddit_video']['fallback_url'],
            MediaType.mp4
        ))
    elif hasattr(submission, 'is_gallery') and submission.is_gallery:
        # As for now, Reddit only supports images in galleries
        for x in submission.gallery_data['items']:
            media_id = x['media_id']
            extension = submission.media_metadata[media_id]['m'].split('/')[-1]
            media.append(SubmissionFile(
                f'https://i.redd.it/{media_id}.{extension}',
                MediaType[extension]
            ))
    elif hasattr(submission, 'post_hint') and submission.post_hint == 'image':
        media.append(SubmissionFile(
            submission.url,
            MediaType[submission.url.split('.')[-1]]
        ))

    return SubmissionResult(media, submission.id)


async def download_async(
    result: SubmissionResult,
    path: str = './reddit-media-downloads',
    separate: bool = False,
    task_limit: int = 5
) -> None:
    """ Downloads all media files of given submission into given folder path """

    # Check file path
    path = path.rstrip('\\/')

    if not os.path.exists(path):
        os.makedirs(path)

    async with ClientSession() as session:
        semaphore = Semaphore(task_limit)
        cors = []

        for i, media in enumerate(result.media):
            if separate:
                file = '%s/%s/%i.%s' % (path, result.id, i, media.type.name)
            else:
                file = '%s/%s_%i.%s' % (path, result.id, i, media.type.name)
            cors.append(download_file_async(media, session, file, semaphore))

        await asyncio.gather(*cors)


async def download_file_async(
    file: SubmissionFile,
    session: ClientSession,
    path: str,
    semaphore: Semaphore
) -> None:
    async with semaphore:
        # GET request
        response = await session.get(file.uri)

        if response.status != 200:
            raise Exception(response)
        elif file.type.assert_head(response.content_type):
            raise Exception('URL leads to file with type that does not match!')

        # Writing into file
        async for img_data in response.content:
            async with aiofiles.open(path, 'ab') as handler:
                await handler.write(img_data)
