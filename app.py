from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from lyricsgenius import Genius
from utils import add_stats, img_to_base64
from colors import dominant_colors
import requests


app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

genius = Genius(
    'TD-NdGeW-I0TRk-uEOkIp6sOAU9TPuxXIPMpRRu7uvWywUZCdeYvtYreG_Pz6f6u', timeout=10)
genius.remove_section_headers = True


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

    if not isinstance(url, str):
        return jsonify('Please enter a valid image URL'), 400

    response = requests.get(url)
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


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
