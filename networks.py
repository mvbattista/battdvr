import json
import os
from pprint import pprint
from urllib.parse import urljoin, urlparse

import requests
import youtube_dl
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

        
class BaseNetwork(object):
    """docstring for base network"""

    def __init__(self, **kwargs):
        self.show_name = None
        self.series_directory = None
        self.has_season = True
        self.has_episode_number = True
        self.verbose = False
        self.data_from_tvmaze = False
        self.tvmaze_show_id = None
        self.tvmaze_episode_data = None
        self.home_directory = ''
        self.provider_opts = {}
        self.extra_opts = {}

        # self.__dict__.update(kwargs)

    # def load_show(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_links(self, url):
        raise NotImplementedError('get_links required for all processors.')

    def rename_title(self, title):
        return title

    def get_filename(self, url):
        ytdl_opts = {
            'quiet': True,
        }
        ytdl_opts.update(self.provider_opts)
        ytdl_opts.update(self.extra_opts)
        with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
            ydl_info = ydl.extract_info(url, download=False)
            if self.verbose:
                pprint(ydl_info)
            
            show = self.show_name if self.show_name else ydl_info['series']
            season_number = None
            season_episode_number = None
            season_dir = None

            title = ydl_info['title']
            title = self.rename_title(title)

            series_dir = self.series_directory if self.series_directory else show

            if self.data_from_tvmaze:
                episode_info = self._get_tvmaze_data(show, title)
                season_number = episode_info['season']
                season_dir = 'Season {}'.format(season_number)
                season_episode_number = '00' if episode_info['number'] is None else str(episode_info['number']).zfill(2)

            else:
                if self.has_season:
                    season_number = ydl_info['season_number']
                    season_dir = 'Season {}'.format(season_number)
                if self.has_episode_number:
                    season_episode_number = str(ydl_info['episode_number']).zfill(2)
            extension = ydl_info['ext']

            # Escape forward slashes in title
            # I don't know why, but, for some reason, this works.
            # It doesn't show on the terminal, but the files get named right.
            title = title.replace('/', ':')

        # if self.has_season and self.has_episode_number:
            filename = "{} - {}x{} - {}.{}".format(show, season_number, season_episode_number, title, extension)
            result = os.path.join(self.home_directory, series_dir, season_dir, filename)
        # else:
        #     self._get_tvmaze_data(show, title)
        #     filename = "{} - {}.{}".format(show, title, extension)
        #     result = os.path.join(HOME_DIRECTORY, series_dir, filename)
            return result

    def download(self, url, full_path):
        if os.path.exists(full_path):
            print('skipping {}'.format(full_path))
            return False
        else:
            print('DOWNLOAD: {} from {}'.format(full_path, url))
            ytdl_opts = {
                'quiet': True,
                'outtmpl': full_path
            }
            ytdl_opts.update(self.provider_opts)
            ytdl_opts.update(self.extra_opts)
            while True:
                try:
                    with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
                        ydl.download([url])
                    break
                except youtube_dl.utils.DownloadError as e:
                    print('Ran into {}, trying again...'.format(e))
            return True

    def _get_tvmaze_data(self, show, title):
        show_r = requests.get('http://api.tvmaze.com/search/shows', params={'q': show})
        show_search_data = json.loads(show_r.text)
        best_show_ratio = 0
        best_show_name = None
        if not self.tvmaze_show_id:
            for i in show_search_data:
                show_ratio = fuzz.ratio(show, i['show']['name'])
                if  show_ratio > best_show_ratio:
                # name_match_ratio = SequenceMatcher(None, show.lower(),
                #                                    show_search_data[i]['show']['name'].lower()).ratio()
                # if name_match_ratio > 0.9:
                    self.tvmaze_show_id = i['show']['id']
                    best_show_ratio = show_ratio
                    best_show_name = i['show']['name']
                    break
            if self.tvmaze_show_id is None:
                raise ValueError('Could not match TV show data')
            print('I believe the show name is {}'.format(best_show_name))

        if not self.tvmaze_episode_data:
            episode_r = requests.get('http://api.tvmaze.com/shows/{}/episodes?specials=1'.format(self.tvmaze_show_id))
            self.tvmaze_episode_data = json.loads(episode_r.text)
        best_ratio = 0
        best_obj = None
        for i in self.tvmaze_episode_data:
            episode_ratio = fuzz.ratio(title, i['name'])
            # print('{} - {} = {}'.format(title, i['name'], episode_ratio))
            if episode_ratio > best_ratio:
                best_ratio = episode_ratio
                best_obj = i
        print('I believe the episode name is {} (s{} e{})'.format(best_obj['name'],
                                                                  best_obj['season'],
                                                                  best_obj['number']))
        return best_obj


