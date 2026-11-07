@echo off
rem Menjalankan worker terus-menerus. Hentikan dengan STOP_WINDOWS.bat atau tutup jendela ini (Ctrl+C).
rem Worker ini belum dipasang sebagai layanan otomatis dan tidak berjalan saat komputer dinyalakan.
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3 belum terpasang. Pasang dari python.org dulu.
    pause
    exit /b 1
  )
  set "PY=python"
)
%PY% jobqueue.py worker
pause
