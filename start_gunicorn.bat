@echo off
REM Gunicorn production server starter for Windows

echo Starting Hungarian IP List Server with Gunicorn...

REM Gunicorn indítása Windows-on
gunicorn ^
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
