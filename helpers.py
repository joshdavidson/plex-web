import requests
from bs4 import BeautifulSoup
from flask import redirect, session
from functools import wraps
from plexapi.server import PlexServer


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("plex_token") is None:
            return redirect("/connect")
        return f(*args, **kwargs)

    return decorated_function


def get_users(url, token):
    return [user.title for user in PlexServer(url, token).myPlexAccount().users() if user.friend]


def check_server(url, token):
    try:
        plex = PlexServer(url, token)
        return True
    except:
        return False


def check_activity(url, token):
    return [client for client in PlexServer(url, token).sessions()]


def get_movies(url, token, query):
    return PlexServer(url, token).search(query)


def get_collections(url, token):
    return PlexServer(url, token).library.section('Movies').collections()


def get_playlists(url, token):
    return PlexServer(url, token).playlists()


def get_playlist_movies(url, token, playlist):
    movies = PlexServer(url, token).playlist(playlist)

    movie_list = []

    for movie in movies.items():
        movie_list.append({"title": movie.title,
                           "guid": str(movie.guids[0]).split('imdb://')[1].split('?')[0].replace('>', ''),
                           "year": movie.year,
                           "rating": movie.audienceRating})

    return movie_list


def get_collection_movies(url, token, collectionName):
    results = PlexServer(url, token).library.section('Movies').search(collection=collectionName)
    movie_list = []
    for movie in results:
        guid_str = str(movie.guids[0]).split("imdb://")[1].split('?')[0].replace('>', '')
        movie_list.append({"title": movie.title,
                           "guid": guid_str,
                           "year": movie.year,
                           "rating": movie.audienceRating})
    return movie_list


def get_sections(url, token):
    return [section.title for section in PlexServer(url, token).library.sections() if section.type == "movie"]

URL_PAGE = "?&mode=detail&page="
HEADERS = {"Accept-Language": "en-US,en;q=0.5"}
def scrape(website):
    # create lists that takes all data from every loop
    movie_final = []
    year_final = []

    k = 1
    while True:

        html = requests.get(website + URL_PAGE + str(k), headers=HEADERS)
        soup = BeautifulSoup(html.content, "lxml")

        # find popular movies and years, and convert to list
        movies = soup.select(
            '#main > div > div.lister.list.detail.sub-list > div.lister-list > div > div.lister-item-content > h3 > a')
        years = soup.select(
            "#main > div > div.lister.list.detail.sub-list > div.lister-list > div > div.lister-item-content > h3 > span.lister-item-year.text-muted.unbold"
        )

        # break if there are not movies left
        if len(movies) == 0:
            break

        # get all movie titles and years
        movies_string = [movie.get_text() for movie in movies]
        years_int = [year.get_text().replace("(", "") for year in years]
        years_int = [year.replace(")", "") for year in years_int]
        years_int = [year.replace("I ", "") for year in years_int]

        # append all movies that are scraped
        movie_final = movie_final + movies_string.copy()
        year_final = year_final + years_int.copy()

        # loop
        k += 1

    # create dict for each movie
    movie_list = {}
    for i, movie in enumerate(movie_final):
        movie_list[movie] = {"title": movie, "year": year_final[i]}

    return movie_list
