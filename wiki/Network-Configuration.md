# Hálózati Konfiguráció

> **Optimális hálózati beállítások a Magyar IP Lista Server működéséhez**

## 🌐 Áttekintés

Ez az útmutató segít beállítani a tökéletes hálózati környezetet a Flask szerver és MikroTik router közötti kommunikációhoz.

## 📊 Hálózati Architektúra

### Ajánlott Topológia

```
Internet
    │
    │
┌───▼────┐         ┌─────────────┐
│MikroTik│◄────────┤Flask Server │
│Router  │  HTTP   │192.168.1.100│
└───┬────┘  :5000  └─────────────┘
    │
    │
┌───▼────┐
│ LAN    │
│Devices │
└────────┘
```

### Hálózati Szegmensek

**DMZ Zone (Ajánlott):**
```
Flask Server: 192.168.100.10/24
Router DMZ:   192.168.100.1/24
```

**LAN Zone (Egyszerű):**
```
Flask Server: 192.168.1.100/24
Router LAN:   192.168.1.1/24
```

## 🔧 Flask Szerver Hálózati Beállítások

### 1. IP Cím Konfiguráció

**Statikus IP beállítása (Ubuntu/Debian):**
```bash
# /etc/netplan/01-network.yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: false
      addresses: [192.168.1.100/24]
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 1.1.1.1]
```

**Alkalmazás után:**
```bash
sudo netplan apply
```

### 2. Firewall Beállítások

**UFW (Ubuntu):**
```bash
# Flask szerver port engedélyezése
sudo ufw allow 5000/tcp

# Specifikus hálózatról
sudo ufw allow from 192.168.1.0/24 to any port 5000

# Firewall állapot
sudo ufw status
```

**iptables (közvetlen):**
```bash
# Flask port engedélyezése
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT

# Specifikus hálózat
sudo iptables -A INPUT -s 192.168.1.0/24 -p tcp --dport 5000 -j ACCEPT
```

### 3. Flask Alkalmazás Hálózati Konfiguráció

**Minden interfészen hallgatás:**
```python
# hulista.py módosítás
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

**Biztonságos konfiguráció:**
```python
# Csak LAN hálózatról
if __name__ == '__main__':
    app.run(host='192.168.1.100', port=5000, debug=False)
```

## 🏢 MikroTik Router Hálózati Beállítások

### 1. Interface Konfiguráció

**LAN Interface:**
```routeros
# Alapbeállítás
/interface ethernet set ether2 name=LAN

# IP cím beállítása
/ip address add address=192.168.1.1/24 interface=LAN network=192.168.1.0
```

**WAN Interface:**
```routeros
# WAN interface
/interface ethernet set ether1 name=WAN

# DHCP kliens (ISP-től)
/ip dhcp-client add interface=WAN disabled=no
```

### 2. DHCP Szerver Beállítás

**DHCP Pool konfiguráció:**
```routeros
# IP pool létrehozása
/ip pool add name=LAN_POOL ranges=192.168.1.50-192.168.1.200

# DHCP server beállítás
/ip dhcp-server add name=LAN_DHCP interface=LAN address-pool=LAN_POOL disabled=no

# DHCP hálózat
/ip dhcp-server network add address=192.168.1.0/24 gateway=192.168.1.1 dns-server=8.8.8.8,1.1.1.1
```

**Statikus DHCP foglalás (Flask szerver):**
```routeros
/ip dhcp-server lease add address=192.168.1.100 mac-address=XX:XX:XX:XX:XX:XX server=LAN_DHCP comment="Flask Server"
```

### 3. DNS Konfiguráció

**DNS beállítások:**
```routeros
# DNS szerverek
/ip dns set servers=8.8.8.8,1.1.1.1 allow-remote-requests=yes

