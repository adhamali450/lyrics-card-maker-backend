from urllib.request import urlopen, Request
from io import BytesIO
from colorthief import ColorThief
from PIL import Image


def get_dominant_colors(url: str) -> tuple:
    """
    Get the dominant colors of an image for front-end purposes

    Parameters:
        url (str): The URL of the image
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    request = Request(url, headers=headers)
    response = urlopen(request)

    image_bytes = BytesIO(response.read())
    image = Image.open(image_bytes)

    # Extract dominant color using colorthief
    color_thief = ColorThief(image_bytes)

    palette = color_thief.get_palette(color_count=2)

    dominant_color = palette[1]
    text_color = palette[0]

    return dominant_color, text_color


# description: Get the dominant colors of an image
def add_stats(hits: list) -> None:
    """
    Add stats to the results so that we don't get KeyError when there are no stats

    Parameters:
        hits (list): The list of results from the Genius API
    """
    for i in range(len(hits)):
        if not hits[i]['result']['stats'].get('pageviews'):
            hits[i]['result']['stats'].update({'pageviews': 0})
