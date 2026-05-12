from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import json

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATUS_FILE = os.path.join(BASE_DIR, "guardian_status.txt")
STATS_CACHE = os.path.join(BASE_DIR, "verus_stats_cache.json")

# Templates klasörü kontrolü
templates_path = os.path.join(BASE_DIR, "templates")
if not os.path.exists(templates_path):
    os.makedirs(templates_path, exist_ok=True)

templates = Jinja2Templates(directory=templates_path)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Varsayılan Değerler
    guardian = {"temp": 0, "status": "Offline / Bekleniyor", "threads": "?"}
    stats = {"hashrate": "0 H/s", "paid": 0, "pending": 0, "last_share": "Veri Yok"}

    # Guardian verisi oku
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if "|" in content:
                    parts = content.split("|")
                    if len(parts) >= 3:
                        guardian = {"temp": parts[0], "status": parts[1], "threads": parts[2]}
        except: pass

    # Stats verisi oku
    if os.path.exists(STATS_CACHE):
        try:
            with open(STATS_CACHE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    # verus_stats.py'den gelen formatı işle
                    stats["hashrate"] = data.get("hashrate", data.get("hashrate_h", "0 H/s"))
                    stats["paid"] = data.get("paid", data.get("paid_vrsc", 0))
                    stats["pending"] = data.get("pending", data.get("pending_vrsc", 0))
                    stats["last_share"] = data.get("last_share", "Yok")
        except: pass

    return templates.TemplateResponse("index.html", {
        "request": request,
        "guardian": guardian,
        "stats": stats,
        "wallet": "RB2dBo22HqmG3hPKBiSQCW9bPpznzYZJB7"
    })
