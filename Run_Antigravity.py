import subprocess
import os
import time

# AYARLAR
BASE_DIR = r"d:\Analiz_Projesi_2024_VERÜS"

def launch():
    os.chdir(BASE_DIR)
    os.system('cls')
    print("="*50)
    print("   PROJECT ANTIGRAVITY - MASTER LAUNCHER")
    print("="*50)

    # Yeni orkestratör scriptini başlat
    print("[+] Fabrika Boru Hattı Başlatılıyor (Run_Project.bat)...")
    subprocess.Popen(['start', 'cmd', '/c', 'Run_Project.bat'], shell=True)
    
    time.sleep(3)
    
    # Dashboard'u başlat
    print("[+] Dashboard Başlatılıyor (main.py)...")
    subprocess.Popen(['start', 'cmd', '/k', 'python', 'main.py'], shell=True)

    print("\n[BİLGİ] Colab veri jeneratörünü çalıştırmayı unutmayın!")
    time.sleep(5)

if __name__ == "__main__":
    launch()