class CWProcessor(BaseNetwork):
    """docstring for CW"""
    tld = 'http://www.cwtv.com'
    network = 'The CW'

    def __init__(self, **kwargs):
        super(CWProcessor, self).__init__(**kwargs)
        # Download best mp4 format available or any other best if no mp4 available
        self.extra_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        }

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
    tld = 'http://www.cbs.com'
    network = 'CBS'

    def get_links(self, url):
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, 'lxml')
        latest_episodes = soup.find(id='latest-episodes')
        if latest_episodes:
            season = latest_episodes.attrs.get('data-season')
            slug = latest_episodes.attrs.get('data-slug')
        else:
            # Older version, not using carousel sections.
            video_json = None
            for item in data.split("\n"):
                if 'section_metadata' in item and 'var $module' in item:
                    video_json = item

            if video_json is None:
                return []
            video_json = video_json.strip()
            video_json = video_json[video_json.startswith('var $module = ') and
                                    len('var $module = '):]
            video_json = video_json.rstrip(';')
            video_json_data = json.loads(video_json)
            season = video_json_data.get('video', {}).get('season_number')
            slug = video_json_data.get('base_url_video', '///').split('/')[2]

            if not season or not slug:
                return []

        offset = 0
        page_limit = 15
        first_loop = True
        total_episodes = 0
        result = []

        api_url = '/shows/{slug}/xhr/episodes/page/{page}/size/{page_limit}/xs/0/season/{season}/'
        while True:
            episodes_url = urljoin(self.tld, api_url.format(slug=slug, page=offset, page_limit=page_limit,
                                                            season=season))
            episodes_r = requests.get(episodes_url)
            episodes_data = json.loads(episodes_r.text)

            if first_loop:
                total_episodes = episodes_data['result']['total']
            for episode in episodes_data['result']['data']:
                if not episode['is_paid_content'] and episode['type'] == 'Full Episode':
                    result.append(urljoin(self.tld, episode['url']))

            if offset + page_limit < total_episodes:
                offset += 1
                first_loop = False
            else:
                break
        return result

    def rename_title(self, title):
        try:
            return title.split(' - ', 1)[1]
        except IndexError:
            return title.split('-', 1)[1].strip()


class OldFOXProcessor(BaseNetwork):
    """docstring for FOX"""
    tld = 'http://www.fox.com'
    network = 'FOX'
    episode_div = 'SeriesDetail_tabContent'

    def __init__(self, **kwargs):
        super(OldFOXProcessor, self).__init__(**kwargs)
        if not self.show_name:
            raise ValueError('show_name required for FOX shows')

    @staticmethod
    def _uniq(seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    def get_links(self, url):
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, 'lxml')
        all_links = []
        episode_wrapper_div = next(iter(soup.select("div[class^=" + self.episode_div + "]")), None)
        try:
            for link in episode_wrapper_div.find_all('a'):
                all_links.append(urljoin(self.tld, link.get('href')))
        except AttributeError:
            print('No episodes found at {}'.format(url))
        result = self._uniq(all_links)

        return result


class FXProcessor(OldFOXProcessor):
    tld = 'http://www.fxnetworks.com'
    network = 'FX'

    def __init__(self, **kwargs):
        super(FXProcessor, self).__init__(**kwargs)
        self.has_season = False
        self.has_episode_number = False
        self.data_from_tvmaze = True
        self.episode_div = 'episode-accordian'


class FOXProcessor(BaseNetwork):
    tld = 'https://www.fox.com'
    network = 'FOX'

    def __init__(self, **kwargs):
        super(FOXProcessor, self).__init__(**kwargs)
        if os.path.isfile('fox_cookies.txt'):
            self.extra_opts = {
                'cookiefile': os.path.abspath('fox_cookies.txt'),
                # 'verbose': True
            }
        pass

    def get_links(self, url):
        url_path = urlparse(url).path.lstrip('/')
        series_alias = url_path.split('/')[0]
        series_info_url = 'https://api2.fox.com/v2.0/series/{}'.format(series_alias)
        network_headers = {'x-api-key': 'abdcbed02c124d393b39e818a4312055'}
        series_info_r = requests.get(series_info_url, headers=network_headers)
        series_data = series_info_r.json()
        latest_season = series_data['currentSeason']['seasonNumber']
        oldest_season = series_data['oldestEpisode'].get('seasonNumber', latest_season)
        result = []
        episodes_url = 'https://api2.fox.com/v2.0/seasons/{}/episodes/'
        watch_url = 'https://www.fox.com/watch/{}'
        for x in range(oldest_season, latest_season + 1):
            season = str(x).zfill(2)
            season_id = series_alias + '_' + season
            season_url = episodes_url.format(season_id)
            season_info_r = requests.get(season_url, headers=network_headers)
            season_data = season_info_r.json()
            for episode in season_data.get('member', []):
                episode_id = episode['id']
                result.append(watch_url.format(episode_id))
        return result


