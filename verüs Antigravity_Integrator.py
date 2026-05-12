import os
import subprocess
import time

# --- ANTIGRAVITY OTONOM YAPILANDIRMA BILGILERI ---
CONFIG = {
    "PROJECT_PATH": r"d:\Analiz_Projesi_2024_VERÜS",
    "PIPELINE_SCRIPT": "Run_Project.bat",
    "DASHBOARD": "main.py"
}

def setup_full_autonomy():
    print(">>> ANTIGRAVITY SISTEM ENTEGRASYONU BASLATILIYOR...")
    
    # 1. Klasör ve Dosya Kontrolü
    if not os.path.exists(CONFIG["PROJECT_PATH"]):
        os.makedirs(CONFIG["PROJECT_PATH"])
    
    # 2. .bat Dosyasını Otonom Olarak Güncelle
    bat_path = os.path.join(CONFIG["PROJECT_PATH"], "Antigravity_Core.bat")
    bat_content = f"""@echo off
title Antigravity Compute Node
:: Bu dosya eski sistemden kalmadir. Yeni sisteme yonlendiriliyor.
cd /d "{CONFIG['PROJECT_PATH']}"
call {CONFIG['PIPELINE_SCRIPT']}
"""
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_content)
        print("[OK] Eski Core baslaticisi yeni boru hattina (Pipeline) yonlendirildi.")

    # 3. Bulut Senkronizasyon Kontrolü
    print("[WAIT] Moduller hazirlaniyor...")
    time.sleep(2)

if __name__ == "__main__":
    setup_full_autonomy()
    
    # Yeni dashboard'u başlat veya Run_Project.bat'a yönlendir
    print(">>> Dashboard baslatiliyor...")
    subprocess.run(["python", "Run_Antigravity.py"])
