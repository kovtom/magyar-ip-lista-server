# Hibaelhárítási Útmutató

> **Részletes útmutató a Magyar IP Lista Server gyakori problémáinak megoldásához**

## 🎯 Hibaelhárítási Folyamat

### Diagnosztikai Lépések

1. **Probléma azonosítása** 📋
2. **Log fájlok ellenőrzése** 📄  
3. **Hálózati kapcsolat tesztelése** 🌐
4. **Konfiguráció validálása** ⚙️
5. **Megoldás implementálása** 🔧

## 🚨 Gyakori Problémák és Megoldások

### 1. Szerver Indítási Problémák

#### ❌ "Address already in use" hiba

**Tünetek:**
```
OSError: [Errno 98] Address already in use
```

**Okok:**
- Port 5000 már használatban
- Előző szerver folyamat még fut
- Más alkalmazás használja a portot

**Megoldások:**

**Linux/Mac:**
```bash
# Fut-e már a szerver?
ps aux | grep python | grep hulista

# Port használat ellenőrzése
sudo netstat -tlnp | grep :5000
# vagy
sudo lsof -i :5000

# Folyamat leállítása
sudo kill -9 [PID]

# Másik port használata
python hulista.py --port 5001
```

**Windows:**
```powershell
# Port használat ellenőrzése
netstat -an | findstr :5000

# Folyamat azonosítása
netstat -ano | findstr :5000

# Folyamat leállítása
taskkill /PID [PID] /F

# Vagy GUI-ban Task Manager használata
```

#### ❌ "Permission denied" hiba

**Tünetek:**
```
PermissionError: [Errno 13] Permission denied
```

**Okok:**
- 1024 alatti port használata nem root felhasználóval
- Fájl írási jogosultság hiánya
- Firewall blokkolja a portot

**Megoldások:**

```bash
# Magasabb port használata (1024+)
python hulista.py --port 8080

# Sudo futtatás (nem ajánlott production-ben)
sudo python hulista.py

# Fájl jogosultságok ellenőrzése
ls -la hulista.py
chmod +x hulista.py

# Firewall beállítás (Ubuntu)
sudo ufw allow 5000/tcp
```

### 2. Hálózati Kapcsolat Problémák

#### ❌ "Connection refused" hiba kliens oldalon

**Tünetek:**
```
requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionRefusedError(61, 'Connection refused'))
```

**Diagnosztika:**

```bash
# Szerver fut-e?
curl http://localhost:5000/status

# Hálózati elérhetőség
ping 192.168.1.100
telnet 192.168.1.100 5000

# Port scan
nmap -p 5000 192.168.1.100
```

**Megoldások:**

**1. Szerver konfigurációja:**
```python
# hulista.py módosítás - minden interfészen hallgatás
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
    #         ^^^^^^^^^^^
    #         NE localhost vagy 127.0.0.1
```

**2. Firewall beállítások:**
```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow from 192.168.1.0/24 to any port 5000

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload

# Windows Defender
netsh advfirewall firewall add rule name="Flask Server" dir=in action=allow protocol=TCP localport=5000
```

#### ❌ Lassú válaszidő

**Tünetek:**
- Több mint 10 másodperc válaszidő
- Timeout hibák
- Szakadozott kapcsolat

**Diagnosztika:**
```bash
# Válaszidő mérése
time curl http://192.168.1.100:5000/status

# Hálózati latencia
ping -c 10 192.168.1.100

# Bandwidth teszt
iperf3 -c 192.168.1.100
```

**Megoldások:**

**1. DNS optimalizáció:**
```bash
# /etc/hosts bejegyzés hozzáadása
echo "192.168.1.100 flask-server.local" >> /etc/hosts
```

**2. Keep-alive beállítások:**
```python
# requests session használata
import requests

session = requests.Session()
session.headers.update({'Connection': 'keep-alive'})
response = session.get('http://192.168.1.100:5000/status')
```

### 3. MikroTik Integration Problémák

#### ❌ Script nem tölt le fájlt

**Tünetek:**
```
RouterOS log: "failure: HTTP/1.1 404 Not Found"
```

**Diagnosztika:**

