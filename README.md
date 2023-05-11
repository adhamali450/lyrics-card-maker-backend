
# Lyrics Card Maker (backend)

A Flask backend application that fetches data required by the [frontend](https://github.com/adhamali450/lyrics-card-maker-frontend) to create a Genius lyrics card using the [lyricsgenius](https://pypi.org/project/lyricsgenius/) library.



## Installation

To get started with this project, you can follow the steps below:

```bash
  git clone https://github.com/adhamali450/lyrics-card-maker-backend
  cd lyrics-card-maker-backend
  pip install -r requirements.txt

```
Once you have completed these steps, you should have the project set up and ready to use on your local machine.
    
## API Reference

#### Search
Searches for a query and it returns a list of results 

```bash
  CURL /api/search
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `query` | `string` | **Required**. The song or artist name |
| `max` | `int` | **Optional**. Max. results to return (default 5) |


#### Get lyrics
Searches the lyrics for a specified song

```bash
  CURL /api/song/lyrics/${song_id}
```


#### Get cover colors
Get the dominant background/foreground colors for a song cover 

```bash
  CURL api/song/colors
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `url` | `string` | **Required**. The cover img url |


#### Get `CORS` cover
Gets the cover image (can be done for any image url), when `CORS` headings isn't provided from Genius

```bash
  CURL /api/cors
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `url` | `string` | **Required**. The cover img url |


## Usage/Examples
To illustrate how to consume the API from a JavaScript application, we will provide a simple code example using `axios`.

```javascript
import axios from "axios";

const API_URL = "https://genius-unofficial-api.vercel.app/api";

const res = axios
  .get(API_URL + `/search`, {
    params: {
      query: "Eminem lose yourself",
    },
}).then((res) => {
    console.log(res.data);
});
```


## Acknowledgements

 - [lyricsgenius](https://pypi.org/project/lyricsgenius/)

## License

[MIT](https://choosealicense.com/licenses/mit/)