# Statikus DNS bejegyzés
/ip dns static add address=192.168.1.100 name=flask-server.local
```

### 4. Routing Beállítások

**Alapértelmezett route:**
```routeros
# Automatikus (DHCP kliens által)
# Vagy manuális:
/ip route add dst-address=0.0.0.0/0 gateway=192.168.1.1
```

## 🔒 Biztonsági Beállítások

### 1. MikroTik Firewall Alapok

**Alapvető firewall szabályok:**
```routeros
# Bejövő kapcsolatok engedélyezése (LAN)
/ip firewall filter add chain=input action=accept connection-state=established,related
/ip firewall filter add chain=input action=accept in-interface=LAN

# Új kapcsolatok blokkolása (WAN)
/ip firewall filter add chain=input action=drop in-interface=WAN

# Forward szabályok (NAT)
/ip firewall filter add chain=forward action=accept connection-state=established,related
/ip firewall filter add chain=forward action=accept in-interface=LAN
/ip firewall filter add chain=forward action=drop
```

### 2. NAT Konfiguráció

**Masquerade beállítás:**
```routeros
# LAN → WAN NAT
/ip firewall nat add chain=srcnat action=masquerade out-interface=WAN
```

### 3. Szolgáltatás Biztonság

**Felesleges szolgáltatások letiltása:**
```routeros
# Veszélyes szolgáltatások kikapcsolása
/ip service disable telnet,ftp,www,ssh
/ip service set www-ssl port=8443
/ip service set winbox port=8291

# API letiltása (ha nem kell)
/ip service disable api,api-ssl
```

## 📡 Távoli Hozzáférés Konfiguráció

### 1. VPN Hozzáférés

**OpenVPN szerver (opcionális):**
```routeros
# Tanúsítványok generálása
/certificate add name=ca common-name=MyCA key-usage=key-cert-sign,crl-sign
/certificate add name=server common-name=server
/certificate add name=client common-name=client

# OpenVPN szerver
/interface ovpn-server server set enabled=yes port=1194 mode=ethernet
```

### 2. WireGuard VPN (RouterOS 7.0+)

**WireGuard konfiguráció:**
```routeros
# WireGuard interface
/interface wireguard add listen-port=51820 name=wireguard1

# Kulcspár generálása
/interface wireguard print
```

### 3. Port Forward (Flask szerver)

**Külső hozzáférés engedélyezése:**
```routeros
# Port forward Flask szerverhez
/ip firewall nat add chain=dstnat action=dst-nat to-addresses=192.168.1.100 to-ports=5000 protocol=tcp dst-port=5000 in-interface=WAN
```

## 🚀 Teljesítmény Optimalizáció

### 1. TCP Optimalizáció

**TCP ablak méret:**
```bash
# Linux szerver oldalon
echo 'net.core.rmem_max = 67108864' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 67108864' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_rmem = 4096 65536 67108864' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_wmem = 4096 65536 67108864' >> /etc/sysctl.conf
sudo sysctl -p
```

### 2. MikroTik Teljesítmény

**TCP optimalizáció RouterOS-ben:**
```routeros
# TCP beállítások
/ip settings set tcp-syncookies=yes rp-filter=strict

# Interface optimalizáció
/interface ethernet set ether1 advertise=1000M-full auto-negotiation=yes
```

### 3. Monitoring Beállítás

**Forgalom monitoring:**
```routeros
# Interface statisztikák engedélyezése
/interface set ether1 monitor-traffic=yes
/interface set ether2 monitor-traffic=yes

# SNMP engedélyezése
/snmp set enabled=yes
```

## 📊 Hálózati Tesztelés

### 1. Kapcsolat Tesztelés

**Router oldalról:**
```routeros
# Ping teszt Flask szerverre
/ping 192.168.1.100 count=5

# HTTP teszt
/tool fetch url="http://192.168.1.100:5000/status" dst-path=test.txt
```

**Szerver oldalról:**
```bash
# Ping teszt routerre
ping -c 5 192.168.1.1

# Port elérhetőség
nc -zv 192.168.1.1 80

