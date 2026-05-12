"""
========================================================
  VERI AKTARICI - Commas Kaynak Entegratoru
========================================================
  Gorev : D:\\google driver commas\\Project_Analiz_Data
          klasöründeki data_segment_*.bin dosyalarini
          Arsiv_Deposu'na tarih bazli TASIR (kopyalar
          sonra kaynagi siler).  System_Core isledikten
          sonra Done/ icindeki kopyayi da temizler.

  Kaynak : D:\\google driver commas\\Project_Analiz_Data
  Hedef  : <PROJE>\\Arsiv_Deposu\\<TARIH>\\commas\\
  Silme  : Arsive tasindiktan SONRA kaynak .bin silinir.
========================================================
"""
import os
import sys
import shutil
import time
from datetime import datetime

# Windows terminali için UTF-8 encoding zorla
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# --- YAPILANDIRMA ---
KAYNAK_DIR  = r"D:\google driver commas\Project_Analiz_Data"
PROJE_DIR   = os.path.dirname(os.path.abspath(__file__))
ARSIV_DIR   = os.path.join(PROJE_DIR, "Arsiv_Deposu")
BEKLEME_SN  = 30       # Saniye — tarama döngüsü aralığı
STABIL_SN   = 2        # Saniye — dosya boyut kararlılık kontrolü
DOSYA_ONEK  = "data_segment_"
DOSYA_UZANTI= ".bin"

# Kayıt dosyası — hangi dosyaların aktarıldığını takip eder
KAYIT_DOSYASI = os.path.join(PROJE_DIR, "aktarilan_dosyalar.log")

os.makedirs(ARSIV_DIR, exist_ok=True)


def log(mesaj: str):
    zaman = datetime.now().strftime("%H:%M:%S")
    print(f"[VERİ-AKTARICI {zaman}] {mesaj}", flush=True)


def aktarilan_dosyalari_yukle() -> set:
    """Daha önce aktarılan dosya isimlerini yükler."""
    if not os.path.exists(KAYIT_DOSYASI):
        return set()
    with open(KAYIT_DOSYASI, "r", encoding="utf-8") as f:
        return set(satir.strip() for satir in f if satir.strip())


def aktarildi_olarak_kaydet(dosya_adi: str):
    """Aktarılan dosya adını kayıt dosyasına ekler."""
    with open(KAYIT_DOSYASI, "a", encoding="utf-8") as f:
        f.write(dosya_adi + "\n")


def dosya_stabil_mi(yol: str) -> bool:
    """Dosyanın tamamen yazıldığını boyut karşılaştırmasıyla doğrular."""
    try:
        b1 = os.path.getsize(yol)
        time.sleep(STABIL_SN)
        b2 = os.path.getsize(yol)
        return b1 == b2 and b1 > 0
    except Exception:
        return False


def gunluk_hedef_klasor() -> str:
    """Bugüne ait arşiv alt klasörünü oluşturur (commas alt dizini ile)."""
    tarih  = datetime.now().strftime("%Y-%m-%d")
    klasor = os.path.join(ARSIV_DIR, tarih, "commas")
    os.makedirs(klasor, exist_ok=True)
    return klasor


