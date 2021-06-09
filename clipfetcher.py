import os
import pprint
import random

import requests
from dotenv import load_dotenv

pp = pprint.PrettyPrinter(width=41, compact=True)


load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')


CLIP_URL = "https://api.twitch.tv/helix/clips"
AUTH_URL = "https://id.twitch.tv/oauth2/token"


def get_auth():
    auth_params = {'client_id': CLIENT_ID,
                   'client_secret': CLIENT_SECRET, 'grant_type': 'client_credentials'}
    auth = requests.post(url=AUTH_URL, params=auth_params)
    auth_json = auth.json()
    access_token = auth_json["access_token"]
    return access_token

def get_clip_url(access_token, clip_url):
    slug = clip_url.rpartition('/')[-1]
    clip_info = requests.get(f"{CLIP_URL}?id={slug}", headers={
                             "Client-ID": CLIENT_ID, 'Authorization': f"Bearer {access_token}"}).json()
    thumb_url = clip_info['data'][0]['thumbnail_url']
    mp4_url = thumb_url.split("-preview", 1)[0] + ".mp4"
    return mp4_url

def get_broadcaster_id(access_token, username):
    url = f"https://api.twitch.tv/helix/users?login={username}"
    user_data = requests.get(url, headers={
                             "Client-ID": CLIENT_ID, 'Authorization': f"Bearer {access_token}"}).json()
    #pp.pprint(user_data)
    if not user_data['data']:
        return
    return user_data['data'][0]['id']

def get_broadcaster_clips(access_token, broadcaster_id, first=20):
    #print(f"{CLIP_URL}?broadcaster_id={broadcaster_id}&first={first}")
    clip_info = requests.get(f"{CLIP_URL}?broadcaster_id={broadcaster_id}&first={first}", headers={
                             "Client-ID": CLIENT_ID, 'Authorization': f"Bearer {access_token}"}).json()
    return clip_info['data']


if __name__ == "__main__":
    access_token = get_auth()
    print(access_token)

    broadcaster_id = get_broadcaster_id("zombunnyyy")

    clips = get_broadcaster_clips(access_token, broadcaster_id, first=100)
    pp.pprint(clips)

    clip = random.choice(clips)

    mp4_url = get_clip_url(access_token, clip['url'])
    print(mp4_url)
