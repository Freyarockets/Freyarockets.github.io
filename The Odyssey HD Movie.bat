@echo off
setlocal EnableDelayedExpansion

:: ============================================================
::  StarDust OS Downloader (Resume-safe)
::  File: TheOdyssey HD Movie BluRay mp4.bat
:: ============================================================

set FILE_ID=1dYxKR-wbLobHPLmO6vHf6Jh5kbDa4sDd
set OUTPUT=StarDustOS.iso

echo.
echo  ========================================
echo    StarDust OS Downloader
echo  ========================================
echo.
echo  File ID : %FILE_ID%
echo  Output  : %OUTPUT%
echo.
echo  This script supports RESUME.
echo  If the download is interrupted, just run
echo  this .bat again and it will continue.
echo.

:: Clean temporary files from previous runs
if exist cookies.txt del cookies.txt >nul 2>&1
if exist confirm.html del confirm.html >nul 2>&1

:: ------------------------------------------------------------
:: Step 1: Visit the download page and save cookies + HTML
:: ------------------------------------------------------------
echo [1/3] Fetching Google Drive confirmation page...
curl -s -c cookies.txt -b cookies.txt -L "https://drive.google.com/uc?export=download&id=%FILE_ID%" -o confirm.html

if not exist confirm.html (
    echo ERROR: Could not reach Google Drive.
    goto :end
)

:: ------------------------------------------------------------
:: Step 2: Try to extract the confirm token (needed for large files)
:: ------------------------------------------------------------
set CONFIRM=

:: Look for confirm=XXXX pattern in the HTML
for /f "tokens=2 delims==&" %%A in ('findstr /i /c:"confirm=" confirm.html 2^>nul') do (
    set CONFIRM=%%A
    goto :token_found
)

:token_found
if defined CONFIRM (
    echo [2/3] Confirm token found: !CONFIRM!
    set "DOWNLOAD_URL=https://drive.google.com/uc?export=download&confirm=!CONFIRM!&id=%FILE_ID%"
) else (
    echo [2/3] No confirm token detected - trying with confirm=t fallback
    set "DOWNLOAD_URL=https://drive.google.com/uc?export=download&confirm=t&id=%FILE_ID%"
)

:: ------------------------------------------------------------
:: Step 3: Download with resume support (-C -)
:: ------------------------------------------------------------
echo [3/3] Starting download...
echo.
echo  Tip: You can close this window anytime.
echo       Re-run the script later to resume.
echo.

curl -L -C - -b cookies.txt --progress-bar -o "%OUTPUT%" "%DOWNLOAD_URL%"

set ERR=%errorlevel%

echo.
if %ERR% equ 0 (
    echo  ========================================
    echo    DOWNLOAD COMPLETED SUCCESSFULLY
    echo    Saved as: %OUTPUT%
    echo  ========================================
) else (
    echo  ========================================
    echo    Download interrupted or failed
    echo    (Error code: %ERR%)
    echo.
    echo    Just run this script again to RESUME
    echo    from where it left off.
    echo  ========================================
)

:end
:: Cleanup temporary files
if exist cookies.txt del cookies.txt >nul 2>&1
if exist confirm.html del confirm.html >nul 2>&1

echo.
pause
