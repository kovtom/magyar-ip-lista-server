#!/bin/bash
# Gunicorn production server starter

# Gunicorn konfigurációs változók
WORKERS=4                    # Worker processek száma
BIND="0.0.0.0:5000"         # Host és port
TIMEOUT=120                  # Timeout másodpercekben
KEEPALIVE=5                  # Keep-alive kapcsolatok
MAX_REQUESTS=1000           # Maximális kérések worker-enként
MAX_REQUESTS_JITTER=100     # Véletlenszerűség a restart-ban

# Gunicorn indítása
exec gunicorn \
    --workers $WORKERS \
    --bind $BIND \
    --timeout $TIMEOUT \
    --keepalive $KEEPALIVE \
    --max-requests $MAX_REQUESTS \
    --max-requests-jitter $MAX_REQUESTS_JITTER \
    --preload \
    --access-logfile - \
    --error-logfile - \
    hulista:app
