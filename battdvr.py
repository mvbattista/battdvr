import os
from pprint import pprint
from urllib.parse import urljoin
import json

import requests
import youtube_dl

from bs4 import BeautifulSoup

from networks import *

import importlib

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

lot = 'http://www.cwtv.com/shows/dcs-legends-of-tomorrow/'
flash = 'http://www.cwtv.com/shows/the-flash/'
arrow = 'http://www.cwtv.com/shows/arrow/'
supergirl = 'http://www.cwtv.com/shows/supergirl/'

gotham = 'http://www.fox.com/gotham/full-episodes'
family_guy = 'http://www.fox.com/family-guy/full-episodes'
new_girl = 'http://www.fox.com/new-girl/full-episodes'
lucifer = 'http://www.fox.com/lucifer/full-episodes'
pitch = 'http://www.fox.com/pitch/full-episodes'
son_of_zorn = 'http://www.fox.com/son-of-zorn/full-episodes'
brooklyn_99 = 'http://www.fox.com/brooklyn-nine-nine/full-episodes'
bobs_burgers = 'http://www.fox.com/bobs-burgers/full-episodes'
simpsons = 'http://www.fox.com/the-simpsons/full-episodes'

tbbt = 'http://www.cbs.com/shows/big_bang_theory/video/'
tbg = 'http://www.cbs.com/shows/2_broke_girls/video/'
kcw = 'http://www.cbs.com/shows/kevin-can-wait/video/'
scorpion = 'http://www.cbs.com/shows/scorpion/video/'
odd_couple = 'http://www.cbs.com/shows/the-odd-couple/video/'
mom = 'http://www.cbs.com/shows/mom/video/'
macgyver = 'http://www.cbs.com/shows/macgyver/video/'

blackish = 'http://abc.go.com/shows/blackish/episode-guide'
middle = 'http://abc.go.com/shows/the-middle/episode-guide'
american_housewife = 'http://abc.go.com/shows/american-housewife/episode-guide'
modern_family = 'http://abc.go.com/shows/modern-family/episode-guide'
shield = 'http://abc.go.com/shows/marvels-agents-of-shield/episode-guide'

superstore = 'http://www.nbc.com/superstore/episodes'
timeless = 'http://www.nbc.com/timeless/episodes'
good_place = 'http://www.nbc.com/the-good-place/episode'

all_shows = [
{'network': 'cw', 'url': lot, 'show_name':'Legends of Tomorrow'},
{'network': 'cw', 'url': arrow, },
{'network': 'cw', 'url': flash, 'series_directory':'The Flash (2014)', },
{'network': 'cw', 'url': supergirl, },

{'network': 'cbs', 'url': tbbt},
{'network': 'cbs', 'url': tbg},
{'network': 'cbs', 'url': kcw},
{'network': 'cbs', 'url': scorpion},
{'network': 'cbs', 'url': odd_couple},
{'network': 'cbs', 'url': mom},
{'network': 'cbs', 'url': macgyver, 'series_directory':'MacGyver (2016)', },

{'network': 'abc', 'url': blackish, 'show_name':'Blackish'},
{'network': 'abc', 'url': middle,},
{'network': 'abc', 'url': american_housewife,},
{'network': 'abc', 'url': modern_family,},
{'network': 'abc', 'url': shield, 'series_directory': 'Marvel/Agents of S.H.I.E.L.D.'},

{'network': 'fox', 'url': gotham, 'show_name':'Gotham'},
{'network': 'fox', 'url': new_girl, 'show_name':'New Girl'},
{'network': 'fox', 'url': family_guy, 'show_name':'Family Guy'},
{'network': 'fox', 'url': lucifer, 'show_name':'Lucifer'},
{'network': 'fox', 'url': pitch, 'show_name':'Pitch'},
{'network': 'fox', 'url': son_of_zorn, 'show_name':'Son of Zorn'},
{'network': 'fox', 'url': brooklyn_99, 'show_name':'Brooklyn Nine Nine'},
{'network': 'fox', 'url': bobs_burgers, 'show_name':"Bob's Burgers"},
{'network': 'fox', 'url': simpsons, 'show_name':'The Simpsons'},

{'network': 'nbc', 'url': superstore, 'show_name': 'Superstore'},
{'network': 'nbc', 'url': timeless, 'show_name': 'Timeless'},
{'network': 'nbc', 'url': good_place, 'show_name': 'The Good Place'},
]

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

