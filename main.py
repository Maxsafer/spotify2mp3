from youtube_search import YoutubeSearch
from joblib import Parallel, delayed
from customSecrets import getSecret
from pytube import YouTube 
from requests import post
import requests
import base64
import json
import math
import re
import os

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

def get_songs(token, os, plID):
    url = f"https://api.spotify.com/v1/playlists/{plID}/tracks"
    payload = ""
    querystring = {"offset": os}
    headers = {"Authorization": "Bearer " + token}
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    json_response = json.loads(response.content)
    return json_response

def song_list(songDict):
    songs = []
    for item in songDict.get("items"):
        track = item.get("track")
        songArtists = track.get("artists")
        songArtistsString = ''
        for artist in songArtists:
            songArtistsString += (" " + artist.get("name"))
        songName = track.get("name")
        query = songName + " - " + songArtistsString.strip()
        songs.append(query)

    return songs

def complete_songlist(tok, plID):
    os = 0
    dictSongs = get_songs(tok, os, plID)
    listSongs = song_list(dictSongs)

    intTotalSongs = dictSongs.get("total")
    intTimesToLoop = math.ceil(intTotalSongs/100)

    for x in range(0, intTimesToLoop):
        os += 100
        dictSongs = get_songs(tok, os, plID)
        listSongs = listSongs + song_list(dictSongs)

    return listSongs

def downloadSongs(song, maxFileSize, folder):
    try:
        f = open(folder + "songsLog.csv", "a", newline='')
        results = YoutubeSearch(song, max_results=1).to_dict()
        url = 'https://www.youtube.com' + results[0].get('url_suffix')
        yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
        
        video = yt.streams.get_audio_only()

        if video.filesize_mb > maxFileSize:
            f.write(f"\nFailed, File size too big {video.filesize_mb} MB, " + song + ", " + url)
            return

        out_file = video.download(output_path=folder)
        
        # save the file 
        base, ext = os.path.splitext(out_file) 
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        try:
            f.write("\nOk, Downloaded, " + str(base) + f" - song: {song}" + ", " + str(url))
        except Exception as e:
            f.write("\nOk, Downloaded, " + str(e) + f" - song: {re.sub('[^A-Za-z0-9]+','', song)}" + ", " + str(url))

    except Exception as e:
        f.write(f"\nFailed, {e}, " + song + ", " + str(url))

    finally:
        f.close()

if __name__ == '__main__':
    tokenM = get_token()
    playListID = ""
    listPlayList = complete_songlist(tokenM, playListID)
    folder = "./songs/"
    maxFileSize = 10    # in MB

    Parallel(n_jobs=-1,prefer='threads')(delayed(downloadSongs)(listPlayList[x], maxFileSize, folder) for x in range(0, len(listPlayList)))