# Magyar IP Lista Flask Szerver

Egy Flask alapú webszerver, amely automatikusan frissíti a magyar IP blokk listát és szolgáltatja azt MikroTik routereknek RouterOS parancsok formájában.

## Követelmények

- Python 3.6+
- flask könyvtár
- requests könyvtár
- schedule könyvtár

## Telepítés

1. Klónozza vagy töltse le a projektet
2. Telepítse a szükséges függőségeket:
   ```
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

## Fájlok a projektben

- **hulista.py** - Flask szerver főprogramja
- **mikrotik_update_script.rsc** - MikroTik RouterOS script
- **hu_ip_list.txt** - Generált MikroTik parancsok (automatikusan frissül)
- **README.md** - Ez a dokumentáció
