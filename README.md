# spotify2youtube-downloader
Download Spotify playlists as .mp3 from YouTube.

<h3> Dependencies </h3>
<ul>- Python3: https://www.python.org/downloads </ul>
<ul>- Ffmpeg: https://www.ffmpeg.org/download.html </ul>
<ul>- A Spotify application token must be created and provided in order to run: https://developer.spotify.com/dashboard </ul>

<h3> pip dependencies </h3>
<ul>- youtube-search </ul>
<ul>- joblib </ul>
<ul>- yt-dlp </ul>
<ul>- requests </ul>
<ul>- flask </ul>

------------------
<h3> 1. Install Python dependencies </h3>

```
pip install -r requirements.txt
```

------------------
<h3> 2. Configuration </h3>
<h4> Edit and set the Spotify token inside </h4>

```customSecrets.py```

------------------
<h3> 3. How to run </h3>
<h4> 3.1 CLI download songs or playlists </h4>

- Download Spotify playlists:

```
python main.py --playlist 2JOHUWecmpONy8NBQk7alx --folder ./songs/ --maxfilesize 10
```

- Download songs by name:

```
python main.py --songs "Daft Punk - One More Time, Radiohead - Creep" --folder ./songs/ --maxfilesize 10
```

------------------
<h4> 3.2 How to run as a web UI </h4>

- Start flask app with any arguments you may need:

```
flask run
```
<img width="1316" height="487" alt="image" src="https://github.com/user-attachments/assets/2d5d81ed-a5fc-416a-85db-a8ae4db31ef7" />
