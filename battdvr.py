import os
from pprint import pprint
from urllib.parse import urljoin
import json

import requests
import youtube_dl

from bs4 import BeautifulSoup
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
lucifer = 'http://www.fox.com/lucifer/full-episodes'
pitch = 'http://www.fox.com/pitch/full-episodes'
son_of_zorn = 'http://www.fox.com/son-of-zorn/full-episodes'
brooklyn_99 = 'http://www.fox.com/brooklyn-nine-nine/full-episodes'

tbbt = 'http://www.cbs.com/shows/big_bang_theory/video/'
tbg = 'http://www.cbs.com/shows/2_broke_girls/video/'
kcw = 'http://www.cbs.com/shows/kevin-can-wait/video/'

blackish = 'http://abc.go.com/shows/blackish/episode-guide'

all_shows = [
{'network': 'cw', 'url': lot, 'show_name':'Legends of Tomorrow'},
{'network': 'cw', 'url': arrow, },
{'network': 'cw', 'url': flash, 'series_directory':'The Flash (2014)', },
{'network': 'cw', 'url': supergirl, },
{'network': 'cbs'}
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

def uniq(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def get_episode_links_cw(url):
    tld = 'http://www.cwtv.com/'
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, 'lxml')
    result = []
    for link in soup.find(id='list_1').find_all('a'):
        result.append(urljoin(tld, link.get('href')))

    # print(result)
    return result

def get_episode_links_fox(url):
    tld = 'http://www.fox.com/'
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, 'lxml')
    all_links = []
    episode_wrapper_div = soup.find('div', 'pane-interior-show-episodes')
    for link in episode_wrapper_div.find_all('a'):
        all_links.append(urljoin(tld, link.get('href')))
    result = uniq(all_links)
    print(result)
    return result

def get_episode_links_cbs(url):
    tld = 'http://www.cbs.com/'
    # browser = webdriver.Chrome()
    # browser.get(url)

    # #delay = 3 # seconds
    # try:
    #     #WebDriverWait(s_browser, delay).until(EC.presence_of_element_located(s_browser.find_element_by_id('capture_signIn_userInformationForm')))
    #     login_form = WebDriverWait(browser, 3).until(
    #         EC.presence_of_element_located((By.ID, "capture_signIn_userInformationForm"))
    #     )
    #     print("Page is ready!")
    # except TimeoutException:
    #     print("Loading took too much time!")

    # video_wrapper_div = soup.find('div', 'cbs-show-content-full')
    # pprint(video_wrapper_div)

    # JSON URL for TBBT: http://www.cbs.com/carousels/videosBySection/237972/offset/0/limit/15/xs/0/10/
                       # http://www.cbs.com//carousels/videosBySection/237972/offset/0/limit/15/xs/0/10/

    r = requests.get(url)
    data = r.text
    video_json = None
    for item in data.split("\n"):
        if 'video.section_metadata' in item:
            video_json = item
            # print(video_json)
    if video_json is None:
        return []
    video_json = video_json.strip()
    video_json = video_json[video_json.startswith('video.section_metadata = ') and len('video.section_metadata = '):]
    video_json = video_json.rstrip(';')
    video_json_data = json.loads(video_json)
    # pprint(video_json_data)
    video_section_id = None
    for section_id, section_data in video_json_data.items():
        if section_data['title'] == 'Full Episodes':
            video_section_id = section_id
            break
    if video_section_id is None:
        return []
    episodes_url = urljoin(tld, '/carousels/videosBySection/{}/offset/0/limit/15/xs/0/'.format(video_section_id))
    episodes_r = requests.get(episodes_url)
    # print(episodes_url)
    # print(episodes_r.text)
    episodes_data = json.loads(episodes_r.text)
    result = []
    for episode in episodes_data['result']['data']:
        result.append(urljoin(tld,episode['url']))
    return result


def get_episode_links_abc(url):
    tld = 'http://abc.go.com/'
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, 'lxml')
    result = []
    episode_wrapper_div = soup.find_all('div', 'm-episode')
    for link in episode_wrapper_div:
        if link.get('data-videoid'):
            result.append(urljoin(tld, link.get('data-url')))
    print(result)
    return result