**RouterOS oldalon:**
```routeros
# Manuális teszt
/tool fetch url="http://192.168.1.100:5000/status" dst-path="test.txt"
/file print where name="test.txt"

# DNS teszt
/ping 192.168.1.100 count=5

# HTTP fejlécek ellenőrzése
/tool fetch url="http://192.168.1.100:5000/hu_ip_list.rsc" dst-path="debug.txt" keep-result=yes
```

**Megoldások:**

**1. URL ellenőrzése:**
```routeros
# Helyes URL formátum
:local SERVER_URL "http://192.168.1.100:5000/hu_ip_list.rsc"
#                                          ^^^^^^^^^^^^^^^^
#                                          Teljes endpoint path
```

**2. HTTP vs HTTPS:**
```routeros
# Ha HTTPS van beállítva a szerveren
:local SERVER_URL "https://192.168.1.100:5000/hu_ip_list.rsc"

# Tanúsítvány ellenőrzés letiltása (teszt célra)
/tool fetch url=$SERVER_URL dst-path="hu_ip_list.rsc" check-certificate=no
```

#### ❌ "Script execution error" RouterOS-ben

**Tünetek:**
```
RouterOS log: "Script execution error"
```

**Diagnosztika:**

```routeros
# Script futtatás debug módban
:log info "Script kezdete - debug"
/system script run HU_IP_Update
:log info "Script vége - debug"

# Részletes log
/log print where topics~"script"

# Memória ellenőrzése
/system resource print
```

**Gyakori okok és megoldások:**

**1. Nem megfelelő Policy jogosultságok:**
```routeros
# Script policy ellenőrzése
/system script print detail where name="HU_IP_Update"

# Helyes policy beállítás
/system script set HU_IP_Update policy=read,write,policy,test
```

**2. Túl nagy fájl méret:**
```routeros
# Memória ellenőrzése
/system resource print

# Ha kevés a memória, csökkentse a köteg méretet
:local BATCH_SIZE 25    # 50 helyett 25
:local DELAY_SECONDS 45  # 30 helyett 45
```

### 4. Python/Flask Specifikus Hibák

#### ❌ "ModuleNotFoundError" hiba

**Tünetek:**
```
ModuleNotFoundError: No module named 'flask'
```

**Megoldás:**

```bash
# Virtual environment aktiválása
source venv/bin/activate  # Linux/Mac
# vagy
venv\Scripts\activate.bat  # Windows

# Csomagok telepítése
pip install -r requirements.txt

# Ellenőrzés
pip list | grep -i flask
```

#### ❌ "Encoding errors" magyar karakterekkel

**Tünetek:**
```
UnicodeDecodeError: 'ascii' codec can't decode byte
```

**Megoldás:**

```python
# hulista.py-ban UTF-8 encoding biztosítása
import sys
import locale

# Encoding beállítása
if sys.platform.startswith('win'):
    locale.setlocale(locale.LC_ALL, 'Hungarian_Hungary.1252')
else:
    locale.setlocale(locale.LC_ALL, 'hu_HU.UTF-8')

# Fájl írás UTF-8-ban
with open('hu_ip_list.rsc', 'w', encoding='utf-8') as f:
    f.write(content)
```

#### ❌ "Out of memory" hiba nagy IP listáknál

**Tünetek:**
```
MemoryError: Unable to allocate array
```

**Megoldás:**

**1. Kötegelt feldolgozás optimalizálása:**
```python
def generate_mikrotik_commands_chunked(ip_list, batch_size=25):
    """Memória-hatékony kötegelt feldolgozás"""
    for i in range(0, len(ip_list), batch_size):
        batch = ip_list[i:i + batch_size]
        yield generate_batch_commands(batch, i // batch_size + 1)
```

**2. Generator használata:**
```python
@app.route('/hu_ip_list.rsc')
def mikrotik_script():
    def generate():
        yield "# Magyar IP Lista - MikroTik RouterOS Script\n"
        for batch_commands in generate_mikrotik_commands_chunked(hungarian_ips):
            yield batch_commands
    
    return Response(generate(), mimetype='text/plain')
```

### 5. Teljesítmény Problémák

#### ❌ Szerver túlterhelés

**Tünetek:**
- CPU használat 100%
- Lassú válaszidők
- Memory leak

**Diagnosztika:**

```bash
# Szerver terhelés ellenőrzése
top -p $(pgrep -f hulista)
htop

# Memória használat
free -h
ps aux | grep python

# Hálózati forgalom
iftop
nethogs
```

