import os
import time
import subprocess
from datetime import datetime

# --- YAPILANDIRMA ---
INTERVAL_MIN = 10  # Kaç dakikada bir buluta veri gönderilsin?
FILES_TO_SYNC = ["guardian_status.txt", "verus_stats_cache.json"]

def sync_to_cloud():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ☁️ Bulut senkronizasyonu baslatiliyor...")
    try:
        # Dosyaların varlığını kontrol et
        for f in FILES_TO_SYNC:
            if os.path.exists(f):
                subprocess.run(["git", "add", f], check=True)
        
        # Değişiklikleri taahhüt et ve gönder
        subprocess.run(["git", "commit", "-m", f"Auto-sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"], check=True)
        subprocess.run(["git", "push", "origin", "master"], check=True)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Bulut basariyla guncellendi.")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Senkronizasyon hatasi: {e}")

if __name__ == "__main__":
    print("====================================================")
    print("   ANTIGRAVITY CLOUD SYNC - OTOMATIK VERI AKTARIMI")
    print(f"   Aralik: {INTERVAL_MIN} dakika")
    print("====================================================")
    
    while True:
        sync_to_cloud()
        time.sleep(INTERVAL_MIN * 60)
