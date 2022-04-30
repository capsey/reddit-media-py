# Reddit Media Getter

![Tests passing Badge](https://github.com/capsey/reddit-media-py/actions/workflows/tests.yml/badge.svg)
[![Supported Python versions Badge](https://img.shields.io/pypi/pyversions/reddit-media)](https://pypi.org/project/reddit-media/)
[![PyPI package version Badge](https://img.shields.io/pypi/v/reddit-media)](https://pypi.org/project/reddit-media/)

Gets media file URLs from Reddit Submissions using [PRAW](https://github.com/praw-dev/praw) library and optionally downloads it. Supports video and single or gallery images. Can be used both as standalone package and library for Python scripts.

## How to install

To use this package, you first have to [install Python 3.7 or higher](https://www.python.org/downloads/) (versions below are not supported). Then open your terminal and type following command to install the latest version of the package from PyPI repository:

```
pip install reddit-media
```

This package uses PRAW library that utilizes Reddit API to fetch data from Reddit. However, Reddit API requires authentication for scripts that use it, so you will have to do some configuration beforehand. Specifically, it requires app Client ID and Client Secret. You can create both very easily following next steps:

- Open this page: https://reddit.com/prefs/apps
- If you are not logged in into your Reddit account, you will be prompted to do so
- You will see 'authorized applications' page
- Scroll to the very bottom and press 'create another app...' button
- Select application type 'script'
- Enter any name and redirect URL you want (you will be able to change it later)
- Press 'create app' button. You will see your new app created
- Copy Client ID just under 'personal use script' text and name of the app
- Copy Client Secret next to 'secret' field

![Example](https://user-images.githubusercontent.com/46106832/166102158-c9df28c2-385e-4de9-a8db-c5e2831f2d3f.png)

> Note that credentials on the screenshot are only for demostrative purposes, they are invalid. For details about authenticating, check out this page: [Authenticating via OAuth](https://praw.readthedocs.io/en/stable/getting_started/authentication.html)

## Using as a library

If your Python script needs to get URLs of some Reddit submission, but you don't want to do it yourself, you can use this package to do it for you. Once you installed the package, you can just import it and use as any other library:

```python
from praw import Reddit
from redditmedia import get_media, MediaType

submissions = Reddit(...).subreddit('aww').hot(limit=10)  # First 10 submissions on r/aww
submissions_media = [get_media(submission) for submission in submissions]

for media_list in submissions_media:
  for media in media_list:
    if media.type in [MediaType.jpg, MediaType.png]:  # Print only URLs of images
      print(media.uri)
```

## Using as standalone program

If you want to download bunch of media files from some reddit submissions into your local storage, you can do this by using this package as standalone CLI program. You can do that typing something like this into terminal:

```console
python -m redditmedia [IDS OF SUBMISSIONS SEPARATED WITH SPACE] -c [Client ID] [Client Secret]
```

This will download all media files from specified submissions into `reddit-media-downloads` folder in current working directory. If you wish to change path of the folder where media should be downloaded to, you can specify it by adding `-p [PATH TO FOLDER]` option at the end of the command above, or if you wish to have media files in separate folders depending on the submission they are from, you can do that by adding `-s` flag at the end of the command.

As you can see, this requires you to explicitly provide credentials as arguments every time you run the program. This is inconvenient if you use the program often. Instead you can create `praw.ini` file inside your current working directory and paste this:

```ini
[redditmedia]
client_id=<Paste Client ID here>
client_secret=<Paste Client Secret here>
```

Now you can just provide IDs of submissions, and credidentials will be automatically picked up from the file:

```console
python -m redditmedia [IDS OF SUBMISSIONS SEPARATED WITH SPACE]
```

> You can do more things using this file, which is outside of the topic of this page. For details about `praw.ini` file, check out this page: [praw.ini Files](https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html)

## Upcoming features

- [ ] Loading submissions from a file
- [x] Easier credentials entering
- [ ] Add file size limit
- [ ] Save URLs into file
