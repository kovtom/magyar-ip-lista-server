# Magyar IP Lista Server - Release Notes

## v1.1.0 - DShield Block List Integráció (2025-08-07)

### 🎉 Főbb Újdonságok

#### 🔒 Háromforrású Biztonsági Platform
- **DShield Block List** integráció (`feeds.dshield.org/block.txt`)
- **Spamhaus DROP Lista** (már meglévő)
- **Magyar IP Lista** (már meglévő)
- **Egységes MikroTik integráció** mind a három forráshoz

#### 🛡️ DShield Block List Funkciók
- **Új biztonsági forrás**: DShield Attack Block lista
- **Egyedi parser**: Tab-elválasztott formátum (IP + netmask → CIDR)
- **Address list**: `DSHIELD_BLOCK` MikroTik RouterOS-hez
- **Lefedettség**: 20+ rosszindulatú IP cím automatikus blokkolása
- **Ütemezés**: Napi frissítés 2:30-kor

#### 🌐 Továbbfejlesztett Flask Szerver
- **Új endpoint**: `/dshield_block.rsc` - DShield scriptek letöltése
- **Frissített Status API**: Mind a három forrás a `/status` végponton
- **Javított webes felület**: Átfogó dashboard minden forrással
- **Valós idejű monitoring**: Élő fájl státusz és IP számok

### 📊 Jelenlegi Biztonsági Lefedettség

| Forrás | Lefedettség | Address Lista | Cél |
|--------|-------------|---------------|-----|
| 🇭🇺 **Magyar IP-k** | 903 cím | `HU_IP` | Földrajzi engedélyezési lista |
| 🚫 **Spamhaus DROP** | 1,596 cím | `SPAMHAUS_DROP` | Spam védelem |
| 🛡️ **DShield Block** | 20+ cím | `DSHIELD_BLOCK` | Támadás megelőzés |

### 🛠️ Technikai Fejlesztések

#### ⚡ Kód Minőség
- Duplikált függvény definíciók javítása
- Javított hibakezelés és naplózás
- Megbízhatóbb kötegelt feldolgozás
- Jobb erőforrás kezelés

#### 📁 Projekt Menedzsment
- Frissített `.gitignore` DShield fájlokhoz (`dshield_block.rsc`, `block_*.txt`)
- Javított ütemező lépcsőzetes frissítésekkel
- Átfogó Wiki dokumentáció (8 oldal)

#### 🔄 Frissítési Ütemezés
- **Magyar IP**: naponta 2:00-kor
- **Spamhaus DROP**: naponta 2:15-kor  
- **DShield Block**: naponta 2:30-kor

### 🐛 Javított Hibák

- Duplikált Flask route definíciók kijavítása
- Ütemező sleep duplikáció megoldása
- Javított fájlkezelési edge case-ek

---

## v1.0.0 - Első Stabil Verzió (2025-08-07)

### 🚀 Új Funkciók

#### Kötegelt Feldolgozás
- **50 IP címenként kötegek** a MikroTik router teljesítményének védelme érdekében
- **30 másodperces szünetek** kötegek között a túlterhelés megelőzésére
- **Automatikus script generálás** RouterOS `.rsc` formátumban

#### MikroTik Integráció
- **Helyes `/tool fetch` szintaxis** használata
- **Automatikus lista frissítés** napi ütemezéssel
- **Részletes hibakezelés** és naplózás
- **Router-barát** megközelítés nagy IP listák kezelésére

#### Multiplatform WSGI Szerver Támogatás
- **Gunicorn** (Linux/Mac) - nagy teljesítményű produkciós szerver
- **Waitress** (Windows) - Windows-kompatibilis WSGI szerver
- **Fejlesztői mód** Flask beépített szerverrel

### 🔧 Technikai Jellemzők

#### Flask Szerver
- **Automatikus frissítés** naponta 2:00-kor
- **REST API** JSON válaszokkal
- **Web interface** státusz ellenőrzéshez
- **Hálózati hozzáférés** 0.0.0.0:5000 porton

#### IP Lista Feldolgozás
- **Forrás**: IPdeny.com magyar IP blokkok
- **Formátum**: RouterOS script (.rsc)
- **Statisztikák**: ~903 IP címtartomány
- **Frissítési gyakoriság**: Naponta

