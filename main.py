import logging
import random
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import clipfetcher
from fonts import font_options

logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static/"), name="static")

templates = Jinja2Templates(directory="templates/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
def get_so_options(request: Request):
    context = {
        "request": request,
        "fonts": font_options
    }
    return templates.TemplateResponse("sooptions.jinja", context=context)


@app.get("/soclip")
def get_so_template(
        request: Request,
        #username: str,
        #max_duration: Optional[int] = Query(20, gt=0, le=60),
        #muted: Optional[bool] = False,
        #cooldownMinutes: Optional[int] = Query(0, gt=0, le=60),
        font: Optional[str] = "Bowlby One SC",
        name_color: Optional[str] = "white"
):
    context = {
        "request": request,
        #"username": username,
        #"max_duration": max_duration,
        #"muted": str(muted).lower() == "true",
        #"cooldownMinutes": cooldownMinutes,
        "font_name": font_options[font],
        "name_color": name_color
    }
    return templates.TemplateResponse('soclip.jinja', context=context)


@app.get("/soclip/{username}")
def get_soclip_url(username: str):

    logger.info(f"Running soclip function for user {username}")
    username = username.replace("@", "")
    access_token = clipfetcher.get_auth()
    broadcaster_id = clipfetcher.get_broadcaster_id(access_token, username)

    if not broadcaster_id:
        logger.warning(f"Could not find broadcaster_id for {username}")
        raise HTTPException(
            status_code=404, detail=f"Error getting broadcaster_id for {username}")

    clips = clipfetcher.get_broadcaster_clips(
        access_token, broadcaster_id, first=100)

    if not clips:
        logger.warning(f"Could not find any clips for {username}")
        raise HTTPException(
            status_code=404, detail=f"No clips found for {username}")

    logger.info(f"Found {len(clips)} clip(s) for {username}")
    clip = random.choice(clips)
    mp4_url = clipfetcher.get_clip_url(access_token, clip['url'])
    logger.info(f"Returning clip {mp4_url} for {username}")

    res = {"username": username, "url": mp4_url}
    json_compatible_item_data = jsonable_encoder(res)

    return JSONResponse(content=json_compatible_item_data)
