from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import asyncio

app = FastAPI()

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
            </body>
        </html>
    """
    return page_code

# ===== REQUESTS =====================================

@app.get("/get-map")
async def get_map():
    print("========== get num ===============")
    return {"tiles": [1, 2, 3]}

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

