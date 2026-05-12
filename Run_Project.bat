@echo off
chcp 65001 >nul
title ANTIGRAVITY - VERİ FABRİKASI
color 0A
cd /d "%~dp0"

echo.
echo  ╔═══════════════════════════════════════════════════════╗
echo  ║      ANTIGRAVITY VERİ FABRİKASI - ANA SALTER         ║
echo  ║  Colab ^| Drive ^| Tasıyıcı ^| Commas ^| Core ^| Backup  ║
echo  ╚═══════════════════════════════════════════════════════╝
echo.

:: --- PYTHON KONTROLÜ ---
python --version >nul 2>&1
if errorlevel 1 (
    echo  [!] HATA: Python bulunamadi. Kurulu ve PATH'e ekli oldugundan emin olun.
    pause
    exit /b 1
)

:: --- GOOGLE DRIVE KLASÖRÜ KONTROLÜ ---
if not exist "C:\Users\ersin\Drive'ım (onatsemra@gmail.com) (1)\Scientific_Data_Backup" (
    echo  [!] UYARI: Google Drive Scientific_Data_Backup klasoru bulunamadi.
    echo      Google Drive masaustu uygulamasi calisiyor mu?
    echo.
)

:: --- COMMAS VERİ KLASÖRÜ KONTROLÜ ---
if not exist "D:\google driver commas\Project_Analiz_Data" (
    echo  [!] UYARI: Commas veri klasoru bulunamadi → D:\google driver commas\Project_Analiz_Data
    echo      Klasor bagli ve erisebilir mi kontrol edin.
    echo.
)

:: --- 1. TAŞIYICI (Drive → Arsiv_Deposu) ---
echo  [1] Tasiyici servisi arka planda baslatiliyor...
start /min "ANTIGRAVITY-Tasiyici" python tasiyici.py

:: --- 2. VERİ AKTARICI (Commas → Arsiv_Deposu) ---
echo  [2] Veri Aktarici (commas kaynagi) arka planda baslatiliyor...
start /min "ANTIGRAVITY-VeriAktarici" python veri_aktarici.py

:: --- 3. SYSTEM CORE (Arsiv_Deposu dosyalarını işle) ---
echo  [3] System Core isleme motoru arka planda baslatiliyor...
start /min "ANTIGRAVITY-SystemCore" python system_core.py

:: --- 4. BACKUP MANAGER (Kota yonetimi, 14 GB sınırı) ---
echo  [4] Backup Manager kota koruyucu arka planda baslatiliyor...
start /min "ANTIGRAVITY-BackupMgr" python backup_manager.py

:: --- 5. GUARDIAN (Ana süreç, sıcaklık + kaynak yönetimi) ---
echo  [4] Guardian sistem koruyucu on planda baslatiliyor...
echo.
echo  ─────────────────────────────────────────────────────────
echo  Sistem aktif. Kapatmak icin bu pencereyi kapatin.
echo  ─────────────────────────────────────────────────────────
echo.

python guardian.py

pause