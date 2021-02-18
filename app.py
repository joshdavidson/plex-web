import traceback

from flask import Flask, render_template, redirect, request, session, jsonify
from helpers import login_required, get_sections, get_users, get_playlists, check_activity, check_server, get_movies, \
    get_playlist_movies, get_collections, get_collection_movies
import json

from playlist import add_playlist_to_plex

app = Flask(__name__)

# configurations for session
app.config["SECRET_KEY"] = "07id2CFJSpRY5sQ3KEoZTjb6hoNfSFcI&&/a..#¤%//aaborpp"
app.config["SESSION_PERMANENT"] = False


@app.route("/connect", methods=["GET", "POST"])
def connect():
    if request.method == "GET":
        return render_template("connect.html.jinja")
    else:
        plex_url = request.form.get("plex-url")
        plex_token = request.form.get("plex-token")

        # check if plex server is available
        if check_server(plex_url, plex_token):
            session["plex_token"] = plex_token
            session["plex_url"] = plex_url
            return redirect("/")
        else:
            return redirect("/tryagain")


@app.route("/about")
def about():
    return render_template("about.html.jinja")


@app.route('/')
@login_required
def index():
    return render_template("index.html.jinja")


@app.route('/server')
@login_required
def server():
    users = get_users(session["plex_url"], session["plex_token"])
    return render_template("server.html.jinja", users=users)


@app.route('/collections')
@login_required
def collections():
    plex_collections = get_collections(session["plex_url"], session["plex_token"])
    collections = []
    for i, p_list in enumerate(plex_collections):
        collections.append({"title": p_list.title,
                            "id": f'collection-{i}',
                            })
    return render_template("collections.html.jinja", collections=collections)


@app.route('/playlists')
@login_required
def playlists():
    plex_playlists = get_playlists(session["plex_url"], session["plex_token"])

    playlists = []

    for i, p_list in enumerate(plex_playlists):
        playlists.append({"title": p_list.title,
                          "id": f'playlist-{i}',
                          })

    return render_template("playlists.html.jinja", playlists=playlists)


@app.route('/addplaylist')
@login_required
def addplaylist():
    sections = get_sections(session["plex_url"], session["plex_token"])
    users = get_users(session["plex_url"], session["plex_token"])

    data = {"sections": sections,
            "users": users}

    return render_template('addplaylist.html.jinja', data=data)


@app.route('/disconnect')
def disconnect():
    session.clear()
    return redirect("/")


@app.route('/tryagain')
def tryagain():
    return render_template("tryagain.html.jinja")


@app.route('/update_activity', methods=["POST"])
def update_activity():
    # get the username from the form
    users = request.form.getlist("users[]")
    user_dict = {}

    # get all active users from plex
    activity = check_activity(session["plex_url"], session["plex_token"])
    for user in users:
        # set standard to false
        user_dict[user] = {"active": False}

        for playing in activity:
            if str(playing.usernames[0]) == user:
                user_dict[user] = {"user": user,
                                   "show": playing.grandparentTitle if playing.type == "episode" else playing.title,
                                   "active": True}

    return jsonify(user_dict)


@app.route('/search', methods=["GET"])
def search():
    query = request.args.get("query")
    movies = get_movies(session["plex_url"], session["plex_token"], query)
    movies = [movie.title for movie in movies]
    return jsonify(movies=movies)


@app.route('/collectiondata', methods=["GET"])
def collectiondata():
    collection = request.args.get("collection")
    movies = get_collection_movies(
        session["plex_url"], session["plex_token"], collection)
    movies_json = jsonify(movies)
    return movies_json


@app.route('/playdata', methods=["GET"])
def playdata():
    playlist = request.args.get("playlist")
    movies = get_playlist_movies(
        session["plex_url"], session["plex_token"], playlist)
    movies_json = jsonify(movies)
    return movies_json


@app.route('/addplaylisttoplex', methods=["POST"])
def addplaylisttoplex():
    link = "https://www.imdb.com/list/"

    imdb = request.form.get('imdb')
    name = request.form.get('name')
    section = request.form.get('section')
    users = json.loads(request.form.get('users'))

    data = {"success": False,
            "error": "Something went wrong. Could not add the playlist to plex. Please try again.",
            "failed": []}

    try:
        failed_movies = add_playlist_to_plex(
            session["plex_url"], session["plex_token"], link + imdb, name, section, users)
        data["success"] = True
        data["error"] = None
        data["failed"] = failed_movies
    except IndexError:
        # gets raised when the list cannot be scraped.
        data["error"] = "Wrong list ID, could not retrieve data."
    except NameError as e:
        # gets raised when a user cannot access the library
        data["error"] = str(e)
    except Exception as e:
        # print error message to trace error
        print(traceback.print_exc())

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=False)
