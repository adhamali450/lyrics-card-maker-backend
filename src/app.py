from flask import Flask, jsonify, request
from flask_cors import CORS
from lyricsgenius import Genius
from .utils import add_stats, img_to_base64
from .colors import dominant_colors
import requests
from urllib.parse import unquote
from dotenv import load_dotenv
import os

# os.system("cls" if os.name == "nt" else "clear")

load_dotenv()

app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

genius = Genius(access_token=os.getenv("genius_key"), timeout=10, verbose=True, remove_section_headers=True, retries=2)

@app.errorhandler(404)
def page_not_found(e):
    return (
        jsonify(
            "404 not found. Please refer to the docs (no docs yet but in the future)"
        ),
        404,
    )


@app.route("/", methods=["GET"])
def index():
    return "Live and working ✅"


@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("query")
    max = request.args.get("max") or 5

    raw_results = genius.search_songs(query)["hits"]

    if raw_results:
        raw_results = raw_results[:max] if len(raw_results) >= max else raw_results

        add_stats(raw_results)

        results = []
        for result in raw_results:
            results.append(
                {
                    "id": result["result"]["id"],
                    "title": result["result"]["title"],
                    "artist": result["result"]["primary_artist"]["name"],
                    "image": result["result"]["header_image_thumbnail_url"],
                    "popularity": result["result"]["stats"]["pageviews"],
                }
            )

        sorted_results = sorted(results, key=lambda x: x["popularity"], reverse=True)

        response = jsonify(sorted_results)

    else:
        # json saying no results
        response = jsonify([])

    return response

@app.route("/api/song/lyrics/<song_id>", methods=["GET"])
def get_lyrics(song_id):
    # if not isinstance(song_id, int) or not isinstance(song_id, str):    
    #     return jsonify("Please enter a valid song ID"), 400

    try:
        lyrics = genius.lyrics(song_url=f'https://genius.com/songs/{song_id}')
    
        if not lyrics:
            return jsonify("Failed to get lyrics"), 400 
            
        response = jsonify(lyrics)
        return response, 200
    
    except Exception as e:
        return jsonify(str(e)), 400

@app.route("/api/cors", methods=["GET"])
def get_cors_image():
    url = request.args.get("url")
    url = unquote(url)

    if not isinstance(url, str):
        return jsonify("Please enter a valid image URL"), 400

    response = requests.get(url)
    print(response)
    if response.status_code != 200:
        return jsonify("Failed to get image"), 400

    response = jsonify(img_to_base64(response.content))

    return response, 200


@app.route("/api/song/colors", methods=["GET"])
def get_colors():
    url = request.args.get("url")

    if not url:
        return jsonify("Please enter a valid song url"), 400

    colors = dominant_colors(url)

    response = jsonify({"background_color": colors[0], "text_color": colors[1]})

    return response, 200