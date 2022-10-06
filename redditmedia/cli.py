import asyncio
import click
from asyncpraw import Reddit  # type: ignore
from asyncpraw.reddit import Submission  # type: ignore
from tqdm import tqdm
from click import Context, Choice
from typing import Callable, Optional, Tuple
from dataclasses import dataclass
from . import get_reddit, get_media, download_async


@dataclass
class Params:
    output: bool
    separate: bool
    path: str
    credentials: Tuple[str, str]

    def get_reddit(self) -> Reddit:
        if self.credentials:
            return get_reddit(client_id=self.credentials[0], client_secret=self.credentials[1])
        return get_reddit()


@click.group()
@click.option('--output', '-o', is_flag=True, help='Print media URLs instead of downloading')
@click.option('--separate', is_flag=True, help='Download media to separate folders for each submission')
@click.option('--path', '-p', default='./reddit-media-downloads', help='Path to folder for downloaded media')
@click.option('--credentials', '-c', type=(str, str), help='Explicitly pass Reddit API credentials')
@click.pass_context
def main(ctx: Context, output: bool, separate: bool, path: str, credentials: Tuple[str, str]):
    """
    Downloads specified reddit submissions media into local folder `reddit-media-downloads`
    (or specified using --path option). For accessing Reddit API credentials should be provided
    either via `-c` option, or `praw.ini` file. For details go to package page:
    https://github.com/capsey/reddit-media-py
    """

    ctx.obj = Params(output, separate, path.rstrip('\\/'), credentials)


@main.command()
@click.argument('submission-ids', type=str, nargs=-1)
@click.pass_obj
def get(params: Params, submission_ids: Tuple[str]):
    """ Download media from specified submissions """

    async def fetch_submission(id: str, reddit: Reddit):
        submission = await reddit.submission(id)
        await process_submission(submission, params)

    async def fetch_submissions():
        async with params.get_reddit() as reddit:
            await asyncio.gather(*(fetch_submission(x, reddit) for x in submission_ids))

    asyncio.run(fetch_submissions())


@main.command()
@click.option('--limit', '-n', default=1, help='Maximum number of submissions to download')
@click.argument('subreddit', type=str)
@click.pass_obj
def hot(params: Params, subreddit: str, limit: int):
    """ Download media of hot submissions in specified subreddit """

    if subreddit.startswith('r/'):
        subreddit = subreddit[2:]

    asyncio.run(fetch_subreddit(subreddit, lambda x: x.hot(limit=limit), params))


@main.command()
@click.option('--limit', '-n', default=1, help='Maximum number of submissions to download')
@click.argument('subreddit', type=str)
@click.pass_obj
def new(params: Params, subreddit: str, limit: int):
    """ Download media of new submissions in specified subreddit """

    if subreddit.startswith('r/'):
        subreddit = subreddit[2:]

    asyncio.run(fetch_subreddit(subreddit, lambda x: x.new(limit=limit), params))


time_filters = ['all', 'day', 'hour', 'month', 'week', 'year']


@main.command()
@click.option('--limit', '-n', default=1, help='Maximum number of submissions to download')
@click.option('--time-filter', '-t', default=time_filters[0], type=Choice(time_filters, case_sensitive=False))
@click.argument('subreddit', type=str)
@click.pass_obj
def top(params: Params, subreddit: str, limit: int, time_filter: str):
    """ Download media of top submissions in specified subreddit """

    if subreddit.startswith('r/'):
        subreddit = subreddit[2:]

    asyncio.run(fetch_subreddit(subreddit, lambda x: x.top(limit=limit, time_filter=time_filter), params))


async def fetch_subreddit(subreddit: str, getter: Callable, params: Params):
    async with params.get_reddit() as reddit:
        with tqdm(desc='Downloading...', leave=False, total=0, unit='B', unit_scale=True, unit_divisor=1024) as bar:
            coroutines = []

            async for submission in getter(await reddit.subreddit(subreddit)):
                coroutines.append(process_submission(submission, params, bar=bar))

            await asyncio.gather(*coroutines)


async def process_submission(submission: Submission, params: Params, bar: Optional[tqdm] = None):
    result = get_media(submission)

    if not params.output:
        await download_async(result, params.path, params.separate, bar=bar)
    else:
        for media in result.media:
            click.echo(media.uri)
