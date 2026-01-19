import re
from bs4 import BeautifulSoup, Tag, NavigableString 
import requests
from dotenv import load_dotenv
import os

load_dotenv()



username = os.getenv("proxy_username")
password = os.getenv("proxy_password")
country = 'US'

# Format the proxy URL
proxy_url = f'http://{username}:{password}@pr.oxylabs.io:7777'

# Set up proxies for requests
proxies = {
    'http': proxy_url,
    'https': proxy_url
}

def get_lyrics_by_id(song_id: int) -> str:
    song_url = f"https://genius.com/songs/{song_id}"
    data = requests.get(song_url, proxies=proxies).text
    
    soup = BeautifulSoup(data, "html.parser")

    # Remove LyricsHeader divs from the DOM
    removes = soup.find_all("div", class_=re.compile("LyricsHeader__Container"))
    if removes:
        for remove in removes:
            remove.decompose()

    # Find all lyrics containers
    containers = soup.find_all("div", attrs={"data-lyrics-container": "true"})
    if not containers:
        print(
            "Couldn't find the lyrics section. "
            "Please report this if the song has lyrics.\n"
            "Song URL: https://genius.com/{}".format(song_url)
        )
        return None

    # Extract and join the lyrics
    lyrics = ""
    for container in containers:
        assert isinstance(container, Tag)
        if not container.contents:
            lyrics += "\n"
            continue
        for element in container.contents:
            assert isinstance(element, (Tag, NavigableString))
            if element.name == "br":
                lyrics += "\n"
            elif isinstance(element, NavigableString):
                lyrics += str(element)
            elif element.get("data-exclude-from-selection") != "true":
                lyrics += element.get_text(separator="\n")

    # Remove [Verse], [Bridge], etc.
    lyrics = re.sub(r"(\[.*?\])*", "", lyrics)
    lyrics = re.sub("\n{2}", "\n", lyrics)  # Gaps between verses
    return lyrics.strip("\n")