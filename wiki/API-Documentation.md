# API Dokumentáció

> **Teljes Flask API referencia a Magyar IP Lista Server használatához**

## 🔌 API Áttekintés

A Magyar IP Lista Server RESTful API-t biztosít, amely lehetővé teszi a magyar IP címek listájának lekérését különböző formátumokban.

### API Alap URL
```
http://[szerver-ip]:5000
```

### Támogatott Formátumok
- **MikroTik RouterOS** (.rsc)
- **Egyszerű szöveges** (.txt)
- **JSON** formátum
- **CSV** formátum

## 📋 Endpoint Dokumentáció

### 1. Szerver Állapot Lekérdezése

**Endpoint:** `GET /status`

**Leírás:** Visszaadja a szerver aktuális állapotát és információit.

**Kérés:**
```http
GET /status HTTP/1.1
Host: 192.168.1.100:5000
```

**Válasz:**
```json
{
    "status": "running",
    "version": "2.0.0",
    "timestamp": "2024-12-19 15:30:45",
    "server_ip": "192.168.1.100",
    "uptime": "2 days, 5 hours, 30 minutes",
    "last_update": "2024-12-19 12:00:00",
    "ip_count": 903,
    "endpoints": [
        "/status",
        "/hu_ip_list.rsc",
        "/hu_ip_list.txt", 
        "/api/v1/ips",
        "/api/v1/ips/csv"
    ]
}
```

**Státusz kódok:**
- `200 OK` - Sikeres lekérdezés
- `500 Internal Server Error` - Szerver hiba

### 2. MikroTik RouterOS Script

**Endpoint:** `GET /hu_ip_list.rsc`

**Leírás:** Visszaadja a magyar IP címeket MikroTik RouterOS script formátumban kötegelt feldolgozással.

**Kérés:**
```http
GET /hu_ip_list.rsc HTTP/1.1
Host: 192.168.1.100:5000
```

**Válasz:**
```routeros
# Magyar IP Lista - MikroTik RouterOS Script
# Generálva: 2024-12-19 15:30:45
# IP címek száma: 903
# 
# FIGYELEM: Ez a script kötegelt feldolgozást használ!
# 50 IP címenként 30 másodperc szünetet tart a router védelme érdekében.

:log info "Magyar IP lista betöltése kezdődik - Köteg 1/18"
/ip firewall address-list add list=HU_IP address=2.16.0.0/13 comment="HU-IP-1"
/ip firewall address-list add list=HU_IP address=2.24.0.0/13 comment="HU-IP-2"
# ... további 48 IP cím
:delay 30
:log info "Köteg 1/18 betöltve, 30 másodperc szünet..."

:log info "Magyar IP lista betöltése folytatódik - Köteg 2/18"
# ... következő 50 IP cím
```

**Response Headers:**
```
Content-Type: text/plain; charset=utf-8
Content-Disposition: attachment; filename="hu_ip_list.rsc"
```

### 3. Egyszerű Szöveges Lista

**Endpoint:** `GET /hu_ip_list.txt`

**Leírás:** Visszaadja a magyar IP címeket egyszerű szöveges formátumban.

**Kérés:**
```http
GET /hu_ip_list.txt HTTP/1.1
Host: 192.168.1.100:5000
```

**Válasz:**
```
# Magyar IP Lista - Szöveges Formátum
# Generálva: 2024-12-19 15:30:45
# IP címek száma: 903

2.16.0.0/13
2.24.0.0/13
5.28.0.0/15
31.0.0.0/12
37.17.0.0/16
46.107.0.0/16
# ... további IP címek
```

**Response Headers:**
```
Content-Type: text/plain; charset=utf-8
Content-Disposition: attachment; filename="hu_ip_list.txt"
```

### 4. JSON API v1

**Endpoint:** `GET /api/v1/ips`

**Leírás:** Visszaadja a magyar IP címeket strukturált JSON formátumban.

**Kérés:**
```http
GET /api/v1/ips HTTP/1.1
Host: 192.168.1.100:5000
Accept: application/json
```

