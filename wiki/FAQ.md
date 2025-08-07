# Gyakran Ismételt Kérdések (GYIK)

> **Válaszok a Magyar IP Lista Server leggyakoribb kérdéseire**

## 🤔 Általános Kérdések

### Mi az a Magyar IP Lista Server?

A Magyar IP Lista Server egy Flask-alapú webalkalmazás, amely automatikusan letölti és konvertálja a magyar IP címtartományokat MikroTik RouterOS-kompatibilis formátumba. A szerver REST API-t biztosít a különböző formátumokban történő hozzáféréshez.

### Miért van szükség kötegelt feldolgozásra?

A magyar IP lista ~903 hálózati tartományt tartalmaz. Ha egyszerre töltjük be őket a MikroTik routerbe, az túlterhelheti a router memóriáját és CPU-ját. A kötegelt feldolgozás 50 IP címenként dolgozik fel, 30 másodperces szünetekkel, így védi a router stabilitását.

### Milyen gyakran frissül a magyar IP lista?

A forrás (nirsoft.net) általában hetente frissíti a nemzeti IP listákat. Ajánlott a MikroTik scriptet naponta futtatni (pl. éjjel 3:00-kor), hogy mindig aktuális legyen a lista.

## 🔧 Telepítési Kérdések

### **K: Milyen rendszerkövetelményeim vannak a Flask szerver futtatásához?**

**V:** Minimális követelmények:
- **CPU**: 1 core (2+ ajánlott)
- **RAM**: 512 MB (1 GB+ ajánlott)
- **Tárhely**: 100 MB
- **Hálózat**: Stabil internet kapcsolat
- **OS**: Windows 10+, Ubuntu 18.04+, CentOS 7+, macOS 10.14+

### **K: Futtathatom Docker containerben?**

**V:** Igen, itt egy egyszerű Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY hulista.py .
EXPOSE 5000

CMD ["python", "hulista.py"]
```

Futtatás:
```bash
docker build -t hulista .
docker run -p 5000:5000 hulista
```

### **K: Használhatom Raspberry Pi-on?**

**V:** Igen! A Flask szerver kiválóan fut Raspberry Pi 3B+ vagy újabb modelleken:

```bash
# Raspberry Pi optimalizált telepítés
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv -y

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Automatikus indítás systemd-vel
sudo systemctl enable hulista.service
```

## 🌐 Hálózati Kérdések

### **K: Hozzáférhetek a szerverhez interneten keresztül?**

**V:** Igen, de fokozott biztonsági intézkedésekkel:

1. **HTTPS használat**:
```python
# SSL tanúsítványokkal
app.run(host='0.0.0.0', port=5000, 
        ssl_context=('cert.pem', 'key.pem'))
```

2. **Reverse proxy (Nginx)**:
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
    }
}
```

3. **Firewall és rate limiting**
4. **VPN hozzáférés ajánlott**

### **K: Működik IPv6 környezetben?**

**V:** Jelenleg csak IPv4 tartományokat szolgál ki a szerver, mert a forrás adatbázis csak IPv4 címeket tartalmaz. Az alkalmazás azonban IPv6 hálózatokon is fut:

```python
# IPv6 és IPv4 dual-stack
app.run(host='::', port=5000)  # IPv6 összes interfész
```

### **K: Milyen portot használjak production környezetben?**

**V:** Ajánlott beállítások:
- **Development**: 5000 (Flask default)
- **Production HTTP**: 80 (reverse proxy mögött)
- **Production HTTPS**: 443 (reverse proxy mögött)
- **Belső hálózat**: 8080, 8000, vagy egyedi port

## 🔒 MikroTik Specifikus Kérdések

### **K: Milyen RouterOS verzió szükséges?**

**V:** Minimális követelmények:
- **RouterOS 6.40+** (alapvető támogatás)
- **RouterOS 6.48+** (ajánlott stability)
- **RouterOS 7.x** (legjobb teljesítmény)

### **K: Mennyi memóriát használ a router a teljes lista betöltése után?**

**V:** Becsült memóriahasználat:
- **903 address list entry**: ~180-200 KB RAM
- **CPU load**: 2-5% (~10 percig a betöltés alatt)
- **Flash írás**: ~50 KB (ha config mentés történik)

CCR és hEX routerek könnyen kezelik, RB750 szintű eszközöknél figyelni kell a memóriát.

### **K: Automatikusan mentésre kerül a konfiguráció?**

**V:** Alapértelmezetten nem. Ha szeretnéd, hogy automatikusan mentse:

```routeros
# Script végéhez hozzáadás
:log info "Konfiguráció automatikus mentése..."
/system backup save name=("backup-" . [/system clock get date])
/export file=("config-" . [/system clock get date])
:log info "Mentés befejezve"
```

### **K: Mi történik, ha a script futás közben megszakad?**

**V:** A script hibatűrő:
- Részleges betöltés esetén a már betöltött IP címek megmaradnak
- Következő futásnál teljes újraszinkronizálás történik
- Log-ban részletes információ a hiba okáról

