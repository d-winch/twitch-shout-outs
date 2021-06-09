import logging
import random
from typing import Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

import clipfetcher

logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)


"""
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.get("/soclip/{user_id}")
def read_item(user_id: str, mute: Optional[bool] = False):
    return {"item_id": user_id, "mute": mute}

@app.get("/test")
def read_item():

    access_token = clipfetcher.get_auth()

    clip_url = "https://www.twitch.tv/zombunnyyy/clip/HardProudKiwiBrainSlug-m-AMp8SA0ftS5t6x"
    mp4_url = clipfetcher.get_clip_url(access_token, clip_url)

    print(mp4_url)
    #return {"user_id": USER, "mute": False, "clip_url": mp4_url}
    return Response(content=mp4_url, media_type="text/plain")
"""

@app.get("/soclip/{username}")
def soclip(username: str):
    logger.info(f"Running soclip function for user {username}")
    username = username.replace("@", "")
    access_token = clipfetcher.get_auth()
    broadcaster_id = clipfetcher.get_broadcaster_id(access_token, username)
    if not broadcaster_id:
        logger.warning(f"Could not find broadcaster_id for {username}")
        raise HTTPException(status_code=404, detail=f"Error getting broadcaster_id for {username}")
    clips = clipfetcher.get_broadcaster_clips(access_token, broadcaster_id, first=100)
    if not clips:
        logger.warning(f"Could not find any clips for {username}")
        raise HTTPException(status_code=404, detail=f"No clips found for {username}")
    logger.info(f"Found {len(clips)} clip(s) for {username}")
    clip = random.choice(clips)
    mp4_url = clipfetcher.get_clip_url(access_token, clip['url'])
    logger.info(f"Returning clip {mp4_url} for {username}")
    return Response(content=mp4_url, media_type="text/plain")
