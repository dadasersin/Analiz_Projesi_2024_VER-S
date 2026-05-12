"""
========================================================
  TAŞIYICI SERVİSİ - Boru Hattı 1. Aşama
========================================================
  Görev : Google Drive'dan gelen veri paketlerini alır.
          Dosyaları Arsiv_Deposu'na kopyalar, ardından
          Google Drive'da sadece son 15 dosyayı bırakacak
          şekilde eskileri siler.
========================================================
"""
import shutil
import os
import time
from datetime import datetime

# --- YAPILANDIRMA ---
# Kullanıcının asıl Google Drive yolu:
KAYNAK   = r"C:\Users\ersin\Drive’ım (onatsemra@gmail.com) (1)\Scientific_Data_Backup"
PROJE    = os.path.dirname(os.path.abspath(__file__))
ARSIV    = os.path.join(PROJE, "Arsiv_Deposu")
BEKLEME  = 0.1     # saniye bekleme süresi (Hızlı tarama için düşürüldü)
STABIL   = 3     # dosya tam inme kontrolü
DRIVE_KOTA = 5   # Drive'da bırakılacak maksimum yeni dosya sayısı

IZIN_VERILEN_UZANTILAR = [".dat", ".bin", ".txt", ".csv", ".json"]
COLAB_DOSYA_ONEK      = "proc_T"

def log(mesaj):
    print(f"[TAŞIYICI {time.strftime('%H:%M:%S')}] {mesaj}", flush=True)

def dosya_stabil_mi(yol):
    try:
        boy1 = os.path.getsize(yol)
        time.sleep(STABIL)
        boy2 = os.path.getsize(yol)
        return boy1 == boy2 and boy1 > 0
    except Exception:
        return False

def gunluk_klasor_hazirla():
    tarih = datetime.now().strftime("%Y-%m-%d")
    klasor = os.path.join(ARSIV, tarih)
    os.makedirs(klasor, exist_ok=True)
    return klasor

def google_drive_temizligi():
    """Google Drive klasöründe sadece en yeni 15 dosyayı bırakır, eskileri siler."""
    try:
        dosyalar = [
            os.path.join(KAYNAK, f) for f in os.listdir(KAYNAK)
            if os.path.isfile(os.path.join(KAYNAK, f))
            and f.startswith(COLAB_DOSYA_ONEK)
        ]
        
        # Yeniden eskiye sırala (en son değiştirilen ilk sırada)
        dosyalar.sort(key=os.path.getmtime, reverse=True)
        
        # Eğer dosyalar 5'ten fazlaysa eskileri sil
        silinecekler = dosyalar[DRIVE_KOTA:]
        
        for f in silinecekler:
            try:
                os.remove(f)
                log(f"🗑️ Drive Temizliği: Eski dosya silindi → {os.path.basename(f)}")
            except Exception as e:
                log(f"⚠️ Dosya silinemedi ({os.path.basename(f)}): {e}")
                
    except Exception as e:
        log(f"HATA (Drive Temizliği): {e}")

def main():
    os.makedirs(ARSIV, exist_ok=True)
    log("="*60)
    log(" 🚀 TAŞIYICI SERVİSİ BAŞLADI - DETAYLI İZLEME AKTİF")
    log(f" 📂 Kaynak : {KAYNAK}")
    log(f" 📦 Arşiv  : {ARSIV}")
    log(f" 🧹 Kural  : Drive'da max {DRIVE_KOTA} dosya tutulacak, eskiler silinecek.")
    log("="*60)

    while True:
        try:
            if not os.path.exists(KAYNAK):
                log(f"⏳ Uyarı: Google Drive klasörü bekleniyor → {KAYNAK}")
                time.sleep(BEKLEME)
                continue

            dosya_isimleri = [
                f for f in os.listdir(KAYNAK)
                if os.path.isfile(os.path.join(KAYNAK, f))
                and f.startswith(COLAB_DOSYA_ONEK)
                and any(f.lower().endswith(uz) for uz in IZIN_VERILEN_UZANTILAR)
            ]

            if not dosya_isimleri:
                log("👀 Drive klasörü dinleniyor... Yeni dosya yok.")
                time.sleep(BEKLEME)
                continue

            hedef_klasor = gunluk_klasor_hazirla()
            islem_yapildi = False

            for f in dosya_isimleri:
                kaynak_yolu = os.path.join(KAYNAK, f)
                hedef_yolu  = os.path.join(hedef_klasor, f)

                # Eğer dosya zaten arşive kopyalanmışsa işlem yapma
                if os.path.exists(hedef_yolu):
                    continue

                log(f"⚙️ Analiz ediliyor: {f} ...")
                if not dosya_stabil_mi(kaynak_yolu):
                    log(f"⏳ Bekleniyor: {f} (İndirme işlemi sürüyor olabilir)")
                    continue

                # KOPYALAMA İŞLEMİ (Şu anki boyutu yazdırarak)
                boyut_mb = os.path.getsize(kaynak_yolu) / (1024 * 1024)
                shutil.copy2(kaynak_yolu, hedef_yolu)
                log(f"✅ AKTARILDI: {f} ({boyut_mb:.2f} MB) → Arsiv_Deposu'na eklendi.")
                islem_yapildi = True

            # Eğer yeni dosyalar aktarıldıysa Google Drive temizlik rutini çalışsın
            if islem_yapildi:
                log("🧹 Drive kotası kontrol ediliyor...")
                google_drive_temizligi()

        except Exception as e:
            log(f"❌ BEKLENMEYEN HATA: {e}")

        time.sleep(BEKLEME)

if __name__ == "__main__":
    main()
