"""
========================================================
  COLAB_SYNC.PY - Drive Senkronizasyon Alıcısı
========================================================
  Görev : Google Drive masaüstü uygulamasının PC'ye
          indirdiği Colab paketlerini (analysis_data_v1_*.dat)
          izler ve Arsiv_Deposu'na tarih bazlı taşır.
  Kaynak: D:\google driver\Scientific_Data_Backup
  Hedef : D:\Data_Science_Project\Analiz_Projesi_2024\Arsiv_Deposu\<TARIH>
  Not   : tasiyici.py ile aynı işi yapar fakat bağımsız
          modül olarak da çalışabilir.
========================================================
"""
import os
import shutil
import time
from datetime import datetime

# --- YAPILANDIRMA ---
DRIVE_DIR   = r"C:\Users\ersin\Drive’ım (onatsemra@gmail.com) (1)\Scientific_Data_Backup"
PROJE_DIR   = os.path.dirname(os.path.abspath(__file__))
ARSIV_DIR   = os.path.join(PROJE_DIR, "Arsiv_Deposu")
BEKLEME_SN  = 30     # saniye — döngü aralığı
STABIL_SN   = 3      # saniye — dosya boyut kararlılık kontrolü

# Colab'ın ürettiği dosya formatı: proc_T_XXXXX.dat
DOSYA_ONEK   = "proc_T"
DOSYA_UZANTI = ".dat"

os.makedirs(ARSIV_DIR, exist_ok=True)

# -------------------------------------------------------

def log(mesaj):
    print(f"[SYNC {datetime.now().strftime('%H:%M:%S')}] {mesaj}", flush=True)

def dosya_stabil_mi(yol, bekleme=STABIL_SN):
    """Dosyanın tamamen indirildiğini boyut karşılaştırmasıyla doğrular."""
    try:
        b1 = os.path.getsize(yol)
        time.sleep(bekleme)
        b2 = os.path.getsize(yol)
        return b1 == b2 and b1 > 0
    except Exception:
        return False

def gunluk_klasor():
    """Bugünün arşiv klasörünü oluşturur ve döndürür."""
    tarih  = datetime.now().strftime("%Y-%m-%d")
    klasor = os.path.join(ARSIV_DIR, tarih)
    os.makedirs(klasor, exist_ok=True)
    return klasor

def start_sync():
    log("=" * 50)
    log("  ANTIGRAVITY COLAB SYNC - AKTİF")
    log(f"  Kaynak : {DRIVE_DIR}")
    log(f"  Arşiv  : {ARSIV_DIR}")
    log("=" * 50)

    while True:
        try:
            # Drive klasörü yoksa Google Drive uygulamasını bekle
            if not os.path.exists(DRIVE_DIR):
                log(f"Drive klasörü bulunamadı: {DRIVE_DIR}  (Google Drive bağlı mı?)")
                time.sleep(60)
                continue

            # Yalnızca Colab paketlerini al
            dosyalar = [
                f for f in os.listdir(DRIVE_DIR)
                if f.startswith(DOSYA_ONEK) and f.endswith(DOSYA_UZANTI)
                and os.path.isfile(os.path.join(DRIVE_DIR, f))
            ]

            if not dosyalar:
                time.sleep(BEKLEME_SN)
                continue

            hedef_klasor  = gunluk_klasor()
            islenen_sayi  = 0

            for dosya in dosyalar:
                kaynak = os.path.join(DRIVE_DIR, dosya)
                hedef  = os.path.join(hedef_klasor, dosya)

                if os.path.exists(hedef):
                    continue  # Zaten taşınmış

                if not dosya_stabil_mi(kaynak):
                    log(f"İNDİRİLİYOR: {dosya} henüz hazır değil, atlandı.")
                    continue

                boyut_mb = os.path.getsize(kaynak) / (1024 * 1024)
                shutil.move(kaynak, hedef)
                log(f"ALINDI ✓  {dosya}  ({boyut_mb:.1f} MB)  →  {hedef_klasor}")
                islenen_sayi += 1

            if islenen_sayi > 0:
                log(f"Döngü özeti: {islenen_sayi} paket başarıyla arşive taşındı.")

        except Exception as e:
            log(f"HATA: {e}")

        time.sleep(BEKLEME_SN)

if __name__ == "__main__":
    start_sync()
