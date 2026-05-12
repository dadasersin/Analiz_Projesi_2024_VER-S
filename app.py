from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json

app = FastAPI()

# Dosya yolları (Render'da dosya yapısı GitHub'a göre olacak)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATUS_FILE = os.path.join(BASE_DIR, "guardian_status.txt")
STATS_CACHE = os.path.join(BASE_DIR, "verus_stats_cache.json")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Verileri Oku
    guardian = {"temp": 0, "status": "Offline", "threads": 0}
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                parts = f.read().split("|")
                guardian = {"temp": float(parts[0]), "status": parts[1], "threads": parts[2]}
        except: pass

    stats = {}
    if os.path.exists(STATS_CACHE):
        try:
            with open(STATS_CACHE, "r") as f:
                stats = json.load(f)
        except: pass

    return templates.TemplateResponse("index.html", {
        "request": request,
        "guardian": guardian,
        "stats": stats,
        "wallet": "RB2dBo22HqmG3hPKBiSQCW9bPpznzYZJB7"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
