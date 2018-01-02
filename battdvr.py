import os
from pprint import pprint
from urllib.parse import urljoin
import json
import argparse
from battprefs import BattPrefs
import sys

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


# def get_prefs():
#     result = []
#     possible_conf_locations = [
#         os.path.join(os.path.expanduser('~'), '.config', __appname__, 'config'),
#         os.path.join(os.path.expanduser('~'), '.config', __appname__ + '.conf')
#     ]
#     found_conf_loc = None
#     for loc in possible_conf_locations:
#         if os.path.isfile(loc):
#             found_conf_loc = loc
#             break
#     if found_conf_loc:
#         with open(found_conf_loc, 'r') as f:
#             full_result = f.read()
#         result = json.loads(full_result)
#     return result


# youtube_dl configuration
# class ytdl_logger(object):
#     def debug(self, msg):
#         sys.stdout.write('\r\033[K')
#         sys.stdout.write(msg)
#         sys.stdout.flush()
#
#     def warning(self, msg):
#         print(msg)
#
#     def error(self, msg):
#         print(msg)

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

class BattDVR(BattPrefs):
    def __init__(self):
        super().__init__('battdvr')
        all_prefs = self._get_prefs()
        self.home_directory = all_prefs['home_directory']
        self.all_shows = all_prefs['shows']
        self.provider = all_prefs['provider']

        self.processor_for = {
            'cw': CWProcessor,
            'cbs': CBSProcessor,
            'abc': ABCProcessor,
            'fox': FOXProcessor,
            'fx': FXProcessor,
            'nbc': NBCProcessor,
            'syfy': SyFyProcessor
        }

    def _get_provider_opts(self):
        result = {}
        mapping = {'name': 'ap_mso', "username": 'ap_username', "password": 'ap_password'}
        for conf_name, opt_name in mapping.items():
            result[opt_name] = self.provider[conf_name]
        return result

    def _setup_show(self, show):
        show['home_directory'] = self.home_directory
        show['provider_opts'] = self._get_provider_opts()
        constructor = self.processor_for[show['network']]
        return constructor

    def check_links(self, show):
        constructor = self._setup_show(show)
        print('[{}]'.format(show['url']))
        show_processor = constructor(**show)
        episodes = show_processor.get_links(show['url'])
        pprint(episodes)

    def check_filenames(self, show):
        constructor = self._setup_show(show)
        print('[{}]'.format(show['url']))
        show_processor = constructor(**show)
        episodes = show_processor.get_links(show['url'])
        for episode in episodes:
            dest = show_processor.get_filename(episode)
            print(dest)

    def download_all(self, networks=None):
        downloaded_urls = []
        skipped_urls = []
        for show in self.all_shows:
            if networks and show['network'] not in networks:
                continue
            constructor = self._setup_show(show)
            print('[{}]'.format(show['url']))
            show_processor = constructor(**show)
            # show_processor.load_show(**show)
            episodes = show_processor.get_links(show['url'])
            for episode in episodes:
                dest = episode
                try:
                    dest = show_processor.get_filename(episode)
                    downloaded = show_processor.download(episode, dest)
                except youtube_dl.utils.DownloadError as e:
                    print('Cannot download {}. {}'.format(episode, e))
                    skipped_urls.append(dest)
                    continue
                except BaseException as e:
                    print('An error occurred when downloading {}: {}'.format(episode, e))
                    skipped_urls.append(dest)
                    continue
                if downloaded:
                    downloaded_urls.append(dest)
                else:
                    skipped_urls.append(dest)
        print('{} downloaded, {} skipped'.format(len(downloaded_urls), len(skipped_urls)))
        print('DOWNLOADED:\n', downloaded_urls)


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




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--networks', nargs='+', type=str, required=False)
    args = parser.parse_args()
    battdvr = BattDVR()
    battdvr.download_all(args.networks)
    # check_links({'network': 'nbc', 'url': superstore})
    # check_filenames({'network': 'nbc', 'url': superstore, 'show_name': 'Superstore',})
