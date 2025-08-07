# MikroTik Script - Magyar IP Lista Automatikus Frissito
# Ez a script naponta frissiti a magyar IP cimek listajat a Flask szerverrol
# 
# Telepites:
# 1. Masolja be ezt a scriptet a MikroTik System > Scripts menube
# 2. Nevezze el peldaul "HU_IP_Update"-nek
# 3. Allitsa be a Scheduler-ben napi futasra
#
# Beallitas elott modositsa a SERVER_URL valtozot a sajat szerver cimere!

# BEALLITASOK - MODOSITSA EZEKET A SAJAT KORNYEZETANAK MEGFELELOEN
:local SERVER_URL "http://192.168.1.100:5000/hu_ip_list.txt"
:local LIST_NAME "HU_IP"

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
    # HTTP GET keres a szerverhez
    :local result [/tool fetch url=$SERVER_URL as-value output=user]
    
    :if (($result->"status") = "finished") do={
        :local data ($result->"data")
        :local lineCount 0
        :local successCount 0
        :local errorCount 0
        
        # Sorok feldolgozasa
        :local lines [:toarray ""]
        :local currentLine ""
        :local pos 0
        
        # Adatok sorokra bontasa
        :while ($pos < [:len $data]) do={
            :local char [:pick $data $pos ($pos+1)]
            :if ($char = "\n" || $char = "\r") do={
                :if ([:len $currentLine] > 0) do={
                    :set lines ($lines, $currentLine)
                    :set currentLine ""
                }
            } else={
                :set currentLine ($currentLine . $char)
            }
            :set pos ($pos + 1)
        }
        
        # Utolso sor hozzaadasa ha nem ures
        :if ([:len $currentLine] > 0) do={
            :set lines ($lines, $currentLine)
        }
        
        # Parancsok vegrehajtasa
        :foreach line in=$lines do={
            :set lineCount ($lineCount + 1)
            
            # Csak MikroTik parancsokat dolgozza fel
            :if ([:pick $line 0 3] = "/ip") do={
                :do {
                    # Parancs vegrehajtasa
                    [:parse $line]
                    :set successCount ($successCount + 1)
                } on-error={
                    :set errorCount ($errorCount + 1)
                    :log warning ("Hiba a parancs vegrehajtasaban: " . $line)
                }
            }
        }
        
        # Eredmeny ellenorzese
        :local finalCount [/ip firewall address-list print count-only where list=$LIST_NAME]
        
        :log info ("Frissites befejezve!")
        :log info ("Feldolgozott sorok: " . $lineCount)
        :log info ("Sikeres parancsok: " . $successCount)
        :log info ("Hibas parancsok: " . $errorCount)
        :log info ("Uj lista merete: " . $finalCount . " IP cim/halozat")
        
        # Ertesites kuldese (opcionalis)
        # /tool e-mail send to="admin@domain.com" subject="MikroTik HU IP lista frissitve" body=("Uj magyar IP lista betoltve: " . $finalCount . " elem")
        
    } else={
        :log error ("HTTP keres sikertelen: " . ($result->"status"))
        :log error "A lista frissitese sikertelen volt!"
    }
    
} on-error={
    :log error "Hiba tortent a lista letoltese soran!"
    :log error "Ellenorizze a halozati kapcsolatot es a szerver elerhetoseget!"
}

:log info "Magyar IP lista frissites script befejezve"