### 📚 Dokumentáció

#### Többnyelvű Támogatás
- 🇬🇧 **Angol dokumentáció** (README.md)
- 🇭🇺 **Magyar dokumentáció** (README_hu.md)
- **Hálózati konfigurációs útmutatók**
- **Hibakezelési instrukciók**

#### Telepítési Útmutatók
- **Windows tűzfal konfiguráció**
- **Linux systemd szolgáltatás**
- **MikroTik RouterOS beállítás**
- **Port forwarding útmutató**

### 🛠️ Rendszerkövetelmények

#### Minimális Követelmények
- **Python 3.6+**
- **2 GB RAM**
- **100 MB szabad hely**
- **Hálózati kapcsolat**

#### Ajánlott Konfiguráció
- **Python 3.8+**
- **4 GB RAM**
- **500 MB szabad hely**
- **Stabil internet kapcsolat**

### 📦 Telepítés

#### Gyors Telepítés
```bash
# Repository klónozása
git clone https://github.com/kovtom/magyar-ip-lista-server.git
cd magyar-ip-lista-server

# Függőségek telepítése
pip install -r requirements.txt

# Szerver indítása
python hulista.py
```

#### Produkciós Telepítés

**Windows:**
```cmd
# Waitress szerver indítása
start_waitress.bat
```

**Linux/Mac:**
```bash
# Gunicorn szerver indítása
./start_gunicorn.sh
```

### 🔒 Biztonsági Funkciók

- ✅ **Jelszó nélküli működés** - HTTP alapú letöltés
- ✅ **Automatikus frissítés** - nincs manuális beavatkozás
- ✅ **Központosított kezelés** - egy szerver több router
- ✅ **Részletes naplózás** - minden művelet követhető

### 🐛 Ismert Problémák és Megoldások

#### Windows Kompatibilitás
- **Gunicorn** nem támogatott Windows-on → **Waitress** használata
- **PowerShell execution policy** → `Set-ExecutionPolicy` beállítás

#### Hálózati Problémák
- **Port 5000 foglalt** → port váltás 5001-re vagy 8080-ra
- **Tűzfal blokkolás** → Windows Defender/UFW/firewalld konfiguráció

### 🔄 Frissítési Útmutató

Meglévő telepítés frissítése:
```bash
# Legújabb verzió letöltése
git pull origin main

# Függőségek frissítése
pip install -r requirements.txt --upgrade

# Szerver újraindítása
# Windows: start_waitress.bat
# Linux/Mac: ./start_gunicorn.sh
```

### 📞 Támogatás

- **GitHub Issues**: Bug jelentések és feature kérések
- **Dokumentáció**: Részletes útmutatók README fájlokban
- **Példa konfigurációk**: MikroTik script sablonok

### 🔮 Tervezett Funkciók (v1.2.0)

- **IPv6 támogatás** hozzáadása
- **Webhook értesítések** lista frissítésről
- **További biztonsági források** (például Blocklist.de)
- **Web admin interface** konfigurációhoz
- **Docker konténer** egyszerű telepítéshez
- **Grafikus statisztikák** a webes felületen

---

## Támogatott Platformok

| Platform | Szerver | Státusz | Megjegyzés |
|----------|---------|---------|------------|
| Windows 10/11 | Waitress | ✅ Teljes | Ajánlott produkciós megoldás |
| Ubuntu 20.04+ | Gunicorn | ✅ Teljes | Systemd integráció |
| CentOS 8+ | Gunicorn | ✅ Teljes | Firewalld konfiguráció |
| macOS 11+ | Gunicorn | ✅ Teljes | Homebrew Python |
| Debian 11+ | Gunicorn | ✅ Teljes | APT csomagkezelő |

## Letöltési Statisztikák

- **Teljes letöltési méret**: ~2.5 MB
- **Telepítési idő**: 2-5 perc
- **Első indítás**: 30-60 másodperc
- **Memory használat**: ~50-100 MB

---

**Köszönjük, hogy használod a Magyar IP Lista Servert!** 🇭🇺

Ha problémába ütközöl, nyiss egy GitHub Issue-t vagy tekintsd meg a dokumentációt.
