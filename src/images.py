import io
from PIL import Image
import base64

def img_to_base64(res_img: bytes) -> str:
    """
    Converts a response image to a base64-encoded string.

    Parameters:
    `res_img` (bytes): The response image data as a bytes object.

    Returns:
    str: The base64-encoded image as a string with the "data:image/jpeg;base64," prefix.

    Example usage:
    >>> response = requests.get('https://example.com/image.jpg')
    >>> base64_image = img_to_base64(response.content)
    """

    image = Image.open(io.BytesIO(res_img))

    image = image.convert('RGB')

    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    img_str = 'data:image/jpeg;base64,' + img_str

    return img_str
