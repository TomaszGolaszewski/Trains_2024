from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import asyncio
import datetime

from app.classes_map import *

app = FastAPI()

WORLD_MAP = World_map()

# ===== PAGE =====================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Return welcome page."""
    page_code = """
        <html>
            <head>
            </head>
            <body>
                <h1>Trains 2024</h1>
                Welcome to the Trains_2024 project server.
                <p><a href="docs#">API Documentation</a></p>
            </body>
        </html>
    """
    return page_code

# ===== REQUESTS =====================================

get_world_examples = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "example": {
                    "tiles":[{
                        "id":541,
                        "coord":[29,18],
                        "tracks":[],
                        "type":"grass"
                    }],
                    "trains": [],
                    "server_time":"2024-08-05T12:59:15.272432"
                }
            }
        },
    },
}

@app.get("/get-world", responses=get_world_examples)
async def get_world():
    """Prepare and provide World's data for API response."""
    response = {
        "tiles": WORLD_MAP.prepare_tiles_data_for_response(),
        "trains": WORLD_MAP.prepare_trains_data_for_response(),
        "server_time": datetime.datetime.now()
    }
    return response

get_trains_examples = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "example": {
                    "trains":[{
                        "id":541,
                    }],
                    "server_time":"2024-08-05T12:59:15.272432"
                }
            }
        },
    },
}

@app.get("/get-trains", responses=get_trains_examples)
async def get_trains():
    """Prepare and provide train's data for API response."""
    response = {
        "trains": WORLD_MAP.prepare_trains_data_for_response(),
        "server_time": datetime.datetime.now()
    }
    return response

# ===== LOOP =====================================

async def main_loop():
    """The main loop of the world simulation."""
    i = 0
    while True:
        i += 1
        print(i)
        await asyncio.sleep(1)

@app.on_event('startup')
async def app_startup():
    """Start tasks at server startup."""
    asyncio.create_task(main_loop())

