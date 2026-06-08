@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment not found, creating .venv...
    python -m venv .venv
    if errorlevel 1 goto :error
)

echo [INFO] Installing/updating dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo [INFO] Starting bot...
".venv\Scripts\python.exe" main.py
goto :end

:error
echo [ERROR] Failed to start bot.
pause
exit /b 1

:end
endlocal
