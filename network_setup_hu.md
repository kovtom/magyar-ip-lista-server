# Hálózati Elérhetőség Beállítása

## Windows Tűzfalbeállítások

### 1. Windows Defender Firewall beállítása

#### Parancssori módszer (rendszergazdaként):
```cmd
# Bejáratkozási szabály hozzáadása
netsh advfirewall firewall add rule name="Magyar IP Lista Szerver" dir=in action=allow protocol=TCP localport=5000

# Kijaró szabály hozzáadása (opcionális)
netsh advfirewall firewall add rule name="Magyar IP Lista Szerver OUT" dir=out action=allow protocol=TCP localport=5000
```

#### Grafikus módszer:
1. Nyissa meg a **Windows Defender Firewall with Advanced Security**-t
2. Kattintson az **Inbound Rules** (Bejáratkozási szabályok) gombra
3. Kattintson a **New Rule...** (Új szabály) gombra
4. Válassza a **Port** opciót -> **Next**
5. Válassza a **TCP** -> **Specific Local Ports** -> írja be: `5000`
6. Válassza az **Allow the connection** -> **Next**
7. Jelöljék ki az összes hálózati profilt (Domain, Private, Public)
8. Adjon nevet a szabálynak: "Magyar IP Lista Szerver"

### 2. PowerShell parancssori módszer:
```powershell
# Bejáratkozási szabály
New-NetFirewallRule -DisplayName "Magyar IP Lista Szerver" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow

# Lista megjelenítése
Get-NetFirewallRule -DisplayName "Magyar IP Lista Szerver"
```

## Router Beállítások (ha szükséges)

### Port Forwarding beállítása:

Ha a szervert a helyi hálózaton kívülről is el szeretné érni:

1. Jelentkezzen be a router admin felületére (általában 192.168.1.1 vagy 192.168.0.1)
2. Keresse meg a **Port Forwarding** vagy **Virtual Server** menüt
3. Adjon hozzá egy új szabályt:
   - **Service Name**: Magyar IP Lista
   - **External Port**: 5000
   - **Internal Port**: 5000
   - **Internal IP**: [a szerver gép IP címe]
   - **Protocol**: TCP

### Dinamikus DNS (opcionális):

Ha nincs statikus IP címe, használhat dinamikus DNS szolgáltatást:
- No-IP (https://www.noip.com)
- DuckDNS (https://www.duckdns.org)
- DynDNS (https://dyn.com)

## Biztonsági Megjegyzések

⚠️ **FIGYELEM**: Ha a szervert publikusan elérhetővé teszi:

1. **Erős jelszavakat használjon** minden hálózati eszközre
2. **Frissítse rendszeresen** az operációs rendszert
3. **Monitorozza a hálózati forgalmat**
4. **Használjon VPN-t** ha lehetséges
5. **Korlátozza a hozzáférést** csak a szükséges IP címekre

## Tesztelés

### Helyi hálózaton:
```bash
# Windows-ból
curl http://192.168.1.100:5000/status

# Vagy böngészőbe:
http://192.168.1.100:5000/
```

### MikroTik RouterOS-ból:
```
/tool fetch url=http://192.168.1.100:5000/hu_ip_list.txt
```

## Hibaelhárítás

### A szerver nem elérhető távolról:

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

### Általános hibák:

- **Port foglaltság**: Változtassa meg a portot 5001-re vagy 8080-ra
- **IP cím változás**: Használjon statikus IP-t vagy dinamikus DNS-t
- **Szolgáltató blokkolása**: Egyes internetszolgáltatók blokkolnak bizonyos portokat

## Hasznos parancsok

### Aktív hálózati kapcsolatok listázása:
```cmd
netstat -an | findstr :5000
```

### Hálózati interfészek listázása:
```cmd
ipconfig /all
```

### Elérhetőségtesztelés:
```cmd
# Helyi tesztelés
curl http://localhost:5000/status

# Távolsági tesztelés
curl http://[szerver-ip]:5000/status
```

## Linux Service Konfiguráció

### Telepítés systemd szolgáltatásként:

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

### Linux Tűzfal Konfiguráció:

#### UFW (Ubuntu):
```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

#### firewalld (CentOS/RHEL):
```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

#### iptables:
```bash
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

### Szolgáltatáskezelő Parancsok:

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
