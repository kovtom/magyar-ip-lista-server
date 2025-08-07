# Magyar IP Lista Server v1.0.0 🇭🇺

> **Első stabil verzió** - Teljes MikroTik RouterOS integráció kötegelt feldolgozással

## ⭐ Kiemelt Funkciók

### 🛡️ Router Védelem
- **Kötegelt feldolgozás**: 50 IP címenként 30s szünet
- **Túlterhelés védelem**: MikroTik router teljesítményének megóvása
- **Optimalizált script**: RouterOS .rsc formátum

### 🌐 Multiplatform Támogatás
- **Windows**: Waitress WSGI szerver
- **Linux/Mac**: Gunicorn WSGI szerver  
- **Docker**: Konténerizált telepítés (tervezett v1.1.0)

### 📚 Teljes Dokumentáció
- 🇬🇧 **Angol** és 🇭🇺 **Magyar** nyelvű útmutatók
- **Telepítési scriptek** minden platformra
- **Hálózati konfiguráció** részletes leírással

## 📦 Letöltési Opciók

### Ajánlott Telepítés (Git)
```bash
git clone https://github.com/kovtom/magyar-ip-lista-server.git
cd magyar-ip-lista-server
pip install -r requirements.txt
```

### ZIP Letöltés
Töltsd le a forráskódot ZIP fájlként a **"Source code"** linkekről alább.

## 🚀 Gyors Indítás

### Windows
```cmd
# Függőségek telepítése
pip install -r requirements.txt

# Produkciós szerver indítása
start_waitress.bat

# Vagy fejlesztői mód
python hulista.py
```

### Linux/Mac
```bash
# Függőségek telepítése
pip install -r requirements.txt

# Produkciós szerver indítása
chmod +x start_gunicorn.sh
./start_gunicorn.sh

# Vagy fejlesztői mód
python hulista.py
```

## 🔧 MikroTik Konfiguráció

1. **Script telepítése**: Másold be a `mikrotik_update_script.rsc` tartalmat
2. **IP cím beállítása**: Módosítsd a `SERVER_URL` változót
3. **Ütemezés**: Állítsd be napi futásra a Scheduler-ben

```routeros
:local SERVER_URL "http://192.168.1.100:5000/hu_ip_list.rsc"
```

## 📊 Technikai Adatok

- **IP címtartományok**: ~903 magyar blokk
- **Feldolgozási idő**: ~8.5 perc (kötegelt)
- **Memory használat**: 50-100 MB
- **Támogatott RouterOS**: 6.40+

## 🐛 Hibabejelentés

Ha problémába ütközöl:
1. Ellenőrizd a [dokumentációt](README.md)
2. Nézd meg a [hibakezelési útmutatót](README.md#troubleshooting)
3. Nyiss [GitHub Issue-t](https://github.com/kovtom/magyar-ip-lista-server/issues)

## 🔄 Frissítés Régebbi Verzióról

Ha korábban használtad ezt a projektet:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

⚠️ **Figyelem**: A fájlformátum megváltozott `.txt`-ről `.rsc`-re!

## 🙏 Köszönetnyilvánítás

Köszönet mindenkinek, aki hozzájárult a projekt fejlesztéséhez és teszteléséhez.

---

**Magyar IP Lista Server** - Automatikus IP lista kezelés MikroTik routerekhez 🚀
