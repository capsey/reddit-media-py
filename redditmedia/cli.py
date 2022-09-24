import asyncio
import click
from asyncpraw import Reddit  # type: ignore
from asyncpraw.reddit import Submission  # type: ignore
from click import Context, Choice
from typing import Callable, Tuple
from dataclasses import dataclass, field
from . import get_reddit, get_media


@dataclass
class Params:
    output: bool
    separate: bool
    path: str
    credentials: dict = field(default_factory=dict)

    def set_credentials(self, credentials: Tuple):
        if credentials:
            self.credentials['client_id'] = credentials[0]
            self.credentials['client_secret'] = credentials[1]

    def get_reddit(self) -> Reddit:
        return get_reddit(**self.credentials)


@click.group()
@click.option('--output', '-o', is_flag=True, help='Print media URLs instead of downloading')
@click.option('--separate', '-s', is_flag=True, help='Download media to separate folders for each submission')
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

    params = ctx.obj = Params(
        output,
        separate,
        path.rstrip('\\/')
    )

    if credentials:
        params.credentials['client_id'] = credentials[0]
        params.credentials['client_secret'] = credentials[1]


@main.command()
@click.argument('submission-ids', type=str, nargs=-1)
@click.pass_obj
def get(params: Params, submission_ids: Tuple[str]):
    """ Download media from specified submissions """

    async def fetch_submission(id: str, reddit: Reddit):
        submission = await reddit.submission(id)
        await process_submission(submission, params)

    async def fetch_submissions():
        reddit = params.get_reddit()
        try:
            await asyncio.gather(*(fetch_submission(x, reddit) for x in submission_ids))
        finally:
            await reddit.close()

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
    reddit = params.get_reddit()

    try:
        coroutines = []

        async for submission in getter(await reddit.subreddit(subreddit)):
            coroutines.append(process_submission(submission, params))

        await asyncio.gather(*coroutines)
    finally:
        await reddit.close()


async def process_submission(submission: Submission, params: Params):
    if not params.output:
        pass
    else:
        for media in get_media(submission):
            click.echo(media.uri)