Manuális helyreállítás:
```routeros
# Részleges lista törlése
/ip firewall address-list remove [find list=HU_IP]

# Script újrafuttatása
/system script run HU_IP_Update
```

## 📊 Teljesítmény Kérdések

### **K: Hány egyidejű kapcsolatot bír el a szerver?**

**V:** Teljesítmény táblázat:

| Szerver Típus | Egyidejű Kérések | Válaszidő |
|---------------|------------------|-----------|
| Raspberry Pi 4 | 10-15 | <2s |
| VPS (2 core, 2GB) | 50-100 | <1s |
| Dedicated Server | 200+ | <0.5s |

Production környezetben használj WSGI szervert:
```bash
# Gunicorn 4 worker-rel
gunicorn --workers 4 --bind 0.0.0.0:5000 hulista:app

# Nginx load balancing
upstream flask_app {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}
```

### **K: Mennyi sávszélességet használ a lista letöltése?**

**V:** Adatforgalom breakdown:
- **Forrás letöltés**: ~50 KB (nirsoft.net)
- **MikroTik script**: ~45 KB (generált .rsc fájl)
- **JSON API**: ~85 KB (metadata-val)
- **Napi forgalom/router**: <500 KB

Havi sávszélesség 30 routerrel: ~15 MB.

### **K: Optimalizálhatom a kötegelt feldolgozást?**

**V:** Igen, az alábbi paraméterekkel:

```routeros
# Gyors routerek (CCR, hEX S)
:local BATCH_SIZE 100
:local DELAY_SECONDS 15

# Közepes routerek (hEX, RB750Gr3)  
:local BATCH_SIZE 50
:local DELAY_SECONDS 30

# Lassú routerek (RB750, régi eszközök)
:local BATCH_SIZE 25  
:local DELAY_SECONDS 45
```

## 🔐 Biztonsági Kérdések

### **K: Biztonságos-e a Flask szerver alapértelmezett beállításokkal?**

**V:** Belső hálózaton igen, de production-ben further hardening szükséges:

**Alapvető biztonság**:
```python
# Debug mód kikapcsolása
app.run(debug=False)

# Csak meghatározott IP-kről hozzáférés
ALLOWED_IPS = ['192.168.1.0/24']

@app.before_request  
def limit_remote_addr():
    if request.remote_addr not in ALLOWED_IPS:
        abort(403)
```

**Haladó biztonság**:
- SSL/TLS titkosítás
- Rate limiting
- Authentication (ha publikus)
- Firewall rules
- Regular updates

### **K: Naplózza a szerver a hozzáféréseket?**

**V:** Alapértelmezetten minimális logging van. Részletes naplózáshoz:

```python
import logging
from datetime import datetime

# Hozzáférési log
@app.after_request
def log_request(response):
    app.logger.info(f"{datetime.now()} - {request.remote_addr} - "
                   f"{request.method} {request.path} - {response.status_code}")
    return response

# Log fájl konfiguráció
logging.basicConfig(
    filename='access.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
```

### **K: Mit tegyek, ha feltörték a szerveremet?**

**V:** Azonnali lépések:
1. **Szerver leállítása**: `sudo systemctl stop hulista`
2. **Hálózat izolálása**: Firewall rules
3. **Log elemzés**: `/var/log/hulista.log`, `/var/log/nginx/access.log`
4. **Backup helyreállítás**: Tiszta verzió telepítése
5. **Security audit**: Dependency update, patch management

## 🔄 Maintenance és Updates

### **K: Hogyan frissítsem a szerver szoftvert?**

**V:** Update folyamat:

```bash
# 1. Backup készítése
cp hulista.py hulista.py.backup.$(date +%Y%m%d)

# 2. Git pull (ha használod)
git pull origin main

# 3. Dependencies frissítése
pip install -r requirements.txt --upgrade

# 4. Konfiguráció validálása
python hulista.py --test

# 5. Graceful restart
sudo systemctl restart hulista
```

### **K: Mi a teendő, ha változik a forrás adatbázis formátuma?**

**V:** A nirsoft.net ritkán változtatja a formátumot, de ha igen:

1. **Monitoring beállítása**: Napi automatikus ellenőrzés
2. **Fallback források**: Több backup URL
3. **Parser rugalmasság**: Regex helyett BeautifulSoup
4. **Alert rendszer**: Email küldés hiba esetén

```python
# Robosztus parser
def parse_ip_list_robust(html_content):
    parsers = [
        parse_nirsoft_format,
        parse_alternative_format,
        parse_generic_format
    ]
    
    for parser in parsers:
        try:
            return parser(html_content)
        except Exception as e:
            logging.warning(f"Parser {parser.__name__} failed: {e}")
    
    raise Exception("All parsers failed")
```

## 🌍 Nemzetközi Használat

### **K: Használhatom más országok IP listáihoz?**

**V:** Igen! Módosítsd a forrás URL-t:

