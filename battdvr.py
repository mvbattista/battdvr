from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
from pprint import pprint

lot = 'http://www.cwtv.com/shows/dcs-legends-of-tomorrow/'
flash = 'http://www.cwtv.com/shows/the-flash/'
arrow = 'http://www.cwtv.com/shows/arrow/'
supergirl = 'http://www.cwtv.com/shows/supergirl/'
gotham = 'http://www.fox.com/gotham/full-episodes'
family_guy = 'http://www.fox.com/family-guy/full-episodes'

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

download_format = 'youtube-dl -o "%(series)s - %(season_number)sx%(episode_number)s - %(title)s.%(ext)s" '

# get_episode_links(lot)
# get_episode_links(flash)
# get_episode_links(arrow)
# get_episode_links(supergirl)

get_episode_links_fox(gotham)
get_episode_links_fox(family_guy)