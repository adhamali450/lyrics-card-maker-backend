from flask import Flask, jsonify, request
from flask_cors import CORS
from lyricsgenius import Genius
from utils import add_stats, img_to_base64
from colors import dominant_colors
import requests
from urllib.parse import unquote
import base64
from dropbox import Dropbox
from dotenv import load_dotenv
import os
os.system('cls' if os.name == 'nt' else 'clear')

load_dotenv()

app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

genius = Genius(
    os.getenv('genius_key'), timeout=10)
genius.remove_section_headers = True

# Dropbox
app_key = os.getenv('app_key')
app_secret = os.getenv('app_secret')
access_token = os.getenv('access_token')
refresh_token = os.getenv('refresh_token')
access_code = os.getenv('access_code')


@app.errorhandler(404)
def page_not_found(e):
    return jsonify("404 not found. Please refer to the docs (no docs yet but in the future)"), 404


@app.route('/', methods=['GET'])
def index():
    return 'Live and working ✅'


@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('query')
    max = request.args.get('max') or 5

    raw_results = genius.search_songs(query)['hits']

    if raw_results:
        raw_results = raw_results[:max] if len(
            raw_results) >= max else raw_results

        add_stats(raw_results)

        results = []
        for result in raw_results:
            results.append({
                'id': result['result']['id'],
                'title': result['result']['title'],
                'artist': result['result']['primary_artist']['name'],
                'image': result['result']['header_image_thumbnail_url'],
                'popularity': result['result']['stats']['pageviews'],
            })

        sorted_results = sorted(
            results, key=lambda x: x['popularity'], reverse=True)

        response = jsonify(sorted_results)

    else:
        # json saying no results
        response = jsonify([])

    return response


@app.route('/api/song/lyrics/<song_id>', methods=['GET'])
def get_lyrics(song_id):
    if isinstance(song_id, int):
        return jsonify('Please enter a valid song ID'), 400

    response = jsonify(genius.lyrics(song_id))
    return response, 200


@app.route('/api/cors', methods=['GET'])
def get_cors_image():
    url = request.args.get('url')
    url = unquote(url)

    if not isinstance(url, str):
        return jsonify('Please enter a valid image URL'), 400

    response = requests.get(url)
    print(response)
    if response.status_code != 200:
        return jsonify('Failed to get image'), 400

    response = jsonify(img_to_base64(response.content))

    return response, 200


@app.route('/api/song/colors', methods=['GET'])
def get_colors():
    url = request.args.get('url')

    if not url:
        return jsonify('Please enter a valid song url'), 400

    colors = dominant_colors(url)

    response = jsonify(
        {
            'background_color': colors[0],
            'text_color': colors[1]
        }
    )

    return response, 200


# TODO: Refactor code base

def get_refreash_token():

    # https://www.codemzy.com/blog/dropbox-long-lived-access-refresh-token
    # https://www.dropbox.com/oauth2/authorize?client_id=<APP_KEY>&token_access_type=offline&response_type=code

    # Create the headers
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{app_key}:{app_secret}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Create the request body
    data = {
        "code": access_code,
        "grant_type": "authorization_code"
    }

    # Make the POST request
    response = requests.post(
        "https://api.dropboxapi.com/oauth2/token", headers=headers, data=data)

    # Print the response
    print("refresh_token:", response.json().get('refresh_token'))
    print(response.text)


@app.route('/api/upload', methods=['POST'])
def upload():
    file = request.files['image']
    filename = file.filename

    dbx = Dropbox(
        oauth2_access_token=access_token,
        oauth2_refresh_token=refresh_token,
        app_key=app_key,
        app_secret=app_secret
    )
    dbx.check_and_refresh_access_token()

    print(dbx.users_get_current_account())

    # Upload the image to Dropbox
    dbx.files_upload(file.read(), f'/{filename}')

    # Get the direct link to the uploaded image
    link = dbx.sharing_create_shared_link(f'/{filename}')
    direct_link = link.url.replace(
        'www.dropbox.com', 'dl.dropboxusercontent.com')

    response = jsonify(
        {
            'url': direct_link,
        }
    )
    return response, 200


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