class ABCProcessor(BaseNetwork):
    """docstring for ABC"""
    tld = 'http://abc.go.com'
    network = 'ABC'

    def __init__(self, **kwargs):
        super(ABCProcessor, self).__init__(**kwargs)
        self.extra_opts = {
            'geo_bypass': False
        }


    def get_links(self, url):
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, 'lxml')
        result = []
        episode_divs = soup.find_all('div', 'tilegroup--shows')
        for episode_div in episode_divs:
            links = episode_div.find_all('a')
            for link in links:
                # if link.get('data-video-id'):
                    result.append(urljoin(self.tld, link.get('href')))
                    # result.append(urljoin(self.tld, link.get('data-url')))

        return result


class NBCProcessor(BaseNetwork):
    """docstring for NBC"""
    tld = 'http://www.nbc.com'
    network = 'NBC'

    def __init__(self, **kwargs):
        super(NBCProcessor, self).__init__(**kwargs)
        # self.has_season = False
        # self.has_episode_number = False
        # self.data_from_tvmaze = True
        # if not self.show_name:
        #     raise ValueError('show_name required for NBC shows.')

    def get_links(self, url):
        url_path = urlparse(url).path.lstrip('/')
        series_alias = url_path.split('/')[0]
        series_info_url = 'https://api.nbc.com/v3.14/shows'
        series_info_r = requests.get(series_info_url, params={'filter[name]': series_alias})
        series_data = series_info_r.json()
        series_id = series_data['data'][0]['id']
        episode_params = {
            'filter[show]': series_id,
            'filter[type][value]': 'Full Episode',
            'page[number]': 1,
            'page[size]': 10
        }
        next_in_resp = True
        result = []
        episode_url = 'https://api.nbc.com/v3.14/videos'
        while next_in_resp:
            if episode_params:
                episode_r = requests.get(episode_url, params=episode_params)
            else:
                episode_r = requests.get(episode_url)
            episode_data = episode_r.json()
            for episode in episode_data.get('data', []):
                # episode_id = episode['id']
                result.append(episode['attributes']['fullUrl'])
            if 'next' not in episode_data['links']:
                # mediaURL or fullURL
                next_in_resp = False
            else:
                episode_params = None
                episode_url = episode_data['links']['next']

        # r = requests.get(url)
        # data = r.text
        # soup = BeautifulSoup(data, 'lxml')
        # result = []
        # for episode in soup.find_all('article'):
        #     link = episode.find('a')
        #     result.append(urljoin(self.tld, link.get('href')))

        return result




class SyFyProcessor(BaseNetwork):
    tld = 'http://www.syfy.com'
    network = 'SyFy'

    def __init__(self, **kwargs):
        super(SyFyProcessor, self).__init__(**kwargs)
        # self.has_season = False
        # self.has_episode_number = False
        self.data_from_tvmaze = True
        if not self.show_name:
            raise ValueError('show_name required for SyFy shows.')

    def get_links(self, url):
        pagination_url = url
        result = []
        while pagination_url:
            r = requests.get(pagination_url)
            data = r.text
            soup = BeautifulSoup(data, 'lxml')
            # view-display-id-pane_related_episodes_by_show
            episodes = soup.find('div', class_='view-full-episodes')
            for episode in episodes.find_all('div', class_='grid-item'):
                link = episode.find('a')
                result.append(urljoin(self.tld, link.get('href')))
            next_page = episodes.find('li', class_='pager-next')
            next_link = next_page.find('a')
            if next_link:
                pagination_url = urljoin(self.tld, next_link.get('href'))
            else:
                pagination_url = None

        return result


class CrackleProcessor(BaseNetwork):
    tld = 'http://www.crackle.com'
    network = 'Crackle'
    # Visiting the URL to download will allow the file to be downloaded

    def get_links(self, url):
        show_slug = urlparse(url).path.split('/')[1]
        show_api_url = 'https://web-api-us.crackle.com/Service.svc/playback/channel/{}/US?format=json'
        show_r = requests.get(show_api_url.format(show_slug))
        show_data = show_r.json()
        if show_data['status']['messageCode'] != '0':
            return []
        show_id = show_data['Result']['ChannelId']
        episode_api_url = 'https://web-api-us.crackle.com/Service.svc/channel/{}/playlists/all/US?format=json'
        episode_r = requests.get(episode_api_url.format(show_id))
        episode_data = episode_r.json()
        if episode_data['Status']['messageCode'] != '0':
            return []
        episode_playlist = [x for x in episode_data['Playlists'] if x['PlaylistName'] == 'Episodes'][0]
        episode_ids = [x['MediaInfo']['Id'] for x in episode_playlist['Items']]
        result = ['/'.join((self.tld, show_slug, str(x))) for x in episode_ids]
        return result

class AdultSwimProcessor(BaseNetwork):
    tld = 'http://www.adultswim.com'
    network = 'Adult Swim'

    def get_links(self, url):
        pass

