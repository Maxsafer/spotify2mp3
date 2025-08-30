import argparse
import math
import os
import re
import json
import base64
import datetime
from youtube_search import YoutubeSearch
from joblib import Parallel, delayed
from customSecrets import getSecret
from yt_dlp import YoutubeDL
from pytube import YouTube
import requests
from requests import post

def get_token():
    auth_string = getSecret.client_id + ":" + getSecret.client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_songs(token, offset, plID):
    url = f"https://api.spotify.com/v1/playlists/{plID}/tracks"
    payload = ""
    querystring = {"offset": offset}
    headers = {"Authorization": "Bearer " + token}
    response = requests.get(url, data=payload, headers=headers, params=querystring)
    json_response = json.loads(response.content)
    return json_response

def song_list(songDict):
    songs = []
    for item in songDict.get("items", []):
        track = item.get("track")
        if not track:
            continue
        songArtists = track.get("artists", [])
        songArtistsString = ' '.join(artist.get("name", "") for artist in songArtists)
        songName = track.get("name")
        query = f"{songName} - {songArtistsString.strip()}"
        songs.append(query)
    return songs

def complete_songlist(token, plID):
    offset = 0
    dictSongs = get_songs(token, offset, plID)
    listSongs = song_list(dictSongs)

    intTotalSongs = dictSongs.get("total", 0)
    intTimesToLoop = math.ceil(intTotalSongs/100)

    for x in range(1, intTimesToLoop):
        offset += 100
        dictSongs = get_songs(token, offset, plID)
        listSongs += song_list(dictSongs)

    return listSongs

def downloadSongs(song, maxFileSize, folder):
    url = ""
    try:
        with open(os.path.join(folder, "songsLog.csv"), "a", newline='') as f:
            timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

            # 1) Get several results and choose the first NON-playlist (prefer /watch or /shorts)
            results = YoutubeSearch(song, max_results=5).to_dict()  # was 1
            picked = next((r for r in results
                           if r.get('url_suffix', '').startswith(('/watch', '/shorts'))), None)
            if not picked:
                f.write("\n" + timestamp + " Skipped, no video result, " + song)
                return
            url = 'https://www.youtube.com' + picked.get('url_suffix')

            # 2) Tell yt-dlp not to download playlists even if one slips through
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
                'max_filesize': maxFileSize * 1024 * 1024,
                'noplaylist': True,
                'cookiesfrombrowser': ('chrome',),   # <- use your browser’s cookies. Try ('edge',) or ('firefox',) if you use those.
            }

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            f.write("\n" + timestamp + " Ok, Downloaded, " + song + ", " + url)
    except Exception as e:
        with open(os.path.join(folder, "songsLog.csv"), "a", newline='') as f:
            timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            f.write("\n" + timestamp + f" Failed, {e}, " + song + ", " + url)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download songs from a Spotify playlist or a list of song names.'
    )
    parser.add_argument('--playlist', type=str,
                        help='Spotify Playlist ID to download songs from')
    parser.add_argument('--songs', type=str,
                        help='Comma separated list of songs to download, e.g. "song1, song2, song3"')
    parser.add_argument('--folder', type=str, default="./songs/",
                        help="Output folder for downloads")
    parser.add_argument('--maxfilesize', type=int, default=10,
                        help="Maximum file size in MB for downloads")
    args = parser.parse_args()

    # Ensure the output folder exists
    if not os.path.exists(args.folder):
        os.makedirs(args.folder)

    if args.playlist:
        tokenM = get_token()
        listPlayList = complete_songlist(tokenM, args.playlist)
    elif args.songs:
        # Split the comma-separated songs into a list and strip any extra whitespace
        listPlayList = [s.strip() for s in args.songs.split(',')]
    else:
        print("Please provide either a Spotify playlist ID with --playlist or a comma-separated list of songs with --songs")
        exit(1)

    Parallel(n_jobs=-1, prefer='threads')(
        delayed(downloadSongs)(song, args.maxfilesize, args.folder) for song in listPlayList
    )
