import os
from pprint import pprint
from urllib.parse import urljoin
import json
from difflib import SequenceMatcher

import requests
import youtube_dl

from bs4 import BeautifulSoup

PROCESSOR_FOR = {
    'cw': 'CWProcessor',
    'cbs': 'CBSProcessor',
    'abc': 'ABCProcessor',
    'fox': 'FOXProcessor',
}
HOME_DIRECTORY = '/Volumes/Public/Video/TV Shows/'

        
class BaseNetwork(object):
    """docstring for base network"""

    def __init__(self, **kwargs):
        self.show_name = None
        self.series_directory = None
        self.has_season = True
        self.has_episode_number = True
        self.verbose = False
        self.data_from_tvmaze = False

        # self.__dict__.update(kwargs)

    def load_show(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_links(self, url):
        print('This is the get_links function')

    def rename_title(self, title):
        return title

    def get_filename(self, url):
        with youtube_dl.YoutubeDL({'quiet':True}) as ydl:
            ydl_info = ydl.extract_info(url, download=False)
            if self.show_name:
                show = self.show_name
            else:
                show = ydl_info['series']
            title = ydl_info['title']
            title = self.rename_title(title)

            # TODO - Add the API 

            if self.series_directory:
                series_dir = self.series_directory
            else:
                series_dir = show

            if self.verbose:
                pprint(ydl_info)

            if self.has_season:
                season_number = ydl_info['season_number']
                season_dir = 'Season {}'.format(season_number)
            if self.has_episode_number:
                season_episode_number = str(ydl_info['episode_number']).zfill(2)
            extension = ydl_info['ext']

        if self.has_season and self.has_episode_number:
            filename = "{} - {}x{} - {}.{}".format(show, season_number, season_episode_number, title, extension)
            result = os.path.join(HOME_DIRECTORY, series_dir, season_dir, filename)
        else:
            filename = "{} - {}.{}".format(show, title, extension)
            result = os.path.join(HOME_DIRECTORY, series_dir, filename)
        return result

        # print('This is the get_filename function')

    def download(self, url, full_path):
        if os.path.exists(full_path):
            print('skipping {}'.format(full_path))
        else:
            print('DOWNLOAD: {} from {}'.format(full_path, url))
            while True:
                try:
                    with youtube_dl.YoutubeDL({'outtmpl': full_path}) as ydl:
                        ydl.download([url])
                    break
                except youtube_dl.utils.DownloadError as e:
                    print('Ran into {}, trying again...'.format(e))


    def _get_tvmaze_data(self, show, title):
        show_r = requests.get('http://api.tvmaze.com/search/shows', params={'q':show})
        show_search_data = json.loads(show_r.text)
        show_id = None
        for i in show_search_data:
            name_match_ratio = SequenceMatcher(None, show.lower(), show_search_data[i]['show']['name'].lower()).ratio()
            if name_match_ratio > 0.9:
                show_id = show_search_data[i]['show']['id']
                break
        if show_id is None:
            raise ValueError('Could not match TV show data')

        episode_r = requests.get('http://api.tvmaze.com/shows/{}/episodes'.format(show_id))
        # TODO - Complete this for FOX



class CWProcessor(BaseNetwork):
    """docstring for CW"""
    tld = 'http://www.cwtv.com/'

    def get_links(self, url):
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, 'lxml')
        result = []
        for link in soup.find(id='list_1').find_all('a'):
            result.append(urljoin(self.tld, link.get('href')))

        return result


class CBSProcessor(BaseNetwork):
    """docstring for CBS"""
    tld = 'http://www.cbs.com/'

    def get_links(self, url):
        r = requests.get(url)
        data = r.text
        video_json = None
        for item in data.split("\n"):
            if 'video.section_metadata' in item:
                video_json = item

        if video_json is None:
            return []
        video_json = video_json.strip()
        video_json = video_json[video_json.startswith('video.section_metadata = ') and len('video.section_metadata = '):]
        video_json = video_json.rstrip(';')
        video_json_data = json.loads(video_json)

        video_section_id = None
        for section_id, section_data in video_json_data.items():
            if section_data['title'] == 'Full Episodes':
                video_section_id = section_id
                break
        if video_section_id is None:
            return []
        episodes_url = urljoin(self.tld, '/carousels/videosBySection/{}/offset/0/limit/15/xs/0/'.format(video_section_id))
        episodes_r = requests.get(episodes_url)

        episodes_data = json.loads(episodes_r.text)
        result = []
        for episode in episodes_data['result']['data']:
            result.append(urljoin(self.tld,episode['url']))
        return result

    def rename_title(self, title):
        return title.split(' - ', 1)[1]


class FOXProcessor(BaseNetwork):
    """docstring for FOX"""
    tld = 'http://www.fox.com/'

    def __init__(self, **kwargs):
        super().__init__()
        self.has_season = False
        self.has_episode_number = False

    @staticmethod
    def __uniq(seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    def get_links(self, url):
        if self.show_name is None:
            raise ValueError('show_name is required for FOXProcessor')
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, 'lxml')
        all_links = []
        episode_wrapper_div = soup.find('div', 'pane-interior-show-episodes')
        for link in episode_wrapper_div.find_all('a'):
            all_links.append(urljoin(self.tld, link.get('href')))
        result = self.__uniq(all_links)

        return result


class ABCProcessor(BaseNetwork):
    """docstring for ABC"""
    tld = 'http://abc.go.com/'

    def get_links(self, url):
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, 'lxml')
        result = []
        episode_wrapper_div = soup.find_all('div', 'm-episode')
        for link in episode_wrapper_div:
            if link.get('data-video-id'):
                result.append(urljoin(self.tld, link.get('data-url')))

        return result

