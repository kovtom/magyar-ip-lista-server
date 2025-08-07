@echo off
REM Gunicorn production server starter for Windows

echo Starting Hungarian IP List Server with Gunicorn...

REM Virtual environment aktiválása és Gunicorn indítása Windows-on
if exist ".venv\Scripts\activate" (
    call .venv\Scripts\activate
    echo Virtual environment activated
) else (
    echo Warning: Virtual environment not found, using system Python
)

.venv\Scripts\gunicorn.exe ^
    --workers 4 ^
    --bind 0.0.0.0:5000 ^
    --timeout 120 ^
    --keepalive 5 ^
    --max-requests 1000 ^
    --max-requests-jitter 100 ^
    --preload ^
    --access-logfile - ^
    --error-logfile - ^
    hulista:app

pause