**Megoldások:**

**1. Production WSGI szerver használata:**
```bash
# Gunicorn (Linux/Mac)
gunicorn --workers 4 --bind 0.0.0.0:5000 hulista:app

# Waitress (Windows)
waitress-serve --host=0.0.0.0 --port=5000 hulista:app
```

**2. Nginx reverse proxy:**
```nginx
# /etc/nginx/sites-available/flask-app
server {
    listen 80;
    server_name 192.168.1.100;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_valid 200 1h;
    }
}
```

#### ❌ Kötegelt feldolgozás túl lassú

**Tünetek:**
- MikroTik script futtatás >15 perc
- Router nem válaszol feldolgozás alatt

**Optimalizálás:**

```python
# Adaptív köteg méret
def calculate_optimal_batch_size(router_memory_mb):
    if router_memory_mb < 128:
        return 25  # Kis memória
    elif router_memory_mb < 256:
        return 50  # Közepes memória  
    else:
        return 100  # Nagy memória

# Dinamikus delay
def calculate_delay(batch_number, total_batches):
    # Csökkenő delay idővel
    base_delay = 30
    return max(5, base_delay - (batch_number * 2))
```

### 6. Adatforrás Problémák

#### ❌ "Unable to download IP list" hiba

**Tünetek:**
```
Error downloading IP list: HTTP 403 Forbidden
Error downloading IP list: Connection timeout
```

**Diagnosztika:**

```bash
# Manuális letöltés teszt
curl -I https://www.nirsoft.net/countryip/hu.html

# DNS feloldás
nslookup www.nirsoft.net

# Hálózati elérhetőség
ping www.nirsoft.net
```

**Megoldások:**

**1. User-Agent és headers beállítása:**
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

response = requests.get(url, headers=headers, timeout=30)
```

**2. Alternatív adatforrások:**
```python
# Backup adatforrások listája
BACKUP_SOURCES = [
    'https://www.nirsoft.net/countryip/hu.html',
    'https://ipinfo.io/countries/hu',
    'https://raw.githubusercontent.com/herrbischoff/country-ip-blocks/master/ipv4/hu.cidr'
]

def download_with_fallback():
    for source in BACKUP_SOURCES:
        try:
            return download_from_source(source)
        except Exception as e:
            logging.warning(f"Failed to download from {source}: {e}")
    raise Exception("All sources failed")
```

## 🔧 Debug Módok és Eszközök

### 1. Flask Debug Mód

```python
# Development környezetben
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    #                                  ^^^^^^^^^^
    #                                  Részletes hibaüzenetek
```

### 2. Részletes Naplózás

```python
import logging

# Logging konfiguráció
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hulista.log'),
        logging.StreamHandler()
    ]
)

# Használat a kódban
app.logger.debug(f"Processing IP list with {len(hungarian_ips)} entries")
app.logger.info(f"Server started on {request.host}")
app.logger.error(f"Failed to process request: {str(e)}")
```

### 3. Profiling Eszközök

```python
# cProfile használata
import cProfile
import pstats

def profile_endpoint():
    pr = cProfile.Profile()
    pr.enable()
    
    # Endpoint kód futtatása
    result = generate_mikrotik_commands(hungarian_ips)
    
    pr.disable()
    
    # Eredmények mentése
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 leglassabb függvény
    
    return result
```

### 4. Memory Profiling

```python
# memory_profiler használata
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Memória használat figyelése
    large_list = [i for i in range(1000000)]
    return process_list(large_list)

# Futtatás:
# python -m memory_profiler hulista.py
```

## 🧪 Tesztelési Stratégiák

### 1. Unit Tesztek

```python
import unittest
from hulista import app, download_and_convert_ips

class TestHulistaApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_status_endpoint(self):
        response = self.app.get('/status')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('status', data)
    
    def test_mikrotik_script_endpoint(self):
        response = self.app.get('/hu_ip_list.rsc')
        self.assertEqual(response.status_code, 200)
        self.assertIn('MikroTik', response.data.decode())

if __name__ == '__main__':
    unittest.main()
```

### 2. Integration Tesztek

```bash
#!/bin/bash
# integration_test.sh

echo "=== Flask Server Integration Test ==="

# Szerver indítása háttérben
python hulista.py &
SERVER_PID=$!
sleep 5

