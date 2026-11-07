@echo off
rem Meminta worker berhenti dengan aman setelah tugas yang sedang berjalan selesai.
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 jobqueue.py stop
) else (
  python jobqueue.py stop
)
pause
