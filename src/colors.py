from urllib.request import urlopen, Request
from io import BytesIO
from colorthief import ColorThief
from PIL import Image, ImageColor
from colorsys import rgb_to_hls, hls_to_rgb


def hex_to_rgb(hex: str) -> tuple:
    """
    Convert HEX to RGB

    Parameters:
        hex (str): The HEX color
    """

    hex = hex.lstrip('#')

    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple) -> str:
    """
    Convert RGB to HEX

    Parameters:
        rgb (tuple): The RGB color
    """

    red, green, blue = rgb

    rgb_int = (red << 16) + (green << 8) + blue
    return '#' + hex(rgb_int)[2:].zfill(6)


def get_contrast(background, foreground):
    # Convert colors to HLS format
    bg_h, bg_l, bg_s = rgb_to_hls(*background)
    fg_h, fg_l, fg_s = rgb_to_hls(*foreground)

    # Calculate color brightness difference
    brightness_diff = abs(bg_l - fg_l)

    # Calculate color saturation difference
    saturation_diff = abs(bg_s - fg_s)

    # Calculate color hue difference
    hue_diff = min(abs(bg_h - fg_h), 1 - abs(bg_h - fg_h))

    # Calculate color contrast ratio
    contrast_ratio = (max(bg_l, fg_l) + 0.05) / (min(bg_l, fg_l) + 0.05)

    # Calculate total score based on color difference and contrast ratio
    score = (1 - brightness_diff) + (1 - saturation_diff) + \
        (1 - hue_diff) + contrast_ratio

    return score


def dominant_colors(url: str) -> tuple:
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

    palette = color_thief.get_palette(color_count=5)

    dom1 = palette[1]
    dom2 = proper_foreground_color(dom1, [palette[0]] + palette[2:])

    if sum(dom1) < sum(dom2):
        primary = dom1
        secondary = dom2
    else:
        primary = dom2
        secondary = dom1

    return rgb_to_hex(primary), rgb_to_hex(secondary)


def proper_foreground_color(background_color: tuple, candidates: list, return_hex=False) -> tuple:
    max_contrast = 0
    best_color = candidates[0]

    for color in candidates:
        # Calculate contrast score for current color
        score = get_contrast(background_color, color)

        # Check if current color has higher contrast than previous colors
        if score > max_contrast:
            max_contrast = score
            best_color = color

    if return_hex:
        best_color = ImageColor.getrgb(f"rgb{best_color}")
        best_color = '#{:02x}{:02x}{:02x}'.format(*best_color)

    return best_color