def get_filename(download_url, show_name=None, series_directory=None, has_season=True, has_episode_number=False, verbose=False):
    data = {}
    with youtube_dl.YoutubeDL({'quiet':True}) as ydl:
        ydl_info = ydl.extract_info(download_url, download=False)
        if show_name:
            data['show'] = show_name
        else:
            data['show'] = ydl_info['series']
        if series_directory:
            data['series_dir'] = series_directory
        else:
            data['series_dir'] = data['show']
        if verbose:
            pprint(ydl_info)
        if has_season:
            data['season_number'] = ydl_info['season_number']
            data['season_dir'] = 'Season {}'.format(season_number)
        if has_episode_number:
            data['season_episode_number'] = str(ydl_info['episode_number']).zfill(2)
        data['title'] = ydl_info['title']
        data['extension'] = ydl_info['ext']
    if has_season and has_episode_number:
        filename = "{} - {}x{} - {}.{}".format(show, season_number, season_episode_number, title, extension)
        result = os.path.join(check_directory, series_dir, season_dir, filename)
    else:
        filename = "{} - {}.{}".format(show, title, extension)
        result = os.path.join(check_directory, series_dir, filename)
    return result


def download(download_url, show_name=None, series_directory=None, has_season=True, has_episode_number=True, verbose=False, ):
    check_directory = '/Volumes/Public/Video/TV Shows/'
    if not os.path.exists(check_directory):
        print('Not connected to the end server')
    else:
        with youtube_dl.YoutubeDL({'quiet':True}) as ydl:
            ydl_info = ydl.extract_info(download_url, download=False)
            if show_name:
                show = show_name
            else:
                show = ydl_info['series']
            if series_directory:
                series_dir = series_directory
            else:
                series_dir = show
            if verbose:
                # pprint(ydl_info)
                print('Season: {} Episode: {}'.format(ydl_info['season_number'], ydl_info['episode_number']))
            if has_season:
                season_number = ydl_info['season_number']
                season_dir = 'Season {}'.format(season_number)
            if has_episode_number:
                season_episode_number = str(ydl_info['episode_number']).zfill(2)
            title = ydl_info['title']
            extension = ydl_info['ext']
        if has_season and has_episode_number:
            filename = "{} - {}x{} - {}.{}".format(show, season_number, season_episode_number, title, extension)
            full_path = os.path.join(check_directory, series_dir, season_dir, filename)
        else:
            filename = "{} - {}.{}".format(show, title, extension)
            full_path = os.path.join(check_directory, series_dir, filename)
        if os.path.exists(full_path):
            print('skipping {}'.format(full_path))
        else:
            print('DOWNLOAD: {} from {}'.format(full_path, download_url))
            while True:
                try:
                    with youtube_dl.YoutubeDL({'outtmpl': full_path}) as ydl:
                        ydl.download([download_url])
                    break
                except youtube_dl.utils.DownloadError as e:
                    print('Ran into {}, trying again...'.format(e))


# download_format = 'youtube-dl -o "%(series)s - %(season_number)sx%(episode_number)s - %(title)s.%(ext)s" '

# a = get_episode_links_cw(lot)
# f = get_episode_links_cw(flash)
# r = get_episode_links_cw(arrow)
# b = get_episode_links_cw(supergirl)

pprint(get_episode_links_cbs(tbbt))
pprint(get_episode_links_cbs(tbg))
pprint(get_episode_links_cbs(kcw))

# get_episode_links_abc(blackish)

# for i in a:
#     download(i, show_name='Legends of Tomorrow')
# for j in b:
#     download(j)
# for k in f:
#     download(k, series_directory='The Flash (2014)')
# for l in r:
#     download(l)

# download('http://www.cbs.com/shows/big_bang_theory/video/fDfEB6Bpziz0KY4WssUNAgFu2vWNH9m7/the-big-bang-theory-the-conjugal-conjecture/')

# for x in get_episode_links_fox(gotham):
#     download(x, show_name='Gotham', has_season=False, has_episode_number=False, series_directory='Gotham/Season 2')
# for y in get_episode_links_fox(family_guy):
#     download(y, show_name='Family Guy', has_season=False, has_episode_number=False)

