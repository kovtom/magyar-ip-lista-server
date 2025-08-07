# Magyar IP Lista Flask Szerver

> **Nyelv:** 🇭🇺 Magyar | [🇬🇧 English](README.md)

Egy Flask alapú webszerver, amely automatikusan frissíti a magyar IP blokk listát és szolgáltatja azt MikroTik routereknek RouterOS parancsok formájában.

## Követelmények

- Python 3.6+
- flask könyvtár
- requests könyvtár
- schedule könyvtár

**Támogatott Operációs Rendszerek:**
- Windows (részletes tűzfal beállításokkal)
- Linux (systemd szolgáltatás integrációval)
- Bármely OS Python 3.6+ támogatással

## Telepítés

1. Klónozza vagy töltse le a projektet:
   ```bash
   git clone https://github.com/[felhasznalo]/hulista.git
   cd hulista
   ```

2. Telepítse a szükséges függőségeket:
   ```bash
   pip install -r requirements.txt
   ```

   Vagy egyenként:
   ```bash
   pip install flask requests schedule
   ```

## Használat

### Szerver indítása:
```
python hulista.py
```

A szerver automatikusan:
1. Indításkor letölti és frissíti az IP listát
2. Elindít egy Flask webszervert a 5000-es porton
3. Ütemezi a napi frissítéseket (minden nap 2:00-kor)

### Elérhető URL-ek:

- **http://localhost:5000/** - Főoldal, státusz információkkal
- **http://localhost:5000/hu_ip_list.txt** - MikroTik parancsok letöltése
- **http://localhost:5000/status** - JSON státusz információk

## MikroTik Konfiguráció

### 1. Script telepítése:

1. Nyissa meg a MikroTik RouterOS WebFig vagy WinBox felületet
2. Navigáljon a **System > Scripts** menübe
3. Hozzon létre új scriptet **"HU_IP_Update"** néven
4. Másolja be a `mikrotik_update_script.rsc` fájl tartalmát
5. **Módosítsa a SERVER_URL változót** a saját szerver IP címére:
   ```
   :local SERVER_URL "http://192.168.1.100:5000/hu_ip_list.txt"
   ```

### 2. Ütemezett futtatás beállítása:

1. Navigáljon a **System > Scheduler** menübe
2. Hozzon létre új feladatot:
   - **Name:** HU_IP_Daily_Update
   - **Start Date:** ma
   - **Start Time:** 03:00:00
   - **Interval:** 1d 00:00:00
   - **On Event:** HU_IP_Update

### 3. Első futtatás (teszt):

A scriptet manuálisan is futtathatja a **System > Scripts** menüben a **Run Script** gombbal.

## Funkciók

### Flask Szerver:
- **Automatikus frissítés**: Naponta 2:00-kor frissíti az IP listát
- **Webinterface**: Böngészőből ellenőrizhető a státusz
- **JSON API**: Programozott eléréshez
- **Fix fájlnév**: Mindig `hu_ip_list.txt` (nem kell változtatni a MikroTik-ben)

### MikroTik Script:
- **Automatikus letöltés**: HTTP GET kérésekkel
- **Lista frissítés**: Törli a régi, betölti az új listát
- **Hibakezelés**: Részletes naplózás és hibaellenőrzés
- **Statisztikák**: Beszámol a feldolgozott elemek számáról

## Biztonsági előnyök

✅ **Nincs szükség jelszavakra**: A MikroTik HTTP-n húzza le a frissítést  
✅ **Automatikus**: Nincs manuális beavatkozás szükséges  
✅ **Központosított**: Egy szerver szolgálja ki az összes routert  
✅ **Naplózott**: Minden művelet naplózva van  

## Kimeneti fájlok

- **hu_ip_list.txt** - MikroTik parancsok (fix név, állandóan frissül)

## Példa kimenet

```
/ip firewall address-list add list=HU_IP address=2.58.168.0/22
/ip firewall address-list add list=HU_IP address=2.59.196.0/22
/ip firewall address-list add list=HU_IP address=5.28.0.0/21
...
```

## Hálózati Konfiguráció

### Windows Tűzfalbeállítások

#### 1. Windows Defender Firewall beállítása

