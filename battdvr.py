import os
from pprint import pprint
from urllib.parse import urljoin
import json

import requests
import youtube_dl

from bs4 import BeautifulSoup

from networks import *

import importlib

__author__ = 'Michael V. Battista'
__copyright__ = 'Copyright 2016, Open Source'
__credits__ = []
__license__ = 'GPL'
__version__ = '0.7.0'
__maintainer__ = "Michael V. Battista"
__email__ = "battdvr@mvbattista.com"
__status__ = "Development"
__appname__ = 'battdvr'


def get_prefs():
    result = []
    possible_conf_locations = [ 
        os.path.join(os.path.expanduser('~'), '.config', __appname__, 'config'),
        os.path.join(os.path.expanduser('~'), '.config', __appname__ + '.conf')
    ]
    found_conf_loc = None
    for loc in possible_conf_locations:
        if os.path.isfile(loc):
            found_conf_loc = loc
            break
    if found_conf_loc:
        with open(found_conf_loc, 'r') as f:
            full_result = f.read()
        result = json.loads(full_result)
    return result


# youtube_dl configuration
class ytdl_logger(object):
    def debug(self, msg):
        sys.stdout.write('\r\033[K')
        sys.stdout.write(msg)
        sys.stdout.flush()

    def warning(self, msg):
        print(msg)
        
    def error(self, msg):
        print(msg)

# ytdl_opts = {
#     'format': 'bestaudio/best',
#     'outtmpl': '%(id)s.%(ext)s',
#     'postprocessors': [{
#         'key': 'FFmpegExtractAudio',
#         'preferredcodec': 'mp3',
#         'preferredquality': '0',
#     }],
#     'logger': ytdl_logger(),
#     'progress_hooks': [ytdl_hook],
#     'quiet': True
# }

def ytdl_hook(d):
    if d['status'] == 'downloading':
        sys.stdout.write('\r\033[K')
        sys.stdout.write('\tDownloading video | ETA: ' 
                            + str(d["eta"]) + " seconds")
        sys.stdout.flush()
    elif d['status'] == 'finished':
        sys.stdout.write('\r\033[K')
        sys.stdout.write('\tDownload complete\n\tConverting video to mp3')
        sys.stdout.flush()

# download_format = 'youtube-dl -o "%(series)s - %(season_number)sx%(episode_number)s - %(title)s.%(ext)s" '

def download_all():
    downloaded_urls = []
    skipped_urls = []
    all_shows = get_prefs()
    for show in all_shows:
        constructor = PROCESSOR_FOR[show['network']]
        print('[{}]'.format(show['url']))
        show_processor = constructor(**show)
        # show_processor.load_show(**show)
        episodes = show_processor.get_links(show['url'])
        for episode in episodes:
            try:
                dest = show_processor.get_filename(episode)
                downloaded = show_processor.download(episode, dest)
            except youtube_dl.utils.DownloadError as e:
                print ('Cannot download {} due to network limitations.'.format(episode))
                skipped_urls.append(episode)
                continue
            if downloaded:
                downloaded_urls.append(episode)
            else:
                skipped_urls.append(episode)
    print('{} downloaded, {} skipped'.format(len(downloaded_urls), len(skipped_urls)))
    print('DOWNLOADED:\n', downloaded_urls)

def check_links(show):
    constructor = PROCESSOR_FOR[show['network']]
    print('[{}]'.format(show['url']))
    show_processor = constructor(**show)
    episodes = show_processor.get_links(show['url'])
    pprint(episodes)

def check_filenames(show):
    constructor = PROCESSOR_FOR[show['network']]
    print('[{}]'.format(show['url']))
    show_processor = constructor(**show)
    episodes = show_processor.get_links(show['url'])
    for episode in episodes:
        dest = show_processor.get_filename(episode)
        print(dest)


if __name__ == '__main__':
    download_all()
    # check_links({'network': 'nbc', 'url': superstore})
    # check_filenames({'network': 'nbc', 'url': superstore, 'show_name': 'Superstore',})

