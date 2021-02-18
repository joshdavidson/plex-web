from helpers import scrape
from plexapi.server import PlexServer


def add_playlist_to_plex(url, token, link, name, section, users):
    movies = scrape(link)
    playlist, failed_movies = add_playlist(movies, url, token, name)

    if len(users) > 0:
        copy_to_users(playlist, users)

    return failed_movies


def add_playlist(name_list, url, token, name):
    movie_list = []
    failed_movies = []

    for movie in name_list:

        # create the movie dict item
        movie = name_list[movie]

        # get movie if it exists
        temp = get_movie(movie, url, token)

        # loop if it can't find the movie
        if temp is False:
            failed_movies.append(movie["title"])
            continue

        # add to list if it can find it
        movie_list.append(temp)

    # create playlist
    playlist = PlexServer(url, token).createPlaylist(name, movie_list)

    return playlist, failed_movies


def get_movie(movie, url, token):
    results = PlexServer(url, token).search(movie["title"])

    # return movie if it exists
    for plex_movie in results:

        if plex_movie.type == "movie" and str(plex_movie.year) in str(movie["year"]):
            return plex_movie

    return False


def copy_to_users(playlist, users):
    for user in users:
        try:
            playlist.copyToUser(user)
        except:
            raise NameError(f"{user} does not have access to the library.")
