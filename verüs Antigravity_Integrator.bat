@echo off
chcp 65001 >nul
title VERUS ANTIGRAVITY INTEGRATOR
color 0A
cd /d "%~dp0"

cls
echo.
echo  ============================================================
echo   ANTIGRAVITY VERUS ENTEGRATOR - BASLANIYOR
echo  ============================================================
echo.

:: ---- VERÜS MADENCILIK ISTATISTIKLERI ----
echo  Luckpool API'den VERUS istatistikleri aliniyor...
echo.
python verus_stats.py
echo.

:: ---- OTOMATIK TEMIZLIK (silindi.bat) ----
echo  [AUTO] Onceki oturum verileri temizleniyor (silindi.bat)...
call silindi.bat auto
echo  [OK] Temizlik tamamlandi.
echo.

:: ---- PYTHON KONTROLÜ ----
python --version >nul 2>&1
if errorlevel 1 (
    echo  [!!] HATA: Python bulunamadi!
    pause
    exit /b 1
)

:: ---- COMMAS KLASOR KONTROLÜ ----
if not exist "D:\google driver commas\Project_Analiz_Data\" (
    echo  [!!] UYARI: Commas veri klasoru bulunamadi.
    echo       D:\google driver commas\Project_Analiz_Data
    echo.
)

:: ---- DRIVE KLASÖR KONTROLÜ ----
if not exist "C:\Users\ersin\Drive'ım (onatsemra@gmail.com) (1)\Scientific_Data_Backup\" (
    echo  [!!] UYARI: Google Drive klasoru bulunamadi.
    echo.
)

echo  ============================================================
echo   PIPELINE MODULLERI BASLATILIYOR
echo  ============================================================
echo.

:: 1. TAŞIYICI (Google Drive → Arsiv)
echo  [1] Tasiyici servisi baslatiliyor...
start /min "AG-Tasiyici" python tasiyici.py

:: 2. VERİ AKTARICI (Commas → Arsiv, sonra kaynak siler)
echo  [2] Veri Aktarici (Commas kaynagi) baslatiliyor...
start /min "AG-VeriAktarici" python veri_aktarici.py

:: 3. SYSTEM CORE
echo  [3] System Core isleme motoru baslatiliyor...
start /min "AG-SystemCore" python system_core.py

:: 4. BACKUP MANAGER
echo  [4] Backup Manager kota koruyucu baslatiliyor...
start /min "AG-BackupMgr" python backup_manager.py

:: 5. DASHBOARD (main.py)
echo  [5] Dashboard baslatiliyor...
start "AG-Dashboard" cmd /k "python main.py"

:: 6. CLOUD SYNC (Render Dashboard Güncelleyici)
echo  [6] Bulut Senkronizasyonu (Render) baslatiliyor...
start /min "AG-CloudSync" python cloud_sync.py

echo.
echo  ============================================================
echo   [AKTIF] TUM MODULLER CALISIYOR
echo   Kapatmak icin bu pencereyi kapatin.
echo  ============================================================
echo.

:: 6. GUARDIAN (ön planda — bu pencereyi yönetir)
python guardian.py

pause
