import asyncio
import click
from asyncpraw.reddit import Submission
from click import Context, Choice
from typing import Callable, Tuple
from . import get_reddit, get_media


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

    obj = ctx.obj = {}

    obj['output'] = output
    obj['separate'] = separate
    obj['path'] = path.rstrip('\\/')
    obj['credentials'] = {}

    if credentials:
        obj['credentials']['client_id'] = credentials[0]
        obj['credentials']['client_secret'] = credentials[1]

    click.echo('Connecting to Reddit API...')


@main.command()
@click.argument('submission-ids', type=str, nargs=-1)
@click.pass_obj
def get(obj: dict, submission_ids: Tuple[str]):
    """ Download media from specified submissions """

    async def fetch_submission(id, reddit):
        submission = await reddit.submission(id)
        await process_submission(submission, obj['output'])

    async def fetch_submissions():
        reddit = get_reddit(**obj['credentials'])
        try:
            await asyncio.gather(*(fetch_submission(x, reddit) for x in submission_ids))
        finally:
            await reddit.close()

    asyncio.run(fetch_submissions())


@main.command()
@click.option('--limit', '-n', default=1, help='Maximum number of submissions to download')
@click.argument('subreddit', type=str)
@click.pass_obj
def hot(obj: dict, subreddit: str, limit: int):
    """ Download media of hot submissions in specified subreddit """

    if subreddit.startswith('r/'):
        subreddit = subreddit[2:]

    asyncio.run(fetch_subreddit(subreddit, lambda x: x.hot(limit=limit), obj['credentials'], obj['output']))


@main.command()
@click.option('--limit', '-n', default=1, help='Maximum number of submissions to download')
@click.argument('subreddit', type=str)
@click.pass_obj
def new(obj: dict, subreddit: str, limit: int):
    """ Download media of new submissions in specified subreddit """

    if subreddit.startswith('r/'):
        subreddit = subreddit[2:]

    asyncio.run(fetch_subreddit(subreddit, lambda x: x.new(limit=limit), obj['credentials'], obj['output']))


time_filters = ['all', 'day', 'hour', 'month', 'week', 'year']


@main.command()
@click.option('--limit', '-n', default=1, help='Maximum number of submissions to download')
@click.option('--time-filter', '-t', default=time_filters[0], type=Choice(time_filters, case_sensitive=False))
@click.argument('subreddit', type=str)
@click.pass_obj
def top(obj: dict, subreddit: str, limit: int, time_filter: str):
    """ Download media of top submissions in specified subreddit """

    if subreddit.startswith('r/'):
        subreddit = subreddit[2:]

    asyncio.run(fetch_subreddit(subreddit, lambda x: x.top(limit=limit, time_filter=time_filter), obj['credentials'], obj['output']))


async def fetch_subreddit(subreddit: str, getter: Callable, credentials: dict, output: bool):
    reddit = get_reddit(**credentials)

    try:
        coroutines = []

        async for submission in getter(await reddit.subreddit(subreddit)):
            coroutines.append(process_submission(submission, output))

        await asyncio.gather(*coroutines)
    finally:
        await reddit.close()


async def process_submission(submission: Submission, output: bool):
    if not output:
        pass
    else:
        for media in get_media(submission):
            click.echo(media.uri)
