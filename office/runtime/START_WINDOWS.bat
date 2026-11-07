@echo off
rem Uji cepat: membuat 2 tugas contoh, mengerjakannya, lalu menampilkan laporan.
rem Klik dua kali aman: tugas contoh memakai kunci tetap, jadi tidak dobel.
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
%PY% jobqueue.py init
%PY% jobqueue.py enqueue --agent kiro --kind story_outline --key demo-story-outline
%PY% jobqueue.py enqueue --agent zek --kind quality_gate --key demo-quality-gate
%PY% jobqueue.py worker --until-empty
%PY% jobqueue.py status
echo.
echo Selesai. Ini TIDAK menjalankan model AI dan TIDAK membuat video.
echo Laporan ada di folder runtime-data (report.md).
pause
