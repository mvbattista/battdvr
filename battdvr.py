import os
from pprint import pprint
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import youtube_dl

lot = 'http://www.cwtv.com/shows/dcs-legends-of-tomorrow/'
flash = 'http://www.cwtv.com/shows/the-flash/'
arrow = 'http://www.cwtv.com/shows/arrow/'
supergirl = 'http://www.cwtv.com/shows/supergirl/'
gotham = 'http://www.fox.com/gotham/full-episodes'
family_guy = 'http://www.fox.com/family-guy/full-episodes'

tbbt = 'http://www.cbs.com/shows/big_bang_theory/video/'

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

ytdl_opts = {
    # 'format': 'bestaudio/best',
    # 'outtmpl': '%(id)s.%(ext)s',
    # 'postprocessors': [{
    #     'key': 'FFmpegExtractAudio',
    #     'preferredcodec': 'mp3',
    #     'preferredquality': '0',
    # }],
    #'logger': ytdl_logger(),
    #'progress_hooks': [ytdl_hook],
    'quiet': True
}

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

def get_episode_links(url):
    tld = 'http://www.cwtv.com/'
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, 'lxml')
    result = []
    for link in soup.find(id='list_1').find_all('a'):
        result.append(urljoin(tld, link.get('href')))

    print(result)
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
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, 'lxml')
    video_wrapper_div = soup.find('div', 'cbs-show-content-full')
    pprint(video_wrapper_div)


def download(download_url, show_name=None, series_directory=None, has_season=True, has_episode_number=False):
    check_directory = '/Volumes/Public/Video/TV Shows/'
    if not os.path.exists(check_directory):
        print('Not connected to the end server')
    else:
        with youtube_dl.YoutubeDL(quiet=True) as ydl:
            ydl_info = ydl.extract_info(download_url, download=False)
            if show_name:
                show = show_name
            else:
                show = ydl_info['series']
            if series_directory:
                series_dir = series_directory
            else:
                series_dir = show
            # pprint(ydl_info)
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
            print(full_path)
        else:
            print('DOWNLOAD: {}'.format(full_path))


# download_format = 'youtube-dl -o "%(series)s - %(season_number)sx%(episode_number)s - %(title)s.%(ext)s" '

# a = get_episode_links(lot)
# f = get_episode_links(flash)
# r = get_episode_links(arrow)
# b = get_episode_links(supergirl)

get_episode_links_cbs(tbbt)

# for i in a:
#     download(i, show_name='Legends of Tomorrow')
# for j in b:
#     download(j)
# for k in f:
#     download(k, series_directory='The Flash (2014)')
# for l in r:
#     download(l)

# for x in get_episode_links_fox(gotham):
#     download(x, show_name='Gotham', has_season=False, has_episode_number=False, series_directory='Gotham/Season 2')
# for y in get_episode_links_fox(family_guy):
#     download(y, show_name='Family Guy', has_season=False, has_episode_number=False)

