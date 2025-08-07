# Changelog

Az összes jelentős változás ebben a projektben dokumentálva van ebben a fájlban.

A formátum a [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) alapján,
és ez a projekt a [Semantic Versioning](https://semver.org/spec/v2.0.0.html) szabványt követi.

## [1.0.0] - 2025-08-07

### Hozzáadott
- Kötegelt feldolgozás 50 IP címenként 30 másodperces szünetekkel
- RouterOS script (.rsc) formátum generálás
- Helyes MikroTik `/tool fetch` szintaxis támogatás
- Multiplatform WSGI szerver támogatás (Gunicorn/Waitress)
- Részletes többnyelvű dokumentáció (angol/magyar)
- Windows tűzfal konfiguráció útmutatók
- Linux systemd szolgáltatás integráció
- Hálózati konfigurációs útmutatók
- Automatikus napi IP lista frissítés
- REST API JSON válaszokkal
- Web interface státusz ellenőrzéshez
- Router teljesítményvédelem nagy listák betöltésekor

### Módosított
- Fájlformátum váltás .txt-ről .rsc-re
- MikroTik script teljes újraírása kötegelt feldolgozással
- Flask szerver optimalizálás produkciós használatra
- Dokumentáció átstrukturálása és bővítése

### Javított
- MikroTik kompatibilitási problémák
- Windows WSGI szerver támogatás (Waitress)
- Hibakezelés és naplózás javítása
- Hálózati elérési problémák megoldása

### Eltávolított
- Régi egyszerű IP lista formátum
- Elavult dokumentáció fájlok

## [Unreleased]

### Tervezett
- IPv6 támogatás
- Webhook értesítések
- Több IP lista forrás támogatás
- Docker konténer
- Web admin interface

---

## Verziószámozás Rendszer

- **MAJOR** verzió: Inkompatibilis API változások
- **MINOR** verzió: Új funkciók visszamenőlegesen kompatibilis módon
- **PATCH** verzió: Visszamenőlegesen kompatibilis hibajavítások

## Release Típusok

- **🚀 Major Release**: Jelentős új funkciók, esetleg breaking changes
- **✨ Minor Release**: Új funkciók, javítások, kompatibilitás megőrzése
- **🐛 Patch Release**: Csak hibajavítások és kisebb fejlesztések
- **🔒 Security Release**: Biztonsági javítások (sürgős)

## Támogatási Szabályzat

- **Aktuális verzió**: Teljes támogatás
- **Előző major verzió**: Biztonsági javítások 6 hónapig
- **Régebbi verziók**: Közösségi támogatás
