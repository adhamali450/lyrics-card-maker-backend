from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from lyricsgenius import Genius

app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

genius = Genius(
    'TD-NdGeW-I0TRk-uEOkIp6sOAU9TPuxXIPMpRRu7uvWywUZCdeYvtYreG_Pz6f6u', timeout=10)


@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('query')

    raw_results = genius.search_songs(query)['hits']

    if raw_results:
        raw_results = raw_results[:5] if len(raw_results) >= 5 else raw_results

        # Not to get KeyError when there are no stats
        for i in range(len(raw_results)):
            if not raw_results[i]['result']['stats'].get('pageviews'):
                raw_results[i]['result']['stats'].update({'pageviews': 0})

        results = []
        for result in raw_results:
            results.append({
                'id': result['result']['id'],
                'title': result['result']['title'],
                'artist': result['result']['primary_artist']['name'],
                'image': result['result']['header_image_thumbnail_url'],
                'popularity': result['result']['stats']['pageviews']
            })

        sorted_results = sorted(
            results, key=lambda x: x['popularity'], reverse=True)

        response = jsonify(sorted_results)

    else:
        # json saying no results
        resposne = jsonify([])

    return response


@app.route('/api/song/<song_id>', methods=['GET'])
def get_lyrics(song_id):
    lyrics = genius.lyrics(song_id)

    response = jsonify(lyrics)
    return response


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