def tarama_ve_aktar():
    """Kaynak klasörü tarar, yeni .bin dosyalarını arşive kopyalar."""
    if not os.path.exists(KAYNAK_DIR):
        log(f"⏳ Kaynak klasör bulunamadı → {KAYNAK_DIR}")
        return

    aktarilmis = aktarilan_dosyalari_yukle()

    kandidatlar = [
        f for f in os.listdir(KAYNAK_DIR)
        if f.startswith(DOSYA_ONEK)
        and f.endswith(DOSYA_UZANTI)
        and os.path.isfile(os.path.join(KAYNAK_DIR, f))
        and f not in aktarilmis
    ]

    # Zaten islem gorup loglanmis ama kaynakta kalmis dosyalari temizle
    for f in os.listdir(KAYNAK_DIR):
        if f in aktarilmis:
            try:
                os.remove(os.path.join(KAYNAK_DIR, f))
                log(f"[TEMIZLIK] Logda kayitli olan eski kaynak silindi: {f}")
            except: pass

    if not kandidatlar:
        log(f"[OK] Tum yeni dosyalar aktarildi. Yeni veri bekleniyor...")
        return

    log(f"[TARAMA] {len(kandidatlar)} yeni dosya bulundu. Aktarim basliyor...")
    hedef_klasor = gunluk_hedef_klasor()
    basarili = 0
    beklenen = 0

    for dosya_adi in sorted(kandidatlar):
        kaynak_yolu = os.path.join(KAYNAK_DIR, dosya_adi)
        hedef_yolu  = os.path.join(hedef_klasor, dosya_adi)

        # Zaten fiziksel olarak kopyalandıysa geç
        if os.path.exists(hedef_yolu):
            aktarildi_olarak_kaydet(dosya_adi)
            continue

        log(f"[KONTROL] {dosya_adi}")
        if not dosya_stabil_mi(kaynak_yolu):
            log(f"[BEKLE] {dosya_adi} (henuz yaziliyor olabilir)")
            beklenen += 1
            continue

        boyut_mb = os.path.getsize(kaynak_yolu) / (1024 * 1024)
        try:
            shutil.copy2(kaynak_yolu, hedef_yolu)
            aktarildi_olarak_kaydet(dosya_adi)
            log(f"[AKTARILDI] {dosya_adi} ({boyut_mb:.1f} MB) -> {hedef_klasor}")
            basarili += 1

            # --- KAYNAK DOSYAYI SIL (Commas klasöründen) ---
            try:
                os.remove(kaynak_yolu)
                log(f"[SILINDI] Kaynak dosya silindi: {dosya_adi}")
            except Exception as se:
                log(f"[UYARI] Kaynak silinemedi [{dosya_adi}]: {se}")

        except Exception as e:
            log(f"[HATA] Kopyalama hatasi [{dosya_adi}]: {e}")

    if basarili > 0:
        log(f"[TAMAM] Bu turda {basarili} dosya aktarildi ve kaynaktan silindi.")
    if beklenen > 0:
        log(f"[BEKLE] {beklenen} dosya bir sonraki turda yeniden denenecek.")


def ilk_envanter():
    """Başlangıçta kaynak klasörünü raporlar."""
    if not os.path.exists(KAYNAK_DIR):
        log(f"[HATA] Kaynak klasor YOK -> {KAYNAK_DIR}")
        return
    dosyalar = [
        f for f in os.listdir(KAYNAK_DIR)
        if f.startswith(DOSYA_ONEK) and f.endswith(DOSYA_UZANTI)
    ]
    toplam_mb = sum(
        os.path.getsize(os.path.join(KAYNAK_DIR, f))
        for f in dosyalar
    ) / (1024 * 1024)
    log(f"[ENVANTER] Kaynak: {len(dosyalar)} dosya | Toplam: {toplam_mb:.1f} MB")


def done_temizligi():
    """
    system_core Done/ klasorune tasidigi .bin dosyalarini temizler.
    Commas kaynagi coktan silindi; Done/ kopya gereksiz kalmistir.
    """
    done_dir = os.path.join(ARSIV_DIR, "Done")
    if not os.path.exists(done_dir):
        return
    silinen = 0
    for kok, _, dosyalar in os.walk(done_dir):
        for f in dosyalar:
            if f.startswith(DOSYA_ONEK) and f.endswith(DOSYA_UZANTI):
                tam_yol = os.path.join(kok, f)
                try:
                    os.remove(tam_yol)
                    silinen += 1
                    log(f"[DONE-SILINDI] Islenmis kopya silindi: {f}")
                except Exception as e:
                    log(f"[UYARI] Done silme hatasi [{f}]: {e}")
    if silinen > 0:
        log(f"[DONE-TEMIZLIK] {silinen} islenmis .bin dosyasi Done/ icinden temizlendi.")


def main():
    log("=" * 60)
    log("  [BASLAT] VERI AKTARICI - COMMAS KAYNAGI ETKINLESTIRILDI")
    log(f"  Kaynak : {KAYNAK_DIR}")
    log(f"  Hedef  : {ARSIV_DIR}")
    log(f"  Tarama : Her {BEKLEME_SN} saniyede bir")
    log("  Not    : Aktarilan kaynak dosyalar otomatik silinir.")
    log("=" * 60)

    ilk_envanter()

    while True:
        try:
            tarama_ve_aktar()
            done_temizligi()   # System_Core'un Done/ icine attigi .bin kopyalarini sil
        except Exception as e:
            log(f"[HATA] BEKLENMEYEN HATA: {e}")
        time.sleep(BEKLEME_SN)


if __name__ == "__main__":
    main()
