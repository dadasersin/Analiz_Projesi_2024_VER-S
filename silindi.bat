@echo off
chcp 65001 >nul
title ANTIGRAVITY - TEMIZLIK MOTORU
color 0C
cd /d "%~dp0"

echo.
echo  ======================================================
echo   ANTIGRAVITY - SILINDI.BAT - OTOMATIK TEMIZLIK
echo  ======================================================
echo.

:: ---- DONE klasoru temizligi ----
set DONE_DIR=%~dp0Arsiv_Deposu\Done
set COP_DIR=%~dp0Cop_Kutusu

echo  [1] Islenmis dosyalar (Done/) siliniyor...
if exist "%DONE_DIR%\" (
    for /f %%i in ('dir /b /s "%DONE_DIR%\*.*" 2^>nul') do (
        echo      Silindi: %%~nxi
        del /f /q "%%i" >nul 2>&1
    )
    echo  [OK] Done/ klasoru temizlendi.
) else (
    echo  [!!] Done/ klasoru bulunamadi: %DONE_DIR%
)

:: ---- COP KUTUSU temizligi ----
echo.
echo  [2] Cop Kutusu temizleniyor...
if exist "%COP_DIR%\" (
    for /f %%i in ('dir /b /s "%COP_DIR%\*.*" 2^>nul') do (
        echo      Silindi: %%~nxi
        del /f /q "%%i" >nul 2>&1
    )
    :: Bos alt klasorleri de sil
    for /d /r "%COP_DIR%" %%d in (*) do (
        rd /s /q "%%d" >nul 2>&1
    )
    echo  [OK] Cop Kutusu temizlendi.
) else (
    echo  [!!] Cop Kutusu bulunamadi: %COP_DIR%
)

:: ---- COMMAS kaynagindaki islenip aktarilan .bin dosyalarini sil ----
echo.
echo  [3] Commas kaynagindaki islenmis .bin dosyalari siliniyor...
set COMMAS_DIR=D:\google driver commas\Project_Analiz_Data
set KAYIT=%~dp0aktarilan_dosyalar.log

if exist "%COMMAS_DIR%\" (
    if exist "%KAYIT%" (
        for /f "tokens=*" %%f in (%KAYIT%) do (
            if exist "%COMMAS_DIR%\%%f" (
                del /f /q "%COMMAS_DIR%\%%f" >nul 2>&1
                echo      Silindi (Commas): %%f
            )
        )
        echo  [OK] Commas kaynagi temizlendi.
    ) else (
        echo  [!!] Kayit dosyasi bulunamadi: %KAYIT%
    )
) else (
    echo  [!!] Commas klasoru bulunamadi: %COMMAS_DIR%
)

echo.
echo  ======================================================
echo   [TAMAM] TEMIZLIK TAMAMLANDI!
echo  ======================================================
echo.

:: Eger silindi.bat dogrudan acildiysa kullaniciya bildir
if "%1"=="auto" (
    timeout /t 3 /nobreak >nul
) else (
    pause
)
