# MikroTik Konfiguráció

> **Teljes útmutató a Magyar IP Lista Server RouterOS integrációjához**

## 🎯 Áttekintés

Ez az útmutató bemutatja, hogyan konfiguráld a MikroTik routert, hogy automatikusan letöltse és frissítse a magyar IP listát a Flask szerverről.

## 📋 Előfeltételek

- **RouterOS verzió**: 6.40 vagy újabb (ajánlott: 7.x)
- **Internet kapcsolat**: A router eléri a Flask szervert
- **Adminisztrátori jogosultságok**: Teljes hozzáférés a RouterOS-hez
- **Elérési mód**: WebFig, WinBox, SSH vagy Console

## 🔧 Script Telepítése

### 1. RouterOS Felület Megnyitása

**WebFig módszer:**
1. Böngészőben: `http://[router-ip]` (pl. `192.168.1.1`)
2. Bejelentkezés admin felhasználóval

**WinBox módszer:**
1. WinBox letöltése: [mikrotik.com](https://mikrotik.com/download)
2. Csatlakozás a router IP címére

### 2. Script Létrehozása

**Navigáció:**
```
System → Scripts → Add New Script
```

**Script beállítások:**
- **Name**: `HU_IP_Update`
- **Policy**: `read,write,policy,test` (minden jog megadása)
- **Source**: Másolja be az alábbi scriptet

### 3. Script Forráskód

```routeros
# MikroTik Script - Magyar IP Lista Automatikus Frissito
# Ez a script naponta frissiti a magyar IP cimek listajat a Flask szerverrol
# 
# FONTOS: A script kotegelt feldolgozast hasznal a router terhelesenek csokkentesere!
# 50 IP cimenkent 30 masodperc szunetet tart a feldolgozas soran.
# 
# Telepites:
# 1. Masolja be ezt a scriptet a MikroTik System > Scripts menube
# 2. Nevezze el peldaul "HU_IP_Update"-nek
# 3. Allitsa be a Scheduler-ben napi futasra (ajanlott ejjel)
#
# Beallitas elott modositsa a SERVER_URL valtozot a sajat szerver cimere!

# BEALLITASOK - MODOSITSA EZEKET A SAJAT KORNYEZETANAK MEGFELELOEN
:local SERVER_URL "http://192.168.1.100:5000/hu_ip_list.rsc"
:local LIST_NAME "HU_IP"

# Kotegelt feldolgozas beallitasai
:local BATCH_SIZE 50
:local DELAY_SECONDS 30

# Script kezdete
:log info "Magyar IP lista frissites kezdese..."

# Aktualis ido lekereses
:local currentTime [/system clock get time]
:local currentDate [/system clock get date]
:log info ("Frissites idopontja: " . $currentDate . " " . $currentTime)

# Regi lista elemeinek torlese
:log info "Regi HU_IP lista torlese..."
:local oldCount [/ip firewall address-list print count-only where list=$LIST_NAME]
:log info ("Torlendo elemek szama: " . $oldCount)

/ip firewall address-list remove [find list=$LIST_NAME]
:log info "Regi lista torolve"

# Uj lista letoltese es betoltese
:log info ("Uj lista letoltese: " . $SERVER_URL)

:do {
    # HTTP GET keres a szerverhez - helyes szintaxis
    /tool fetch url=$SERVER_URL dst-path="hu_ip_list.rsc"
    :log info "Fajl sikeresen letoltve"
    
    # Letoltott fajl beolvasasa
    :local scriptContent [/file get [/file find name="hu_ip_list.rsc"] contents]
    
    :if ([:len $scriptContent] > 0) do={
        :log info "Script tartalom beolvasva, kotegelt vegrehajtasa kezdodik..."
        :log info ("Koteg meret: " . $BATCH_SIZE . " IP cim, szunet: " . $DELAY_SECONDS . " masodperc")
        
        # Script vegrehajtasa (a letoltott fajl MikroTik parancsokat tartalmaz kotegelt feldolgozassal)
        :execute script=$scriptContent
        
        :log info "Kotegelt script sikeresen vegrehajtva"
        
        # Uj lista elemeinek szamolasa
        :local newCount [/ip firewall address-list print count-only where list=$LIST_NAME]
        :log info ("Uj lista betoltve. Elemek szama: " . $newCount)
        
        # Letoltott fajl torlese (takarekossag)
        /file remove [find name="hu_ip_list.rsc"]
        
        :log info "Magyar IP lista frissites sikeresen befejezve!"
        
    } else={
        :log error "Fajl letoltese sikertelen volt!"
    }
    
} on-error={
    :log error "Hiba tortent a lista letoltese soran!"
    :log error "Ellenorizze a halozati kapcsolatot es a szerver elerhetoseget!"
    :log error "Szerver URL: " . $SERVER_URL
}

:log info "Magyar IP lista frissites script befejezve"
```

### 4. Script Testreszabása

**Kötelező módosítások:**
```routeros
# Módosítsa ezt a sort a saját szerver IP címére!
:local SERVER_URL "http://192.168.1.100:5000/hu_ip_list.rsc"
#                        ^^^^^^^^^^^
#                        Az Ön szerver IP címe
```

**Opcionális beállítások:**
```routeros
:local LIST_NAME "HU_IP"           # Address list neve
:local BATCH_SIZE 50               # Köteg mérete
:local DELAY_SECONDS 30            # Szünet másodpercekben
```

## ⏰ Ütemezett Futtatás

### 1. Scheduler Létrehozása

**Navigáció:**
```
System → Scheduler → Add New Task
```

### 2. Scheduler Beállítások

**Alapbeállítások:**
- **Name**: `HU_IP_Daily_Update`
- **Start Date**: `jan/01/1970` (vagy mai dátum)
- **Start Time**: `03:00:00` (éjjel 3:00 - ajánlott)
- **Interval**: `1d 00:00:00` (naponta)

**Policy beállítások:**
- ✅ `read`
- ✅ `write` 
- ✅ `policy`
- ✅ `test`

**Script beállítás:**
- **On Event**: `HU_IP_Update` (a script neve)

### 3. CLI Parancsokkal

```routeros
# Scheduler létrehozása CLI-ben
/system scheduler add name=HU_IP_Daily_Update start-date=jan/01/1970 start-time=03:00:00 interval=1d on-event=HU_IP_Update policy=read,write,policy,test
```

## ✅ Teszt Futtatás

### 1. Manuális Script Futtatás

**WebFig/WinBox:**
1. `System → Scripts`
2. Válassza ki a `HU_IP_Update` scriptet
3. Kattintson a **"Run Script"** gombra

**CLI:**
```routeros
/system script run HU_IP_Update
```

### 2. Eredmény Ellenőrzése

**Address List megtekintése:**
```routeros
/ip firewall address-list print where list=HU_IP
```

**Lista méret ellenőrzése:**
```routeros
/ip firewall address-list print count-only where list=HU_IP
```

**Log üzenetek megtekintése:**
```routeros
/log print where topics~"info"
```

## 🔍 Kötegelt Feldolgozás Működése

### Mi történik a futtatás során?

1. **Előkészítés**: Régi lista törlése
2. **Letöltés**: `.rsc` fájl letöltése a szerverről
3. **Kötegelt végrehajtás**: 
   - 50 IP cím hozzáadása
   - 30 másodperc szünet
   - Következő 50 IP cím
   - És így tovább...
4. **Befejezés**: Ideiglenes fájl törlése

### Időkalkuláció

**~903 IP cím esetén:**
- **Kötegek száma**: 18 köteg (903 ÷ 50)
- **Szünetek**: 17 × 30 másodperc = 8.5 perc
- **Feldolgozási idő**: ~9-10 perc összesen

## 🛡️ Firewall Integráció

### Address List Használata

**Blokkolási szabály:**
```routeros
# Magyar IP címek blokkolása
/ip firewall filter add chain=forward action=drop src-address-list=HU_IP comment="Block Hungarian IPs"
```

**Engedélyezési szabály:**
```routeros
# Csak magyar IP címek engedélyezése
/ip firewall filter add chain=forward action=accept src-address-list=HU_IP comment="Allow only Hungarian IPs"
/ip firewall filter add chain=forward action=drop comment="Drop all other traffic"
```

**NAT szabály:**
```routeros
# Magyar IP címek speciális NAT-ja
/ip firewall nat add chain=srcnat action=masquerade src-address-list=HU_IP comment="NAT for Hungarian IPs"
```

## 🔍 Monitoring és Naplózás

### Log Szűrés

**Magyar IP lista üzenetek:**
```routeros
/log print where message~"Magyar IP"
```

**Hibakeresés:**
```routeros
/log print where topics~"error" and message~"IP"
```

### Rendszeres Ellenőrzések

**Heti jelentés script:**
```routeros
:local count [/ip firewall address-list print count-only where list=HU_IP]
:log info ("Heti jelentes: Magyar IP lista merete: " . $count)
```

## ⚠️ Hibaelhárítás

### Gyakori Problémák

**1. Script nem fut:**
- Policy jogosultságok ellenőrzése
- Script szintaxis hibák
- Scheduler beállítások

**2. Letöltési hiba:**
```routeros
# Hálózati kapcsolat tesztelése
/tool fetch url=http://192.168.1.100:5000/status
```

**3. Túl sok IP cím:**
- Router memória ellenőrzése: `/system resource print`
- Köteg méret csökkentése: `BATCH_SIZE 25`

**4. Lassú feldolgozás:**
- Szünet idő csökkentése: `DELAY_SECONDS 15`
- Éjszakai futtatás beállítása

### Debugging Script

```routeros
# Debug információk
:log info ("Rendszer memória: " . [/system resource get free-memory])
:log info ("Address list méret előtte: " . [/ip firewall address-list print count-only where list=HU_IP])
```

## 🔄 Frissítések és Karbantartás

### Script Frissítése

1. **Backup készítése**:
   ```routeros
   /export file=backup_before_update
   ```

2. **Új script verzió telepítése**
3. **Teszt futtatás**
4. **Scheduler újraaktiválása**

### Rendszeres Karbantartás

**Havi feladatok:**
- Log fájlok tisztítása
- Address list méret ellenőrzése
- Hálózati kapcsolat tesztelése
- Script frissítések keresése

## 📚 Következő Lépések

- **[API Dokumentáció](API-Documentation)** - További automatizálási lehetőségek
- **[Hálózati Beállítások](Network-Configuration)** - Optimális hálózati konfiguráció
- **[Hibaelhárítás](Troubleshooting)** - Részletes hibaelhárítási útmutató

---

**MikroTik konfiguráció kész! Következő: [Hálózati Beállítások](Network-Configuration)** 🚀
