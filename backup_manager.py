"""
========================================================
  BACKUP MANAGER - Boru Hattı 2. Aşama
========================================================
  Görev : Arşiv deposunun toplam boyutunu izler.
          14 GB sınırı aşılırsa en eski dosyaları siler
          (Colab tarafındaki kota yönetimiyle senkron).
   Arşiv : d:\Analiz_Projesi_2024_VERÜS\Arsiv_Deposu
  Kota  : MAX 14 GB
========================================================
"""
import os
import time

# --- YAPILANDIRMA ---
PROJE_DIR   = os.path.dirname(os.path.abspath(__file__))
ARSIV_DIR   = os.path.join(PROJE_DIR, "Arsiv_Deposu")
COP_DIR     = os.path.join(PROJE_DIR, "Cop_Kutusu")
MAX_KOTA_GB = 14.0   # Colab tarafıyla eşleşen kota
KONTROL_SN  = 60     # saniye — kaç saniyede bir kota kontrol edilsin

os.makedirs(ARSIV_DIR, exist_ok=True)
os.makedirs(COP_DIR,   exist_ok=True)

def log(mesaj):
    print(f"[BACKUP {time.strftime('%H:%M:%S')}] {mesaj}", flush=True)

def tum_dosyalari_listele(klasor):
    """Klasör ve alt klasörlerindeki tüm dosyaları değiştirme zamanına göre sıralar (en eski önce)."""
    dosyalar = []
    for kok, _, dosya_listesi in os.walk(klasor):
        for f in dosya_listesi:
            tam_yol = os.path.join(kok, f)
            dosyalar.append(tam_yol)
    dosyalar.sort(key=os.path.getmtime)
    return dosyalar

def kota_kontrol_ve_temizle():
    """Arşivin toplam boyutunu hesaplar, sınır aşılırsa en eski dosyaları çöp kutusuna taşır."""
    dosyalar = tum_dosyalari_listele(ARSIV_DIR)

    if not dosyalar:
        log("Arşiv boş, kontrol atlandı.")
        return

    toplam_byte = sum(os.path.getsize(f) for f in dosyalar if os.path.isfile(f))
    toplam_gb   = toplam_byte / (1024 ** 3)

    log(f"📊 Arşiv Doluluğu: {toplam_gb:.2f} GB / {MAX_KOTA_GB} GB  ({len(dosyalar)} dosya)")

    while toplam_gb > MAX_KOTA_GB and dosyalar:
        en_eski = dosyalar.pop(0)

        try:
            boyut_gb  = os.path.getsize(en_eski) / (1024 ** 3)
            cop_hedef = os.path.join(COP_DIR, os.path.basename(en_eski))

            # Aynı isimde dosya varsa üzerine yaz
            if os.path.exists(cop_hedef):
                os.remove(cop_hedef)

            import shutil
            shutil.move(en_eski, cop_hedef)
            toplam_gb -= boyut_gb
            log(f"🗑️  Kota doldu! Çöpe taşındı: {os.path.basename(en_eski)}  ({boyut_gb:.2f} GB)")
        except Exception as e:
            log(f"❌ Silme hatası: {en_eski} → {e}")

def istatistik_raporu():
    """Arşiv ve çöp kutusunun durumunu raporlar."""
    def klasor_bilgisi(yol):
        dosyalar = [os.path.join(kok, f) for kok, _, fs in os.walk(yol) for f in fs]
        boyut_gb = sum(os.path.getsize(f) for f in dosyalar if os.path.isfile(f)) / (1024**3)
        return len(dosyalar), boyut_gb

    a_adet, a_gb = klasor_bilgisi(ARSIV_DIR)
    c_adet, c_gb = klasor_bilgisi(COP_DIR)
    log(f"📁 Arşiv: {a_adet} dosya / {a_gb:.2f} GB   |   🗑️  Çöp: {c_adet} dosya / {c_gb:.2f} GB")

def main():
    log("="*55)
    log("  ANTIGRAVITY BACKUP MANAGER BAŞLATILDI")
    log(f"  Kota Sınırı : {MAX_KOTA_GB} GB")
    log(f"  Arşiv Yolu  : {ARSIV_DIR}")
    log("="*55)

    while True:
        try:
            kota_kontrol_ve_temizle()
            istatistik_raporu()
        except Exception as e:
            log(f"HATA: {e}")

        time.sleep(KONTROL_SN)

if __name__ == "__main__":
    main()