# HTTP teszt saját magára
curl http://192.168.1.100:5000/status
```

### 2. Sávszélesség Teszt

**MikroTik bandwidth teszt:**
```routeros
# Helyi teszt
/tool bandwidth-test address=192.168.1.100 duration=10s direction=both
```

### 3. Latencia Monitoring

**Folyamatos ping monitoring:**
```routeros
# Ping watch
/tool ping-watch address=192.168.1.100 interval=1s
```

## 🌍 Internet Kapcsolat Optimalizáció

### 1. DNS Optimalizáció

**Gyors DNS szerverek:**
```routeros
# Cloudflare + Google DNS
/ip dns set servers=1.1.1.1,8.8.8.8,1.0.0.1,8.8.4.4

# DNS cache méret növelése
/ip dns set cache-size=4096
```

### 2. MTU Optimalizáció

**MTU beállítások:**
```routeros
# Interface MTU
/interface ethernet set ether1 mtu=1500

# MSS clamping
/ip firewall mangle add chain=forward action=change-mss new-mss=clamp-to-pmtu passthrough=yes protocol=tcp tcp-flags=syn
```

### 3. QoS Beállítások

**Traffic prioritás:**
```routeros
# Magyar IP lista forgalom prioritása
/queue simple add name="HU_IP_Priority" target=192.168.1.100/32 max-limit=10M/10M priority=1/1
```

## 🔧 Speciális Konfigurációk

### 1. Load Balancing

**Több WAN interfész:**
```routeros
# PCC load balancing
/ip route add dst-address=0.0.0.0/0 gateway=192.168.1.1 routing-mark=wan1 check-gateway=ping
/ip route add dst-address=0.0.0.0/0 gateway=192.168.2.1 routing-mark=wan2 check-gateway=ping
```

### 2. Failover Konfiguráció

**WAN failover:**
```routeros
# Elsődleges és másodlagos WAN
/ip route add dst-address=0.0.0.0/0 gateway=192.168.1.1 distance=1 check-gateway=ping
/ip route add dst-address=0.0.0.0/0 gateway=192.168.2.1 distance=2 check-gateway=ping
```

### 3. VLAN Konfiguráció

**VLAN szeparáció:**
```routeros
# VLAN interface
/interface vlan add interface=ether2 name=vlan100 vlan-id=100

# IP cím VLAN-hoz
/ip address add address=192.168.100.1/24 interface=vlan100
```

## 📈 Monitoring és Naplózás

### 1. System Logging

**Log beállítások:**
```routeros
# Részletes naplózás
/system logging action set memory memory-lines=10000
/system logging add topics=info action=memory
/system logging add topics=error action=memory
```

### 2. SNMP Monitoring

**SNMP konfiguráció:**
```routeros
# SNMP engedélyezése
/snmp set enabled=yes contact="admin@company.com" location="Server Room"
/snmp community set public address=192.168.1.0/24 name=public
```

### 3. Grafana Integration

**Prometheus exporter:**
```bash
# MikroTik Prometheus exporter
docker run -d \
  --name mikrotik-exporter \
  -p 9436:9436 \
  nshttpd/mikrotik-exporter \
  -address=192.168.1.1 \
  -user=monitoring \
  -password=monitoring123
```

## ⚠️ Hibaelhárítás

### Gyakori Hálózati Problémák

**1. Nem éri el a Flask szervert:**
- Firewall szabályok ellenőrzése
- IP cím konfiguráció
- Routing táblák

**2. Lassú kapcsolat:**
- MTU beállítások
- DNS feloldás
- Sávszélesség korlátozások

**3. Időszakos kapcsolat megszakadás:**
- Interface stabilitás
- Power management
- Kábel minőség

### Debug Parancsok

```routeros
# Kapcsolat debug
/tool torch interface=ether1
/ip route print
/ip firewall connection print where dst-address~"192.168.1.100"
```

## 📚 Következő Lépések

- **[API Dokumentáció](API-Documentation)** - Flask szerver API részletei
- **[Hibaelhárítás](Troubleshooting)** - Részletes hibaelhárítási útmutató
- **[Biztonsági Útmutató](Security-Guide)** - Haladó biztonsági beállítások

---

**Hálózat konfiguráció kész! Következő: [API Dokumentáció](API-Documentation)** 🚀
