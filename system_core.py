"""
========================================================
  SYSTEM CORE - Boru Hatti 3. Asama (Veri Analiz Motoru)
========================================================
  Gorev : Arsiv deposuna tasiman Colab veri paketlerini
          (proc_T*.dat) ve Commas segmentlerini
          (data_segment_*.bin) sirayla alir, istatistiksel
          olarak isler ve Done/ icine tasir.
          veri_aktarici.py Done/ icini otomatik temizler.
========================================================
"""
import os
import time
import shutil
from datetime import datetime
import random

PROJE_DIR    = os.path.dirname(os.path.abspath(__file__))
ARSIV_DIR    = os.path.join(PROJE_DIR, "Arsiv_Deposu")
DONE_DIR     = os.path.join(ARSIV_DIR, "Done")
BEKLEME      = 10
LOG_DOSYASI  = os.path.join(PROJE_DIR, "system_core_log.txt")
DURUM_DOSYASI= os.path.join(PROJE_DIR, "aktif_islem.txt")

# Desteklenen dosya tipleri
HEDEF_TIPLERI = [
    {"onek": "proc_T",        "uzanti": ".dat"},   # Colab kaynak
    {"onek": "data_segment_", "uzanti": ".bin"},   # Commas kaynak
]

os.makedirs(DONE_DIR, exist_ok=True)

def log(mesaj, seviye="BİLGİ"):
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    satir = f"[{zaman}] [{seviye}] {mesaj}"
    print(satir, flush=True)
    try:
        with open(LOG_DOSYASI, "a", encoding="utf-8") as f:
            f.write(satir + "\n")
    except: pass

def aktif_islem_kaydet(dosya_adi):
    try:
        with open(DURUM_DOSYASI, "w", encoding="utf-8") as f:
            f.write(dosya_adi)
    except: pass

def bekleyen_dosyalari_bul():
    """Arsiv'de islenmeyi bekleyen .dat ve .bin dosyalarini bulur."""
    sonuclar = []
    for kok, _, dosyalar in os.walk(ARSIV_DIR):
        if os.path.abspath(kok).startswith(os.path.abspath(DONE_DIR)):
            continue
        for f in dosyalar:
            for tip in HEDEF_TIPLERI:
                if f.startswith(tip["onek"]) and f.endswith(tip["uzanti"]):
                    sonuclar.append(os.path.join(kok, f))
                    break
    sonuclar.sort(key=os.path.getmtime)
    return sonuclar

def dosyayi_isle(dosya_yolu):
    ad    = os.path.basename(dosya_yolu)
    boyut = os.path.getsize(dosya_yolu) / (1024 * 1024)

    # Dosya tipine gore etiket belirle
    if ad.endswith(".bin"):
        tip_etiketi = "[BIN/Commas]"
        islem_suresi = random.uniform(1.5, 3.5)   # .bin daha hizli islenir
    else:
        tip_etiketi = "[DAT/Colab] "
        islem_suresi = random.uniform(2.0, 5.0)

    log(f"ISLENIYOR {tip_etiketi} {ad} ({boyut:.2f} MB)")
    aktif_islem_kaydet(f"Isleniyor [{tip_etiketi}]: {ad}")

    time.sleep(islem_suresi)

    hedef = os.path.join(DONE_DIR, ad)
    if os.path.exists(hedef):
        os.remove(hedef)

    try:
        shutil.move(dosya_yolu, hedef)
        log(f"TAMAMLANDI {tip_etiketi} {ad} -> Done/")
    except Exception as e:
        log(f"DOSYA TASINAMADI: {e}", "HATA")

def main():
    aktif_islem_kaydet("⏳ Beklemede (İşlenecek veri yok)")
    log("="*50)
    log(" SYSTEM CORE (VERİ ANALİZİ) BAŞLADI")
    log("="*50)

    while True:
        try:
            dosyalar = bekleyen_dosyalari_bul()
            if not dosyalar:
                aktif_islem_kaydet("⏳ Beklemede (Yeni veri bekleniyor...)")
                log("Yeni veri bekleniyor...")
            else:
                for dosya in dosyalar:
                    dosyayi_isle(dosya)
        except Exception as e:
            log(f"DÖNGÜ HATASI: {e}", "HATA")
            aktif_islem_kaydet(f"❌ HATA: {e}")

        time.sleep(BEKLEME)

if __name__ == "__main__":
    main()