```python
# Országkódok a nirsoft.net-en
COUNTRY_SOURCES = {
    'HU': 'https://www.nirsoft.net/countryip/hu.html',  # Magyarország
    'AT': 'https://www.nirsoft.net/countryip/at.html',  # Ausztria  
    'SK': 'https://www.nirsoft.net/countryip/sk.html',  # Szlovákia
    'RO': 'https://www.nirsoft.net/countryip/ro.html',  # Románia
    'DE': 'https://www.nirsoft.net/countryip/de.html',  # Németország
}

# Dinamikus endpoint
@app.route('/<country_code>_ip_list.rsc')
def country_mikrotik_script(country_code):
    if country_code.upper() not in COUNTRY_SOURCES:
        abort(404)
    # ... ország-specifikus feldolgozás
```

### **K: Támogatja a szerver a időzónákat?**

**V:** Alapértelmezetten a szerver helyi időt használ. Többzónás támogatáshoz:

```python
import pytz
from datetime import datetime

# UTC időbélyegek
def get_utc_timestamp():
    return datetime.now(pytz.UTC)

# Magyar időzóna
def get_hungarian_timestamp():
    hungarian_tz = pytz.timezone('Europe/Budapest')
    return datetime.now(hungarian_tz)

# API response-ban
{
    "generated_at_utc": "2024-12-19T14:30:45.000Z",
    "generated_at_local": "2024-12-19T15:30:45.000+01:00"
}
```

## 📈 Skalázás és Production

### **K: Hogyan skálázom nagyobb környezetre?**

**V:** Multi-tier architektúra:

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000-5003:5000"
    deploy:
      replicas: 4
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - web
    
  redis:
    image: redis:alpine
    
  monitoring:
    image: prom/prometheus
```

**Load balancing**:
- Nginx upstream
- HAProxy
- AWS ALB/ELB
- Cloudflare

### **K: Kubernetes deployment lehetséges?**

**V:** Igen, példa konfiguráció:

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hulista-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hulista
  template:
    metadata:
      labels:
        app: hulista
    spec:
      containers:
      - name: hulista
        image: hulista:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
---
apiVersion: v1
kind: Service
metadata:
  name: hulista-service
spec:
  selector:
    app: hulista
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

## 🎯 Üzleti Használat

### **K: Használhatom kereskedelmi célra?**

**V:** A szoftver MIT licenc alatt áll, ami kereskedelmi használatot is engedélyez. A forrás adatok (nirsoft.net) free-to-use, de check their terms. Saját felelősségre használd production környezetben.

### **K: Van SLA vagy support?**

**V:** A community verzió "as-is" alapon elérhető. Enterprise támogatásért lépj kapcsolatba:
- **Professional Support**: enterprise@example.com
- **Custom Development**: development@example.com  
- **Training és Consulting**: training@example.com

### **K: GDPR compliance?**

**V:** A szerver által gyűjtött adatok:
- **IP címek**: Publikus IP tartományok (nem személyes adatok)
- **Access logs**: IP címek, timestamp (configurable retention)
- **No cookies**: Alapértelmezetten nem használ cookie-kat

GDPR-friendly konfiguráció:
```python
# No logging of client IPs
@app.after_request
def no_ip_logging(response):
    # Anonymize or skip IP logging
    return response

# Data retention policy
def cleanup_old_logs():
    # Auto-delete logs older than 30 days
    pass
```

## 🚀 Jövőbeli Fejlesztések

### **K: Mik a tervezett új funkciók?**

**V:** Roadmap 2024-2025:
- **IPv6 támogatás** (ha elérhetővé válik forrás)
- **Multi-country support** (dinamikus ország választás)
- **Web UI** (grafikus admin felület)
- **Webhook integration** (Discord, Slack notifications)
- **Database backend** (PostgreSQL, MySQL támogatás)
- **API v2** (GraphQL endpoint)

### **K: Hogyan járulhatok hozzá a fejlesztéshez?**

**V:** Közreműködési lehetőségek:
1. **GitHub Issues**: Bug jelentések, feature requests
2. **Pull Requests**: Kód hozzájárulások
3. **Documentation**: Wiki frissítések, fordítások
4. **Testing**: Beta verziók tesztelése
5. **Community Support**: Fórumokon segítségnyújtás

```bash
# Development environment setup
git clone https://github.com/your-repo/hulista
cd hulista
python -m venv dev-env
source dev-env/bin/activate
pip install -r requirements-dev.txt
pre-commit install
```

---

## 🔍 Nem találod a választ?

### További Segítség
- **📧 Email**: support@example.com
- **💬 Discord**: [discord.gg/hulista](https://discord.gg/hulista)
- **📱 Telegram**: [@hulista_support](https://t.me/hulista_support)
- **🐛 GitHub Issues**: [github.com/your-repo/issues](https://github.com/your-repo/issues)

### Dokumentáció Linkek
- **[Kezdő Útmutató](Installation-Guide)** - Telepítési lépések
- **[API Dokumentáció](API-Documentation)** - Teljes API referencia
- **[Hibaelhárítás](Troubleshooting)** - Problémamegoldás
- **[Fejlesztői Útmutató](Development-Guide)** - Kód hozzájárulás

---

**GYIK kész! Vissza a [Főoldalra](Home)** 🏠