**Válasz:**
```json
{
    "metadata": {
        "generated_at": "2024-12-19T15:30:45.123456",
        "ip_count": 903,
        "country": "HU",
        "country_name": "Hungary",
        "data_source": "https://www.nirsoft.net/countryip/hu.html",
        "format_version": "1.0",
        "batch_processing": {
            "enabled": true,
            "batch_size": 50,
            "delay_seconds": 30,
            "total_batches": 18
        }
    },
    "ip_ranges": [
        {
            "network": "2.16.0.0/13",
            "start_ip": "2.16.0.0",
            "end_ip": "2.23.255.255",
            "total_ips": 524288,
            "batch_number": 1
        },
        {
            "network": "2.24.0.0/13", 
            "start_ip": "2.24.0.0",
            "end_ip": "2.31.255.255",
            "total_ips": 524288,
            "batch_number": 1
        }
        // ... további IP tartományok
    ],
    "statistics": {
        "total_networks": 903,
        "total_ip_addresses": 67108864,
        "largest_network": "2.16.0.0/13",
        "smallest_network": "195.199.200.0/24"
    }
}
```

**Response Headers:**
```
Content-Type: application/json; charset=utf-8
```

### 5. CSV Export

**Endpoint:** `GET /api/v1/ips/csv`

**Leírás:** Visszaadja a magyar IP címeket CSV formátumban.

**Kérés:**
```http
GET /api/v1/ips/csv HTTP/1.1
Host: 192.168.1.100:5000
```

**Válasz:**
```csv
network,start_ip,end_ip,total_ips,batch_number,comment
2.16.0.0/13,2.16.0.0,2.23.255.255,524288,1,HU-IP-1
2.24.0.0/13,2.24.0.0,2.31.255.255,524288,1,HU-IP-2
5.28.0.0/15,5.28.0.0,5.29.255.255,131072,1,HU-IP-3
```

**Response Headers:**
```
Content-Type: text/csv; charset=utf-8
Content-Disposition: attachment; filename="hungarian_ips.csv"
```

## 🔄 Kötegelt Feldolgozás API

### Köteg Információ Lekérdezése

**Endpoint:** `GET /api/v1/batches`

**Leírás:** Visszaadja a kötegelt feldolgozás részleteit.

**Válasz:**
```json
{
    "batch_config": {
        "batch_size": 50,
        "delay_seconds": 30,
        "total_batches": 18
    },
    "batches": [
        {
            "batch_number": 1,
            "ip_count": 50,
            "start_index": 0,
            "end_index": 49,
            "estimated_duration": "0 seconds"
        },
        {
            "batch_number": 2,
            "ip_count": 50,
            "start_index": 50,
            "end_index": 99,
            "estimated_duration": "30 seconds"
        }
        // ... további kötegek
    ],
    "total_processing_time": "510 seconds"
}
```

## 🧪 API Tesztelés

### cURL Példák

**Állapot lekérdezése:**
```bash
curl -X GET http://192.168.1.100:5000/status
```

**MikroTik script letöltése:**
```bash
curl -X GET http://192.168.1.100:5000/hu_ip_list.rsc -o hu_ip_list.rsc
```

**JSON formátum:**
```bash
curl -X GET http://192.168.1.100:5000/api/v1/ips \
  -H "Accept: application/json" | jq '.'
```

**CSV export:**
```bash
curl -X GET http://192.168.1.100:5000/api/v1/ips/csv -o hungarian_ips.csv
```

### PowerShell Példák

**Állapot lekérdezése:**
```powershell
Invoke-RestMethod -Uri "http://192.168.1.100:5000/status" -Method Get
```

**JSON letöltés és feldolgozás:**
```powershell
$response = Invoke-RestMethod -Uri "http://192.168.1.100:5000/api/v1/ips" -Method Get
$response.metadata.ip_count
$response.ip_ranges | Select-Object network, total_ips
```

### Python Példák

**Alapvető használat:**
```python
import requests
import json

# Szerver állapot
response = requests.get('http://192.168.1.100:5000/status')
status = response.json()
print(f"IP count: {status['ip_count']}")

# JSON API használat
response = requests.get('http://192.168.1.100:5000/api/v1/ips')
data = response.json()

for ip_range in data['ip_ranges']:
    print(f"{ip_range['network']} - {ip_range['total_ips']} IPs")
```

**Fájl letöltés:**
```python
import requests

# MikroTik script letöltés
response = requests.get('http://192.168.1.100:5000/hu_ip_list.rsc')
with open('hu_ip_list.rsc', 'w', encoding='utf-8') as f:
    f.write(response.text)

print("MikroTik script letöltve!")
```

## 🔐 Biztonsági Megfontolások

### Rate Limiting

A szerver alapértelmezetten nem implementál rate limiting-et, de éles környezetben ajánlott:

```python
# Nginx rate limiting példa
location /api/ {
    limit_req zone=api burst=10 nodelay;
    proxy_pass http://127.0.0.1:5000;
}
```

### Access Control

