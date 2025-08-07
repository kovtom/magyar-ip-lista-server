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
