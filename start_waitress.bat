@echo off
REM Waitress production server starter for Windows

echo Starting Hungarian IP List Server with Waitress (Windows compatible)...

REM Virtual environment aktiválása és Waitress indítása Windows-on
if exist ".venv\Scripts\activate" (
    call .venv\Scripts\activate
    echo Virtual environment activated
) else (
    echo Warning: Virtual environment not found, using system Python
)

echo.
echo Starting production server...
echo Server will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

.venv\Scripts\waitress-serve.exe ^
    --host=0.0.0.0 ^
    --port=5000 ^
    --threads=8 ^
    --connection-limit=1000 ^
    --cleanup-interval=30 ^
    --channel-timeout=120 ^
    hulista:app

pause
