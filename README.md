# spotify2youtube-downloader
Download Spotify playlists as .mp3 from YouTube.

<h3> Dependencies </h3>
<ul>- A Spotify application token must be created and provided in order to run: https://developer.spotify.com/dashboard </ul>
<ul>- ffmpeg </ul>

<h3> pip dependencies </h3>
<ul>-youtube-search </ul>
<ul>-joblib </ul>
<ul>-yt-dlp </ul>
<ul>-pytube </ul>
<ul>-requests </ul>

<h3> How to run </h3>
<h4> 1. Install dependencies </h4>

```pip install -r requirements.txt```

<h4> 2. Download songs </h4>

- Download Spotify playlists:

```python main.py --playlist 2JOHUWecmpONy8NBQk7alx --folder ./songs/ --maxfilesize 10```

- Download songs by name:

```python main.py --songs "Daft Punk - One More Time, Radiohead - Creep" --folder ./songs/ --maxfilesize 10```