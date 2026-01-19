import re
from bs4 import BeautifulSoup, Tag, NavigableString 

import requests

def get_lyrics_by_id(song_id: int) -> str:
    song_url = f"https://genius.com/songs/{song_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    data = requests.get(song_url, headers=headers).text
    
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