**Parancssori módszer (rendszergazdaként):**
```cmd
# Bejáratkozási szabály hozzáadása
netsh advfirewall firewall add rule name="Magyar IP Lista Szerver" dir=in action=allow protocol=TCP localport=5000

# Kijaró szabály hozzáadása (opcionális)
netsh advfirewall firewall add rule name="Magyar IP Lista Szerver OUT" dir=out action=allow protocol=TCP localport=5000
```

**Grafikus módszer:**
1. Nyissa meg a **Windows Defender Firewall with Advanced Security**-t
2. Kattintson az **Inbound Rules** (Bejáratkozási szabályok) gombra
3. Kattintson a **New Rule...** (Új szabály) gombra
4. Válassza a **Port** opciót -> **Next**
5. Válassza a **TCP** -> **Specific Local Ports** -> írja be: `5000`
6. Válassza az **Allow the connection** -> **Next**
7. Jelöljék ki az összes hálózati profilt (Domain, Private, Public)
8. Adjon nevet a szabálynak: "Magyar IP Lista Szerver"

#### 2. PowerShell parancssori módszer:
```powershell
# Bejáratkozási szabály
New-NetFirewallRule -DisplayName "Magyar IP Lista Szerver" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow

# Lista megjelenítése
Get-NetFirewallRule -DisplayName "Magyar IP Lista Szerver"
```

### Router Beállítások (ha szükséges)

#### Port Forwarding beállítása:

Ha a szervert a helyi hálózaton kívülről is el szeretné érni:

1. Jelentkezzen be a router admin felületére (általában 192.168.1.1 vagy 192.168.0.1)
2. Keresse meg a **Port Forwarding** vagy **Virtual Server** menüt
3. Adjon hozzá egy új szabályt:
   - **Service Name**: Magyar IP Lista
   - **External Port**: 5000
   - **Internal Port**: 5000
   - **Internal IP**: [a szerver gép IP címe]
   - **Protocol**: TCP

#### Dinamikus DNS (opcionális):

