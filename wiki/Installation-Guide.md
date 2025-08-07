# Telepítési Útmutató

> **Lépésről lépésre útmutató a Magyar IP Lista Server telepítéséhez minden platformon**

## 📋 Előfeltételek

### Rendszerkövetelmények
- **Python**: 3.6 vagy újabb (ajánlott: 3.8+)
- **Memória**: Minimum 2 GB RAM
- **Tárhely**: Minimum 100 MB szabad hely
- **Hálózat**: Internet kapcsolat az IP lista letöltéséhez

### Ellenőrzés
```bash
# Python verzió ellenőrzése
python --version
# vagy
python3 --version
```

## 🪟 Windows Telepítés

### 1. Python Telepítése
Ha még nincs Python telepítve:
1. Letöltés: [python.org](https://www.python.org/downloads/)
2. Telepítés során: ✅ **"Add Python to PATH"**
3. Ellenőrzés: `python --version`

### 2. Projekt Letöltése
```cmd
# Git-tel (ajánlott)
git clone https://github.com/kovtom/magyar-ip-lista-server.git
cd magyar-ip-lista-server

# Vagy ZIP letöltés után kicsomagolás
```

### 3. Virtuális Környezet (Ajánlott)
```cmd
# Virtuális környezet létrehozása
python -m venv venv

# Aktiválás
venv\Scripts\activate.bat

# Deaktiválás (később)
deactivate
```

### 4. Függőségek Telepítése
```cmd
# Virtuális környezetben
pip install -r requirements.txt

# Vagy egyenként
pip install flask requests schedule gunicorn waitress
```

### 5. Tűzfal Konfiguráció
```cmd
# Rendszergazdaként futtatva
netsh advfirewall firewall add rule name="Magyar IP Lista Szerver" dir=in action=allow protocol=TCP localport=5000
```

### 6. Szerver Indítása

**Fejlesztői mód:**
```cmd
python hulista.py
```

**Produkciós mód (ajánlott):**
```cmd
# Dupla kattintás vagy parancssorból
start_waitress.bat
```

## 🐧 Linux Telepítés

### 1. Python és Git Telepítése

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

**CentOS/RHEL:**
```bash
sudo yum install python3 python3-pip git
# vagy újabb verziókban
sudo dnf install python3 python3-pip git
```

### 2. Projekt Letöltése
```bash
git clone https://github.com/kovtom/magyar-ip-lista-server.git
cd magyar-ip-lista-server
```

### 3. Virtuális Környezet
```bash
# Virtuális környezet létrehozása
python3 -m venv venv

# Aktiválás
source venv/bin/activate

# Deaktiválás (később)
deactivate
```

### 4. Függőségek Telepítése
```bash
pip install -r requirements.txt
```

### 5. Tűzfal Konfiguráció

**UFW (Ubuntu):**
```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

**firewalld (CentOS/RHEL):**
```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### 6. Szerver Indítása

**Fejlesztői mód:**
```bash
python3 hulista.py
```

**Produkciós mód:**
```bash
chmod +x start_gunicorn.sh
./start_gunicorn.sh
```

### 7. Systemd Szolgáltatás (Opcionális)

**Service fájl létrehozása:**
```bash
sudo nano /etc/systemd/system/hulista.service
```

**Tartalom:**
```ini
[Unit]
Description=Magyar IP Lista Flask Szerver (Gunicorn)
After=network.target
Wants=network.target

[Service]
Type=simple
User=hulista
Group=hulista
WorkingDirectory=/opt/hulista
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/hulista/start_gunicorn.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Aktiválás:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable hulista.service
sudo systemctl start hulista.service

# Státusz ellenőrzése
sudo systemctl status hulista.service
```

## 🍎 macOS Telepítés

### 1. Homebrew Telepítése (ha még nincs)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Python és Git Telepítése
```bash
brew install python3 git
```

### 3. Projekt Letöltése
```bash
git clone https://github.com/kovtom/magyar-ip-lista-server.git
cd magyar-ip-lista-server
```

### 4. Virtuális Környezet és Függőségek
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Szerver Indítása
```bash
# Fejlesztői mód
python3 hulista.py

# Produkciós mód
chmod +x start_gunicorn.sh
./start_gunicorn.sh
```

## ✅ Telepítés Ellenőrzése

### 1. Szerver Elérhetősége
Böngészőben nyisd meg: `http://localhost:5000`

### 2. API Teszt
```bash
curl http://localhost:5000/status
```

### 3. IP Lista Letöltés
```bash
curl http://localhost:5000/hu_ip_list.rsc -o test_ip_list.rsc
```

## 🔧 Gyakori Telepítési Problémák

### Python Nem Található
**Windows:**
- Python PATH ellenőrzése
- `py` parancs használata `python` helyett

**Linux:**
- `python3` használata `python` helyett
- `sudo apt install python-is-python3` (Ubuntu)

### Port Foglaltság
```bash
# Port ellenőrzése
netstat -an | grep :5000

# Másik port használata a kódban vagy környezeti változóval
export PORT=5001
```

### Függőség Telepítési Hibák
```bash
# Pip frissítése
pip install --upgrade pip

# Wheel telepítése
pip install wheel

# Rendszer csomagok (Linux)
sudo apt install python3-dev build-essential
```

### Hálózati Hozzáférési Problémák
1. **Tűzfal szabályok ellenőrzése**
2. **Router port forwarding**
3. **Antivirus szoftver beállítások**
4. **VPN kapcsolat megszakítása**

## 📚 Következő Lépések

Sikeres telepítés után:

1. **[MikroTik Konfiguráció](MikroTik-Configuration)** beállítása
2. **[Hálózati Beállítások](Network-Configuration)** konfigurálása
3. **[Produkciós Telepítés](Production-Deployment)** végrehajtása
4. **[Biztonsági Beállítások](Security-Configuration)** alkalmazása

## 🆘 Segítségkérés

Ha problémába ütközöl:
1. Ellenőrizd a **[Hibaelhárítás](Troubleshooting)** oldalt
2. Nézd meg a **[FAQ](FAQ)** részt
3. Nyiss [GitHub Issue-t](https://github.com/kovtom/magyar-ip-lista-server/issues)

---

**Sikeres telepítést! Következő: [MikroTik Konfiguráció](MikroTik-Configuration)** 🚀
