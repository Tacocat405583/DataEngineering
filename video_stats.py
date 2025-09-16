import requests
import json

import os
from dotenv import load_dotenv


load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "3blue1brown"
maxResults = 50


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
    




def get_video_ids(playlistId):
    
    video_ids = []
    
    pageToken = None
    
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}"
    
    try:
        
        while True:
            
            url = base_url
            
            if pageToken:
                url += f"&pageToken={pageToken}"
                
            response = requests.get(url)
        
            response.raise_for_status()

            data = response.json()
            
            
            for item in data.get('items',[]):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)
                
            pageToken = data.get('nextPageToken')
            
            #no more videos
            if not pageToken:
                break
            
        
        return video_ids
                
            
    except requests.exceptions.RequestException as e:
        raise e
    
    
    
if __name__ == "__main__":
    playlistId = get_playlist_id()
    print(get_video_ids(playlistId))

        