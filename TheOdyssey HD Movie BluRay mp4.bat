@echo off
setlocal

:: Replace with your Google Drive file URL
set URL=https://drive.google.com/file/d/1dYxKR-wbLobHPLmO6vHf6Jh5kbDa4sDd/view?usp=drivesdk

:: Output filename
set OUTPUT=StarDust.iso

echo Downloading...
curl -L -C - -o "%OUTPUT%" "%URL%"

if %errorlevel%==0 (
    echo Download completed successfully.
) else (
    echo Download interrupted.
)

pause
