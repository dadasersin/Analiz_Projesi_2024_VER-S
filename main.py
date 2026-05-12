"""
========================================================
  ANTIGRAVITY MASTER DASHBOARD v3.0 - Otonom Komuta
========================================================
  Gorev : Tum modulleri tek bir ekranda izler.
          VRSC Kazanc Tahmini | Termal Takip | Veri Akisi
========================================================
"""
import os
import time
import sys
from datetime import datetime
import verus_stats

# --- YAPILANDIRMA ---
PROJE_DIR    = os.path.dirname(os.path.abspath(__file__))
WALLET       = "RB2dBo22HqmG3hPKBiSQCW9bPpznzYZJB7"
ARSIV_DIR    = os.path.join(PROJE_DIR, "Arsiv_Deposu")
DONE_DIR     = os.path.join(ARSIV_DIR, "Done")
COP_DIR      = os.path.join(PROJE_DIR, "Cop_Kutusu")
DRIVE_KAYNAK = os.path.join("D:", "Project_Backup") # Örnek Drive yolu
COMMAS_DIR   = os.path.join("D:", "google driver commas", "Project_Analiz_Data")
GUARDIAN_LOG = os.path.join(PROJE_DIR, "guardian_status.txt")
MINER_LOG    = os.path.join(PROJE_DIR, "miner_log.txt") # Yeni log takibi
MAX_KOTA_GB  = 14.0
YENILE_SN    = 5

def get_guardian_data():
    if os.path.exists(GUARDIAN_LOG):
        try:
            with open(GUARDIAN_LOG, "r", encoding="utf-8") as f:
                parts = f.read().split("|")
                return {"temp": float(parts[0]), "status": parts[1], "threads": parts[2]}
        except: pass
    return {"temp": 0, "status": "Beklemede", "threads": "?"}

def get_miner_log():
    """Hellminer logundan son satırı çeker."""
    if os.path.exists(MINER_LOG):
        try:
            with open(MINER_LOG, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                if lines:
                    # En son anlamlı satırı bul (boş olmayan)
                    for line in reversed(lines):
                        if line.strip() and "---" not in line:
                            return line.strip()[:64]
        except: pass
    return "Log bekleniyor..."

def format_bar(val, max_val, width=30):
    per = min(val / max_val, 1.0)
    filled = int(per * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] %{per*100:.1f}"

def ekrani_goster():
    os.system("cls")
    now = datetime.now()
    
    # Verileri Hazırla
    m = verus_stats.fetch_miner()
    p = verus_stats.fetch_payments()
    e = verus_stats.fetch_earnings()
    v = verus_stats.parse_stats(m, p, e)
    g = get_guardian_data()
    
    # Klasör Boyutları
    def get_dir_size(path):
        t, c = 0, 0
        if os.path.exists(path):
            for r, _, files in os.walk(path):
                for f in files:
                    t += os.path.getsize(os.path.join(r, f))
                    c += 1
        return c, t / (1024**3)

    arsiv_c, arsiv_g = get_dir_size(ARSIV_DIR)
    done_c, done_g = get_dir_size(DONE_DIR)
    
    # Baglanti Mesaji (Kullanici istegi)
    conn_msg = f"Hellminer sisteme baglandi. https://luckpool.net/verus/miner.html?{WALLET} adresine {done_g:.2f} GB veri aktarildi."
    
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "🚀 ANTIGRAVITY MASTER DASHBOARD v3.2" + " " * 12 + "║")
    print("║" + f"  {now.strftime('%Y-%m-%d %H:%M:%S'):<64}" + "  ║")
    print("╠" + "═" * 68 + "╣")
    print(f"║ 📡 {conn_msg[:64]:<64} ║")
    print("╠" + "═" * 68 + "╣")

    
    # BÖLÜM 1: MADENCİLİK (POOL & PROFIT)
    print("║ 💎 [POOLS & EARNINGS] " + " " * 44 + "║")
    if not v["error"]:
        hr = verus_stats.format_hashrate(v["hashrate_h"])
        print(f"║  Hashrate : {hr:<16} | Worker : Rig001 {' ':<18} ║")
        print(f"║  Kazanilan: {v['paid_vrsc']:.6f} VRSC | Bekleyen: {v['pending_vrsc']:.6f} VRSC {' ':<2} ║")
        print(f"║  Gunluk   : ~{v['projections']['daily']:.4f} VRSC | Aylik   : ~{v['projections']['monthly']:.4f} VRSC {' ':<3} ║")
    else:
        print(f"║  [!] Pool Durumu: {v['error']:<48} ║")
    
    print("╠" + "─" * 68 + "╣")
    
    # BÖLÜM 2: SİSTEM SAĞLIĞI & MADENCİ AKIŞI
    print("║ 🌡️  [SYSTEM & MINER LIVE FLOW] " + " " * 38 + "║")
    t_color = "!" if g["temp"] > 65 else " "
    print(f"║  CPU: {g['temp']:.1f}°C {t_color} | Durum: {g['status']:<11} | Log: {get_miner_log():<22} ║")
    print(f"║  {format_bar(g['temp'], 80, 40)} {' ':<25} ║")
    
    print("╠" + "─" * 68 + "╣")

    # BÖLÜM 3: VERİ FABRİKASI (THROUGHPUT)
    print("║ 🏭 [DATA FACTORY - THROUGHPUT] " + " " * 35 + "║")
    verimlilik = (done_g / (arsiv_g + done_g) * 100) if (arsiv_g + done_g) > 0 else 100
    print(f"║  Islenen Toplam: {done_c:<5} Paket | Verimlilik Skoru: %{verimlilik:.1f} {' ':<13} ║")
    print(f"║  Depolama: {arsiv_g:.2f} GB / {MAX_KOTA_GB} GB {' ':<37} ║")
    print(f"║  {format_bar(arsiv_g, MAX_KOTA_GB, 40)} {' ':<23} ║")
    
    print("╚" + "═" * 68 + "╝")
    print(" 🔄 5 saniyede bir otomatik yenilenir. Durdurmak için [CTRL+C]")

def main():
    try:
        while True:
            ekrani_goster()
            time.sleep(YENILE_SN)
    except KeyboardInterrupt:
        print("\n[!] Dashboard kapatildi.")

if __name__ == "__main__":
    main()