Ha nincs statikus IP címe, használhat dinamikus DNS szolgáltatást:
- No-IP (https://www.noip.com)
- DuckDNS (https://www.duckdns.org)
- DynDNS (https://dyn.com)

### Linux Service Konfiguráció

#### Telepítés systemd szolgáltatásként:

1. **Service fájl létrehozása**:
   ```bash
   sudo nano /etc/systemd/system/hulista.service
   ```

2. **Service fájl tartalma**:
   ```ini
   [Unit]
   Description=Magyar IP Lista Flask Szerver
   After=network.target
   Wants=network.target

   [Service]
   Type=simple
   User=hulista
   Group=hulista
   WorkingDirectory=/opt/hulista
   ExecStart=/usr/bin/python3 /opt/hulista/hulista.py
   Restart=always
   RestartSec=10
   Environment=PYTHONUNBUFFERED=1

   [Install]
   WantedBy=multi-user.target
   ```

3. **Felhasználó és könyvtár létrehozása**:
   ```bash
   sudo useradd -r -s /bin/false hulista
   sudo mkdir -p /opt/hulista
   sudo cp -r * /opt/hulista/
   sudo chown -R hulista:hulista /opt/hulista
   ```

4. **Python függőségek telepítése**:
   ```bash
   cd /opt/hulista
   sudo pip3 install -r requirements.txt
   ```

5. **Szolgáltatás engedélyezése és indítása**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable hulista.service
   sudo systemctl start hulista.service
   ```

6. **Szolgáltatás állapotának ellenőrzése**:
   ```bash
   sudo systemctl status hulista.service
   sudo journalctl -u hulista.service -f
   ```

#### Linux Tűzfal Konfiguráció:

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

**iptables:**
```bash
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

#### Szolgáltatáskezelő Parancsok:

```bash
# Szolgáltatás indítása
sudo systemctl start hulista.service

# Szolgáltatás leállítása
sudo systemctl stop hulista.service

# Szolgáltatás újraindítása
sudo systemctl restart hulista.service

# Naplók megtekintése
sudo journalctl -u hulista.service

# Valós idejű naplók
sudo journalctl -u hulista.service -f

# Szolgáltatás állapotának ellenőrzése
sudo systemctl is-active hulista.service
```

### Biztonsági Megjegyzések

⚠️ **FIGYELEM**: Ha a szervert publikusan elérhetővé teszi:

1. **Erős jelszavakat használjon** minden hálózati eszközre
2. **Frissítse rendszeresen** az operációs rendszert
3. **Monitorozza a hálózati forgalmat**
4. **Használjon VPN-t** ha lehetséges
5. **Korlátozza a hozzáférést** csak a szükséges IP címekre

### Hálózati Konfiguráció Tesztelése

#### Helyi hálózaton:
```bash
# Windows-ból
curl http://192.168.1.100:5000/status

# Vagy böngészőbe:
http://192.168.1.100:5000/
```

#### MikroTik RouterOS-ból:
```
/tool fetch url=http://192.168.1.100:5000/hu_ip_list.txt
```

#### Hasznos parancsok:

**Windows:**
```cmd
# Aktív hálózati kapcsolatok listázása
netstat -an | findstr :5000

# Hálózati interfészek listázása
ipconfig /all

# Helyi tesztelés
curl http://localhost:5000/status

# Távolsági tesztelés
curl http://[szerver-ip]:5000/status
```

**Linux:**
```bash
# Aktív hálózati kapcsolatok listázása
netstat -an | grep :5000

# Hálózati interfészek listázása
ip addr show

# Helyi tesztelés
curl http://localhost:5000/status

# Távolsági tesztelés
curl http://[szerver-ip]:5000/status
```

## Troubleshooting

### Szerver nem indul el:
- Ellenőrizze, hogy a 5000-es port szabad-e
- Telepítse a hiányzó könyvtárakat

### MikroTik nem tölti le:
- Ellenőrizze a hálózati kapcsolatot
- Győződjön meg róla, hogy a SERVER_URL helyes
- Nézze meg a MikroTik log fájlokat

### Lista nem frissül:
- Ellenőrizze a szerver log kimenetét
- Győződjön meg róla, hogy a forrás URL elérhető

### Hálózati Elérési Problémák:

#### A szerver nem elérhető távolról:

1. **Ellenőrizze a Windows tűzfalat**:
   ```cmd
   netsh advfirewall firewall show rule name="Magyar IP Lista Szerver"
   ```

2. **Tesztelje a portot helyileg**:
   ```cmd
   telnet localhost 5000
   ```

3. **Ellenőrizze a hálózati kapcsolatot**:
   ```cmd
   ping 192.168.1.100
   ```

4. **Ellenőrizze a router beállításokat**

#### Általános hálózati hibák:

- **Port foglaltság**: Változtassa meg a portot 5001-re vagy 8080-ra
- **IP cím változás**: Használjon statikus IP-t vagy dinamikus DNS-t
- **Szolgáltató blokkolása**: Egyes internetszolgáltatók blokkolnak bizonyos portokat

## Fájlok a projektben

- **hulista.py** - Flask szerver főprogramja
- **mikrotik_update_script.rsc** - MikroTik RouterOS script
- **hu_ip_list.txt** - Generált MikroTik parancsok (automatikusan frissül)
- **README.md** - Angol dokumentáció (átfogó)
- **README_hu.md** - Ez a magyar dokumentáció (átfogó)
- **network_setup.md** - Hálózati konfiguráció útmutató (angol) *[elavult - tartalom beolvasztva README.md-be]*
- **network_setup_hu.md** - Hálózati konfiguráció útmutató (magyar) *[elavult - tartalom beolvasztva README_hu.md-be]*

## Nyelvi Támogatás

Ez a dokumentáció több nyelven érhető el:

- 🇭🇺 **Magyar**: [README_hu.md](README_hu.md) *(jelenlegi)*
- 🇬🇧 **English**: [README.md](README.md)

Hálózati konfigurációs útmutatók:
- 🇭🇺 **Magyar**: Tartalom integrálva a README_hu.md-be
- 🇬🇧 **English**: Tartalom integrálva a README.md-be

## Licenc

MIT Licenc - részletekért lásd a [LICENSE](LICENSE) fájlt.

## Közreműködés

1. Fork-old a projektet
2. Hozd létre a feature branch-edet (`git checkout -b feature/ValamilyenUjFunkció`)
3. Commit-old a változásaidat (`git commit -m 'Valamilyen új funkció hozzáadása'`)
4. Push-old a branch-re (`git push origin feature/ValamilyenUjFunkció`)
5. Nyiss egy Pull Request-et
