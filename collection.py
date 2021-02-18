from helpers import scrape
from plexapi.server import PlexServer
import requests

URL_PAGE = "?&mode=detail&page="
HEADERS = {"Accept-Language": "en-US,en;q=0.5"}


def add_collection_to_plex(url, token, link, name, section):
    movies = scrape(link)
    collection, failed_movies = add_collection(movies, url, token, name)

    return failed_movies


def add_collection(url, token, name, library_key, rating_key):
    headers = {"X-Plex-Token": token}
    params = {"type": 1,
              "id": rating_key,
              "collection[0].tag.tag": name,
              "collection.locked": 1
              }

    url = "{base_url}/library/sections/{library}/all".format(base_url=url, library=library_key)
    r = requests.put(url, headers=headers, params=params)
