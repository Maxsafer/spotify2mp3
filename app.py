from flask import Flask, request, jsonify, render_template
import subprocess
import os
import re

app = Flask(__name__)

# --- Configuration ---
MUSIC_FOLDER = "./songs"
LOG_FILE = os.path.join(MUSIC_FOLDER, "songsLog.csv")

def extract_playlist_id(input_str):
    """
    Extracts the playlist ID from a Spotify URL.
    If the input_str is already just an ID, returns it.
    """
    match = re.search(r'playlist/([a-zA-Z0-9]+)', input_str)
    if match:
        return match.group(1)
    return input_str.strip()

# --- Flask Endpoints ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download_item", methods=["POST"])
def download_item():
    data = request.get_json()
    mode = data.get("mode")
    query = data.get("query", "").strip()
    maxfilesize = data.get("maxfilesize", 20)
    
    if not query:
        return jsonify({"log": "Error: Query is empty."}), 400

    # For songs mode, if multiple songs (separated by newline) are provided,
    # replace newlines with commas.
    if mode == "song":
        query = query.replace("\n", ",")
        command = f'python main.py --songs "{query}" --folder "{MUSIC_FOLDER}" --maxfilesize {maxfilesize}'
    elif mode == "playlist":
        # Extract playlist ID from URL if needed.
        query = extract_playlist_id(query)
        command = f'python main.py --playlist "{query}" --folder "{MUSIC_FOLDER}" --maxfilesize {maxfilesize}'
    else:
        return jsonify({"log": "Error: Invalid mode."}), 400

    # Clear the songsLog.csv file before running the command.
    try:
        os.makedirs(MUSIC_FOLDER, exist_ok=True)
        open(LOG_FILE, 'w', encoding='utf-8').close()
    except Exception as e:
        return jsonify({"log": f"Error clearing log file: {e}"})

    # Execute the command without capturing its output.
    try:
        subprocess.run(command, shell=True)
    except Exception as e:
        return jsonify({"log": f"Error executing command: {e}"})

    # Read and return the content of songsLog.csv
    try:
        with open(LOG_FILE, 'r', encoding="utf-8") as f:
            csv_content = f.read()
    except Exception as e:
        csv_content = f"Error reading log file: {e}"

    return jsonify({"log": csv_content})

if __name__ == "__main__":
    os.makedirs(MUSIC_FOLDER, exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
