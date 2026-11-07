@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3 is not installed. Install it from python.org first.
    pause
    exit /b 1
  )
  set "PY=python"
)
%PY% queue.py init
%PY% queue.py enqueue --agent kiro --kind story_outline
%PY% queue.py run-once
%PY% queue.py status
echo.
echo Prototype finished. This does NOT run AI models or render video.
pause
