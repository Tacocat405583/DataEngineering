import requests
import json

import os
from dotenv import load_dotenv


load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "3blue1brown"

def get_playlist_id():
    
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

        response = requests.get(url)
        
        response.raise_for_status()

        data = response.json()

        #json.dumps will convert python object to json string, indent=4 makes it pretty
        #print(json.dumps(data,indent=4))

        #append .uploads to get the uploads playlist id
        #data.items[0].contentDetails.relatedPlaylists.uploads
        channel_items = data["items"][0]

        channel_playlist_id = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]

        print(channel_playlist_id)
        
        return channel_playlist_id
    
    except requests.exceptions.RequestException as e:
        raise e
    
    
if __name__ == "__main__":
    get_playlist_id()

        