**IP alapú korlátozás:**
```python
ALLOWED_IPS = ['192.168.1.0/24', '10.0.0.0/8']

@app.before_request
def check_ip():
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if not any(ipaddress.ip_address(client_ip) in ipaddress.ip_network(allowed) 
               for allowed in ALLOWED_IPS):
        abort(403)
```

### HTTPS Implementáció

**SSL Tanúsítványok:**
```python
# HTTPS futtatás
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, 
            ssl_context=('cert.pem', 'key.pem'))
```

## 📊 Monitoring és Metrikák

### Prometheus Metrikák

A szerver alapértelmezetten nem ad ki Prometheus metrikákat, de implementálható:

```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

### Alapvető Statisztikák

**Állapot monitoring endpoint fejlesztés:**
```json
{
    "uptime_seconds": 172800,
    "total_requests": 1234,
    "requests_per_minute": 2.5,
    "last_requests": [
        {
            "timestamp": "2024-12-19T15:30:45",
            "endpoint": "/hu_ip_list.rsc",
            "client_ip": "192.168.1.1",
            "user_agent": "MikroTik/6.48.6"
        }
    ]
}
```

## 🚀 Teljesítmény Optimalizáció

### Caching

**Redis cache implementáció:**
```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_response(timeout=3600):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            if cached:
                return cached.decode('utf-8')
            result = f(*args, **kwargs)
            redis_client.setex(cache_key, timeout, result)
            return result
        return decorated_function
    return decorator
```

### Kompresszió

**GZip kompresszió:**
```python
from flask_compress import Compress

compress = Compress()
compress.init_app(app)
```

## 🔧 Egyedi API Implementáció

### Saját Endpoint Létrehozása

```python
@app.route('/api/v1/stats', methods=['GET'])
def get_statistics():
    """API statisztikák visszaadása"""
    stats = {
        'total_networks': len(hungarian_ips),
        'total_ip_addresses': sum(ipaddress.ip_network(ip).num_addresses 
                                 for ip in hungarian_ips),
        'largest_network': max(hungarian_ips, 
                              key=lambda x: ipaddress.ip_network(x).num_addresses),
        'update_frequency': '24 hours',
        'data_freshness': 'daily'
    }
    return jsonify(stats)
```

### Webhook Integráció

```python
@app.route('/webhook/update', methods=['POST'])
def webhook_update():
    """Külső rendszerből trigger"""
    if request.headers.get('Authorization') != 'Bearer YOUR_SECRET_TOKEN':
        abort(401)
    
    # IP lista frissítése
    download_and_convert_ips()
    
    return jsonify({'status': 'updated', 'timestamp': datetime.now().isoformat()})
```

## 📚 SDK Fejlesztés

### Python SDK Példa

```python
class HungarianIPClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        
    def get_status(self):
        response = requests.get(f"{self.base_url}/status")
        return response.json()
    
    def get_ips_json(self):
        response = requests.get(f"{self.base_url}/api/v1/ips")
        return response.json()
    
    def download_mikrotik_script(self, output_path):
        response = requests.get(f"{self.base_url}/hu_ip_list.rsc")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)

# Használat
client = HungarianIPClient('http://192.168.1.100:5000')
status = client.get_status()
print(f"Server has {status['ip_count']} IP addresses")
```

## 📋 API Verziókezelés

### Jövőbeli v2 API Tervezés

```python
@app.route('/api/v2/ips', methods=['GET'])
def get_ips_v2():
    """Fejlettebb API v2-ben"""
    return jsonify({
        'version': '2.0',
        'data': {
            'ip_ranges': hungarian_ips,
            'metadata': {
                'pagination': {
                    'page': 1,
                    'per_page': 100,
                    'total': len(hungarian_ips)
                }
            }
        }
    })
```

## ⚠️ Hibaelhárítás

### Gyakori API Hibák

**1. Connection Refused:**
- Szerver fut-e?
- Port elérhető-e?
- Firewall beállítások

**2. Timeout:**
- Hálózati kapcsolat
- Szerver terhelés
- DNS feloldás

**3. 404 Not Found:**
- Helyes endpoint használata
- API verzió ellenőrzése

### Debug Beállítások

```python
import logging

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

@app.before_request
def log_request():
    app.logger.debug(f"Request: {request.method} {request.url}")
```

## 📚 Következő Lépések

- **[Hibaelhárítás](Troubleshooting)** - Részletes hibaelhárítási útmutató
- **[Fejlesztői Útmutató](Development-Guide)** - Szerver fejlesztése és testreszabása
- **[Integrációs Példák](Integration-Examples)** - Valós használati esetek

---

**API dokumentáció kész! Következő: [Hibaelhárítás](Troubleshooting)** 🚀
