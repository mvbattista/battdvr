from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
from pprint import pprint

lot = 'http://www.cwtv.com/shows/dcs-legends-of-tomorrow/'
flash = 'http://www.cwtv.com/shows/the-flash/'
arrow = 'http://www.cwtv.com/shows/arrow/'
supergirl = 'http://www.cwtv.com/shows/supergirl/'

def get_episode_links(url):
    tld = 'http://www.cwtv.com/'
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, 'lxml')
    result = []
    for link in soup.find(id='list_1').find_all('a'):
        result.append(urljoin(tld, link.get('href')))

    print(result)

download_format = 'youtube-dl -o "%(series)s - %(season_number)sx%(episode_number)s - %(title)s.%(ext)s" '

get_episode_links(lot)
get_episode_links(flash)
get_episode_links(arrow)
get_episode_links(supergirl)

