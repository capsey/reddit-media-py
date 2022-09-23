import click
from praw import Reddit
from praw.reddit import Submission
from redditmedia import download, get_media, __version__
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


@click.group()
@click.option('--output', '-o', is_flag=True, help='print media URLs instead of downloading')
@click.option('--separate', '-s', is_flag=True, help='download media to separate folders for each submission')
@click.option('--path', '-p', default='./reddit-media-downloads', help='path to folder for downloaded media')
@click.option('--credentials', '-c', type=(str, str), help='explicitly pass Reddit API credentials')
@click.pass_context
def main(ctx, output, separate, path, credentials):
    """
    Downloads specified reddit submissions media into local folder `reddit-media-downloads`
    (or specified using --path option). For accessing Reddit API credentials should be provided,
    for details go to package page: https://github.com/capsey/reddit-media-py
    """

    obj = ctx.obj = {}

    obj['output'] = output
    obj['separate'] = separate
    obj['path'] = path.rstrip('\\/')
    obj['credentials'] = {}

    if credentials:
        obj['credentials']['client_id'] = credentials[0]
        obj['credentials']['client_secret'] = credentials[1]
    else:
        obj['credentials']['site_name'] = 'redditmedia'

    obj['reddit'] = Reddit(**obj['credentials'], user_agent=f'Script/{__version__}')


@main.command()
@click.argument('submissions', type=str, nargs=-1)
@click.pass_obj
def get(obj, submissions):
    """ Download media from specified submissions """

    submissions = (obj['reddit'].submission(x) for x in submissions)
    process(submissions, obj['output'], obj['path'], obj['separate'])


@main.command()
@click.option('--limit', '-n', default=1, help='maximum number of submissions to download')
@click.argument('subreddit', type=str)
@click.pass_obj
def hot(obj, subreddit, limit):
    """ Download media of hot submissions in specified subreddit """

    if subreddit.startswith('r/'):
        subreddit = subreddit[2:]

    submissions = obj['reddit'].subreddit(subreddit).hot(limit=limit)
    process(submissions, obj['output'], obj['path'], obj['separate'])


@main.command()
@click.option('--limit', '-n', default=1, help='maximum number of submissions to download')
@click.argument('subreddit', type=str)
@click.pass_obj
def new(obj, subreddit, limit):
    """ Download media of new submissions in specified subreddit """

    if subreddit.startswith('r/'):
        subreddit = subreddit[2:]

    submissions = obj['reddit'].subreddit(subreddit).hot(limit=limit)
    process(submissions, obj['output'], obj['path'], obj['separate'])


time_filters = ['all', 'day', 'hour', 'month', 'week', 'year']

@main.command()
@click.option('--limit', '-n', default=1, help='maximum number of submissions to download')
@click.option('--time-filter', '-t', default=time_filters[0], type=click.Choice(time_filters, case_sensitive=False))
@click.argument('subreddit', type=str)
@click.pass_obj
def top(obj, subreddit, limit, time_filter):
    """ Download media of top submissions in specified subreddit """

    if subreddit.startswith('r/'):
        subreddit = subreddit[2:]

    submissions = obj['reddit'].subreddit(subreddit).top(limit=limit, time_filter=time_filter)
    process(submissions, obj['output'], obj['path'], obj['separate'])


def process(submissions: Iterable[Submission], output, path: str, separate: bool):
    """ Downloads or prints media files of given submissions """

    if not output:
        with click.progressbar(submissions, label='Downloading...') as bar:
            download(bar, path=path, separate=separate)
    else:
        for id in submissions:
            for media in get_media(id):
                click.echo(media.uri)
