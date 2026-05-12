"""
========================================================
  VERUS_STATS.PY - VERUS Madencilik Istatistik Paneli
========================================================
  Gorev  : Hem luckpool.net API'sinden hem de yerel
           sistem loglarindan VERUS kazanim bilgilerini
           derler ve ekrana basar.
  Cuzdan : RB2dBo22HqmG3hPKBiSQCW9bPpznzYZJB7
========================================================
"""
import urllib.request
import json
import sys
import os
import re
from datetime import datetime

# --- UTF-8 ---
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WALLET    = "RB2dBo22HqmG3hPKBiSQCW9bPpznzYZJB7"
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "verus_stats_cache.json")
CORE_LOG   = os.path.join(BASE_DIR, "system_core_log.txt")
DONE_DIR   = os.path.join(BASE_DIR, "Arsiv_Deposu", "Done")

# Luckpool API Endpointleri
API_BASE = "https://luckpool.net/verus/api"

def api_get(url: str, timeout: int = 8):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json"
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except:
        return {"error": "Baglanti Hatasi"}

def fetch_miner():
    return api_get(f"{API_BASE}/miner/{WALLET}")

def fetch_payments():
    res = api_get(f"{API_BASE}/payments/{WALLET}")
    return res if isinstance(res, list) else []

def fetch_earnings():
    return api_get(f"{API_BASE}/earnings/{WALLET}")

def format_hashrate(h: float) -> str:
    if h >= 1_000_000:
        return f"{h/1_000_000:.2f} MH/s"
    elif h >= 1_000:
        return f"{h/1_000:.2f} kH/s"
    elif h > 0:
        return f"{h:.1f} H/s"
    return "0 H/s"

def parse_stats(miner: dict, payments: list, earnings: dict) -> dict:
    out = {
        "hashrate_h":   0.0,
        "paid_vrsc":    0.0,
        "pending_vrsc": 0.0,
        "workers":      0,
        "last_share":   "?",
        "error":        None,
        "projections":  {"daily": 0.0, "monthly": 0.0}
    }

    if not miner or "error" in miner:
        out["error"] = "API Offline"
        return out

    try:
        out["hashrate_h"]   = float(miner.get("hashrate", 0))
        out["pending_vrsc"] = float(miner.get("pendingBalance", 0))
        out["workers"]      = int(miner.get("workersTotal", 1))
        out["last_share"]   = str(miner.get("lastShare", "?"))
        
        # Odemeler
        if payments:
            out["paid_vrsc"] = sum(float(p.get("amount", 0)) for p in payments)
        elif earnings and "error" not in earnings:
            out["paid_vrsc"] = float(earnings.get("total", 0))
            
        # Tahmin (1 MH/s ~ 0.15 VRSC)
        mh = out["hashrate_h"] / 1_000_000
        out["projections"]["daily"] = mh * 0.15
        out["projections"]["monthly"] = out["projections"]["daily"] * 30.4
    except:
        pass

    return out

def get_local_stats():
    stats = {"count": 0, "size_gb": 0.0, "last": "Yok"}
    if os.path.exists(DONE_DIR):
        for root, _, files in os.walk(DONE_DIR):
            for f in files:
                stats["count"] += 1
                stats["size_gb"] += os.path.getsize(os.path.join(root, f)) / (1024**3)
    return stats

def main():
    m = fetch_miner()
    p = fetch_payments()
    e = fetch_earnings()
    s = parse_stats(m, p, e)
    l = get_local_stats()
    
    print("="*62)
    print("   ANTIGRAVITY VERUS COMPUTE NODE")
    print("="*62)
    if s["error"]:
        print(f"   [POOL] Durum: {s['error']}")
    else:
        print(f"   [POOL] Hashrate : {format_hashrate(s['hashrate_h'])}")
        print(f"   [POOL] Kazanilan: {s['paid_vrsc']:.6f} VRSC")
        print(f"   [POOL] Tahmin   : Günlük ~{s['projections']['daily']:.4f} VRSC")
    print("-"*62)
    print(f"   [LOCAL] Islenen : {l['count']} paket / {l['size_gb']:.2f} GB")
    print("="*62)

if __name__ == "__main__":
    main()