# Tesztek futtatása
echo "Testing status endpoint..."
curl -f http://localhost:5000/status || exit 1

echo "Testing MikroTik script endpoint..."
curl -f http://localhost:5000/hu_ip_list.rsc -o test_script.rsc || exit 1

echo "Testing file content..."
grep -q "MikroTik" test_script.rsc || exit 1

# Cleanup
kill $SERVER_PID
rm -f test_script.rsc

echo "All tests passed!"
```

### 3. Load Testing

```python
# load_test.py
import requests
import concurrent.futures
import time

def test_endpoint(url):
    start_time = time.time()
    try:
        response = requests.get(url, timeout=30)
        return {
            'status_code': response.status_code,
            'response_time': time.time() - start_time,
            'success': response.status_code == 200
        }
    except Exception as e:
        return {
            'status_code': 0,
            'response_time': time.time() - start_time,
            'success': False,
            'error': str(e)
        }

def load_test(url, concurrent_requests=10, total_requests=100):
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [executor.submit(test_endpoint, url) for _ in range(total_requests)]
        
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    # Eredmények kiértékelése
    success_rate = sum(1 for r in results if r['success']) / len(results) * 100
    avg_response_time = sum(r['response_time'] for r in results) / len(results)
    
    print(f"Success rate: {success_rate:.2f}%")
    print(f"Average response time: {avg_response_time:.2f}s")

# Futtatás
if __name__ == '__main__':
    load_test('http://192.168.1.100:5000/status')
```

## 📋 Hibaellenőrző Checklist

### Szerver Indítás Előtt

- [ ] Python virtual environment aktiválva
- [ ] Összes dependency telepítve (`pip install -r requirements.txt`)
- [ ] Port 5000 szabad
- [ ] Firewall beállítások megfelelőek
- [ ] Hálózati kapcsolat elérhető

### MikroTik Konfiguráció Előtt

- [ ] RouterOS verzió 6.40+ 
- [ ] Script policy jogosultságok beállítva
- [ ] Szerver IP cím elérhető RouterOS-ből
- [ ] HTTP/HTTPS megfelelően konfigurálva
- [ ] Elegendő memória és tárhely

### Deployment Előtt

- [ ] Production WSGI szerver konfigurálva
- [ ] SSL tanúsítványok (ha HTTPS)
- [ ] Monitoring és logging beállítva
- [ ] Backup stratégia kialakítva
- [ ] Dokumentáció frissítve

## 🆘 Sürgősségi Helyreállítás

### Gyors Restart Folyamat

```bash
#!/bin/bash
# emergency_restart.sh

echo "=== Emergency Flask Server Restart ==="

# Régi folyamatok leállítása
pkill -f "python.*hulista" || true
pkill -f "gunicorn.*hulista" || true

# Port felszabadítása
sudo fuser -k 5000/tcp || true

# Virtual environment aktiválása
source venv/bin/activate

# Szerver újraindítása
python hulista.py > /var/log/hulista.log 2>&1 &

echo "Server restarted. Check logs: tail -f /var/log/hulista.log"
```

### Backup Konfiguráció Helyreállítása

```bash
# Konfiguráció backup
cp hulista.py hulista.py.backup.$(date +%Y%m%d_%H%M%S)

# Alapértelmezett konfiguráció visszaállítása
git checkout HEAD -- hulista.py

# Vagy ismert jó verzió
git checkout [commit-hash] -- hulista.py
```

## 📞 További Segítség

### Log Fájlok Helye

**Linux:**
- Application logs: `/var/log/hulista.log`
- System logs: `/var/log/syslog`
- Nginx logs: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`

**Windows:**
- Application logs: `hulista.log` (alkalmazás könyvtárában)
- System logs: Event Viewer → Windows Logs

### Community Support

- **GitHub Issues**: [github.com/your-repo/issues](https://github.com/your-repo/issues)
- **Stack Overflow**: Tag: `mikrotik`, `flask`, `hungarian-ip`
- **MikroTik Forum**: [forum.mikrotik.com](https://forum.mikrotik.com)

### Professional Support

- **Enterprise Support**: enterprise@example.com
- **Consulting Services**: consulting@example.com
- **Training**: training@example.com

---

**Hibaelhárítás kész! Következő: [GYIK](FAQ)** 🚀
