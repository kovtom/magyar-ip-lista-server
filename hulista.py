import requests
import os
from urllib.parse import urlparse
from datetime import datetime
from flask import Flask, send_file, jsonify
import threading
import time
import schedule
import socket

URL = "https://www.ipdeny.com/ipblocks/data/countries/hu.zone"
SPAMHAUS_URL = "https://www.spamhaus.org/drop/drop.txt"
DSHIELD_URL = "https://feeds.dshield.org/block.txt"

def get_local_ip_addresses():
    """Visszaadja az osszes helyi IP cimet"""
    ip_addresses = ['127.0.0.1']  # localhost mindig benne van
    
    try:
        # Halozati interfeszek IP cimeinek lekerese
        hostname = socket.gethostname()
        local_ips = socket.gethostbyname_ex(hostname)[2]
        
        for ip in local_ips:
            if ip != '127.0.0.1' and not ip.startswith('169.254'):  # loopback es APIPA kihagyasa
                ip_addresses.append(ip)
                
        # Alternativ modszer - socket kapcsolattal
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                main_ip = s.getsockname()[0]
                if main_ip not in ip_addresses:
                    ip_addresses.append(main_ip)
        except:
            pass
            
    except Exception as e:
        print(f"IP cimek lekerese sikertelen: {e}")
    
    return ip_addresses

def download_file_as_text(url, output_filename=None):
    """
    Letolt egy fajlt a megadott URL-rol es elmenti szoveges fajlkent.
    
    Args:
        url (str): A letoltendo fajl URL-je
        output_filename (str, optional): A kimeneti fajl neve. Ha None, akkor az URL-bol generalja.
    
    Returns:
        str: A mentett fajl neve
    """
    try:
        # HTTP GET keres kuldese
        print(f"Letoltes indul: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Hibat dob ha nem 200-as status
        
        # Ha nincs megadva fajlnev, generaljunk egyet az URL-bol
        if output_filename is None:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename:
                filename = "downloaded_file"
            
            # Datum es ido hozzaadasa a fajlnevhez
            current_time = datetime.now()
            timestamp = current_time.strftime("%Y%m%d_%H%M%S")
            
            # Fajlnev es kiterjesztes szetvalasztasa
            name_without_ext = filename
            if '.' in filename:
                name_without_ext = filename.rsplit('.', 1)[0]
            
            # Uj fajlnev osszealitasa: eredeti_nev_YYYYMMDD_HHMMSS.txt
            output_filename = f"{name_without_ext}_{timestamp}.txt"
        
        # Fajl mentese szoveges modban
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write(response.text)
        
        print(f"Fajl sikeresen mentve: {output_filename}")
        return output_filename
        
    except requests.exceptions.RequestException as e:
        print(f"Hiba a letoltes soran: {e}")
        return None
    except Exception as e:
        print(f"Varatlan hiba: {e}")
        return None

def convert_to_mikrotik_commands(input_filename, output_filename="hu_ip_list.rsc"):
    """
    Atalakitja az IP cimeket MikroTik RouterOS parancsokka.
    
    Args:
        input_filename (str): A bemeneti fajl neve (IP cimeket tartalmaz)
        output_filename (str): A kimeneti fajl neve (alapertelmezett: hu_ip_list.rsc)
    
    Returns:
        str: A kimeneti fajl neve, vagy None hiba eseten
    """
    try:
        # Fix fajlnev hasznalata
        output_filename = "hu_ip_list.rsc"
        
        print(f"Atalakitas indul: {input_filename} -> {output_filename}")
        
        # Bemeneti fajl olvasasa es atalakitas
        with open(input_filename, 'r', encoding='utf-8') as input_file:
            lines = input_file.readlines()
        
        # MikroTik parancsok generalasa kötegelt feldolgozással
        mikrotik_commands = []
        processed_count = 0
        batch_size = 50  # 50 IP címenként kötegek
        
        # Script fejlec hozzáadása
        mikrotik_commands.append("# Magyar IP Lista - Automatikusan generalt MikroTik script")
        mikrotik_commands.append("# Kotegelt feldolgozas 50 IP cimenkent 30 masodperc szunettel")
        mikrotik_commands.append("")
        mikrotik_commands.append(":log info \"Magyar IP lista betoltese megkezdve...\"")
        mikrotik_commands.append("")
        
        batch_count = 0
        for line in lines:
            ip_address = line.strip()
            # Csak akkor dolgozzuk fel, ha valodi IP cim vagy halozat van a sorban
            if ip_address and not ip_address.startswith('#') and '/' in ip_address:
                # Köteg kezdete jelölés
                if processed_count % batch_size == 0 and processed_count > 0:
                    batch_count += 1
                    mikrotik_commands.append("")
                    mikrotik_commands.append(f":log info \"Koteg {batch_count} feldolgozasa befejezve, 30 masodperc szunet...\"")
                    mikrotik_commands.append(":delay 30")
                    mikrotik_commands.append(f":log info \"Koteg {batch_count + 1} feldolgozasa kezdodik...\"")
                    mikrotik_commands.append("")
                
                mikrotik_command = f"/ip firewall address-list add list=HU_IP address={ip_address}"
                mikrotik_commands.append(mikrotik_command)
                processed_count += 1
        
        # Script lábléc hozzáadása
        mikrotik_commands.append("")
        mikrotik_commands.append(f":log info \"Magyar IP lista betoltese befejezve. Osszes IP cim: {processed_count}\"")
        mikrotik_commands.append(":log info \"Kotegelt feldolgozas sikeresen vegrehajtva!\"")
        
        # Kimeneti fajl irasa
        with open(output_filename, 'w', encoding='utf-8') as output_file:
            for command in mikrotik_commands:
                output_file.write(command + '\n')
        
        print(f"Atalakitas befejezve! {processed_count} IP cim atalakitva.")
        print(f"MikroTik parancsok mentve: {output_filename}")
        return output_filename
        
    except FileNotFoundError:
        print(f"Hiba: A fajl nem talalhato: {input_filename}")
        return None
    except Exception as e:
        print(f"Varatlan hiba az atalakitas soran: {e}")
        return None

def convert_spamhaus_to_mikrotik(input_filename, output_filename="spamhaus_drop.rsc"):
    """
    Atalakitja a Spamhaus DROP lista IP cimeket MikroTik RouterOS parancsokka.
    
    Args:
        input_filename (str): A bemeneti fajl neve (Spamhaus DROP format)
        output_filename (str): A kimeneti fajl neve (alapertelmezett: spamhaus_drop.rsc)
    
    Returns:
        str: A kimeneti fajl neve, vagy None hiba eseten
    """
    try:
        # Fix fajlnev hasznalata
        output_filename = "spamhaus_drop.rsc"
        
        print(f"Spamhaus atalakitas indul: {input_filename} -> {output_filename}")
        
        # Bemeneti fajl olvasasa es atalakitas
        with open(input_filename, 'r', encoding='utf-8') as input_file:
            lines = input_file.readlines()
        
        # MikroTik parancsok generalasa kötegelt feldolgozással
        mikrotik_commands = []
        processed_count = 0
        batch_size = 50  # 50 IP címenként kötegek
        
        # Script fejlec hozzáadása
        mikrotik_commands.append("# Spamhaus DROP Lista - Automatikusan generalt MikroTik script")
        mikrotik_commands.append("# Spamhaus.org/drop/drop.txt alapjan")
        mikrotik_commands.append("# Kotegelt feldolgozas 50 IP cimenkent 30 masodperc szunettel")
        mikrotik_commands.append("")
        mikrotik_commands.append(":log info \"Spamhaus DROP lista betoltese megkezdve...\"")
        mikrotik_commands.append("")
        
        batch_count = 0
        for line in lines:
            line = line.strip()
            # Komment sorok és üres sorok kihagyása
            if line and not line.startswith(';') and not line.startswith('#'):
                # IP cím kinyerése a sor elejéről (a ';' előtti rész)
                if ';' in line:
                    ip_part = line.split(';')[0].strip()
                else:
                    ip_part = line
                
                # Ellenőrzés, hogy CIDR formátumú IP tartomány-e
                if '/' in ip_part and '.' in ip_part:
                    # Köteg kezdete jelölés
                    if processed_count % batch_size == 0 and processed_count > 0:
                        batch_count += 1
                        mikrotik_commands.append("")
                        mikrotik_commands.append(f":log info \"Koteg {batch_count} feldolgozasa befejezve, 30 masodperc szunet...\"")
                        mikrotik_commands.append(":delay 30")
                        mikrotik_commands.append(f":log info \"Koteg {batch_count + 1} feldolgozasa kezdodik...\"")
                        mikrotik_commands.append("")
                    
                    mikrotik_command = f"/ip firewall address-list add list=SPAMHAUS_DROP address={ip_part}"
                    mikrotik_commands.append(mikrotik_command)
                    processed_count += 1
        
        # Script lábléc hozzáadása
        mikrotik_commands.append("")
        mikrotik_commands.append(f":log info \"Spamhaus DROP lista betoltese befejezve. Osszes IP cim: {processed_count}\"")
        mikrotik_commands.append(":log info \"Kotegelt feldolgozas sikeresen vegrehajtva!\"")
        
        # Kimeneti fajl irasa
        with open(output_filename, 'w', encoding='utf-8') as output_file:
            for command in mikrotik_commands:
                output_file.write(command + '\n')
        
        print(f"Spamhaus atalakitas befejezve! {processed_count} IP cim atalakitva.")
        print(f"MikroTik parancsok mentve: {output_filename}")
        return output_filename
        
    except FileNotFoundError:
        print(f"Hiba: A fajl nem talalhato: {input_filename}")
        return None
    except Exception as e:
        print(f"Varatlan hiba a Spamhaus atalakitas soran: {e}")
        return None

def convert_dshield_to_mikrotik(input_data, output_filename="dshield_block.rsc"):
    """
    Atalakitja a DShield Block lista IP cimeket MikroTik RouterOS parancsokka.
    
    Args:
        input_data (str): A bemeneti adatok (DShield Block format string)
        output_filename (str): A kimeneti fajl neve (alapertelmezett: dshield_block.rsc)
    
    Returns:
        str: A MikroTik parancsok stringje
    """
    try:
        # Fix fajlnev hasznalata
        output_filename = "dshield_block.rsc"
        
        print(f"DShield atalakitas indul...")
        
        # Bemeneti adatok feldolgozása
        lines = input_data.strip().split('\n')
        
        # MikroTik parancsok generalasa kötegelt feldolgozással
        mikrotik_commands = []
        processed_count = 0
        batch_size = 50  # 50 IP címenként kötegek
        
        # Script fejlec hozzáadása
        mikrotik_commands.append("# DShield Block Lista - Automatikusan generalt MikroTik script")
        mikrotik_commands.append("# feeds.dshield.org/block.txt alapjan")
        mikrotik_commands.append("# Kotegelt feldolgozas 50 IP cimenkent 30 masodperc szunettel")
        mikrotik_commands.append("")
        mikrotik_commands.append(":log info \"DShield Block lista betoltese megkezdve...\"")
        mikrotik_commands.append("")
        
        batch_count = 0
        for line in lines:
            line = line.strip()
            # Komment sorok és üres sorok kihagyása
            if line and not line.startswith('#') and not line.startswith('Start'):
                # Tab-okkal elválasztott oszlopok feldolgozása
                parts = line.split('\t')
                if len(parts) >= 3:
                    try:
                        # 1. oszlop: kezdő IP, 3. oszlop: netmask
                        start_ip = parts[0].strip()
                        netmask = parts[2].strip()
                        
                        # CIDR formátum összeállítása
                        if start_ip and netmask and netmask.isdigit():
                            cidr_network = f"{start_ip}/{netmask}"
                            
                            # Köteg kezdete jelölés
                            if processed_count % batch_size == 0 and processed_count > 0:
                                batch_count += 1
                                mikrotik_commands.append("")
                                mikrotik_commands.append(f":log info \"Koteg {batch_count} feldolgozasa befejezve, 30 masodperc szunet...\"")
                                mikrotik_commands.append(":delay 30")
                                mikrotik_commands.append(f":log info \"Koteg {batch_count + 1} feldolgozasa kezdodik...\"")
                                mikrotik_commands.append("")
                            
                            mikrotik_command = f"/ip firewall address-list add list=DSHIELD_BLOCK address={cidr_network}"
                            mikrotik_commands.append(mikrotik_command)
                            processed_count += 1
                    except (IndexError, ValueError):
                        # Hibás sor kihagyása
                        continue
        
        # Script lábléc hozzáadása
        mikrotik_commands.append("")
        mikrotik_commands.append(f":log info \"DShield Block lista betoltese befejezve. Osszes IP cim: {processed_count}\"")
        mikrotik_commands.append(":log info \"Kotegelt feldolgozas sikeresen vegrehajtva!\"")
        
        print(f"DShield atalakitas befejezve! {processed_count} IP cim atalakitva.")
        
        # Visszatérés a parancsok stringjével
        return '\n'.join(mikrotik_commands)
        
    except Exception as e:
        print(f"Varatlan hiba a DShield atalakitas soran: {e}")
        return None

# Flask szerver inicializalasa
app = Flask(__name__)

# Globalis valtozok
MIKROTIK_FILE = "hu_ip_list.rsc"
SPAMHAUS_FILE = "spamhaus_drop.rsc"
DSHIELD_FILE = "dshield_block.rsc"
LAST_UPDATE = None
LAST_SPAMHAUS_UPDATE = None
LAST_DSHIELD_UPDATE = None

def update_ip_list():
    """Frissiti az IP listat es atalakitja MikroTik parancsokka"""
    global LAST_UPDATE
    
    print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - IP lista frissitese...")
    
    try:
        # Letoltes
        downloaded_file = download_file_as_text(URL)
        
        if downloaded_file:
            # Atalakitas
            mikrotik_file = convert_to_mikrotik_commands(downloaded_file, MIKROTIK_FILE)
            
            if mikrotik_file:
                # Eredeti fajl torlese
                try:
                    os.remove(downloaded_file)
                    print(f"Ideiglenes fajl torolve: {downloaded_file}")
                except:
                    pass
                
                LAST_UPDATE = datetime.now()
                print(f"IP lista sikeresen frissitve: {MIKROTIK_FILE}")
                return True
            else:
                print("Hiba az atalakitas soran!")
                return False
        else:
            print("Hiba a letoltes soran!")
            return False
            
    except Exception as e:
        print(f"Varatlan hiba a frissites soran: {e}")
        return False

def update_dshield_list():
    """DShield Block lista frissítése"""
    global LAST_DSHIELD_UPDATE
    
    print(f"DShield Block lista frissítése: {datetime.now()}")
    
    try:
        response = requests.get(DSHIELD_URL, timeout=30)
        response.raise_for_status()
        
        with open(DSHIELD_FILE, 'w', encoding='utf-8') as f:
            f.write(convert_dshield_to_mikrotik(response.text))
        
        LAST_DSHIELD_UPDATE = datetime.now()
        print(f"DShield Block lista sikeresen frissítve: {LAST_DSHIELD_UPDATE}")
        
    except requests.RequestException as e:
        print(f"Hiba a DShield Block lista letöltésekor: {e}")
    except Exception as e:
        print(f"Általános hiba a DShield Block lista frissítésekor: {e}")

def update_spamhaus_list():
    """Frissiti a Spamhaus DROP listat es atalakitja MikroTik parancsokka"""
    global LAST_SPAMHAUS_UPDATE
    
    print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Spamhaus DROP lista frissitese...")
    
    try:
        # Letoltes
        downloaded_file = download_file_as_text(SPAMHAUS_URL)
        
        if downloaded_file:
            # Atalakitas
            spamhaus_file = convert_spamhaus_to_mikrotik(downloaded_file, SPAMHAUS_FILE)
            
            if spamhaus_file:
                # Eredeti fajl torlese
                try:
                    os.remove(downloaded_file)
                    print(f"Ideiglenes fajl torolve: {downloaded_file}")
                except:
                    pass
                
                LAST_SPAMHAUS_UPDATE = datetime.now()
                print(f"Spamhaus lista sikeresen frissitve: {SPAMHAUS_FILE}")
                return True
            else:
                print("Hiba a Spamhaus atalakitas soran!")
                return False
        else:
            print("Hiba a Spamhaus letoltes soran!")
            return False
            
    except Exception as e:
        print(f"Varatlan hiba a Spamhaus frissites soran: {e}")
        return False

@app.route('/hu_ip_list.rsc')
def serve_ip_list():
    """Szolgaltatja a MikroTik IP listat"""
    try:
        if os.path.exists(MIKROTIK_FILE):
            return send_file(MIKROTIK_FILE, as_attachment=True, download_name='hu_ip_list.rsc')
        else:
            return "IP lista nem talalhato!", 404
    except Exception as e:
        return f"Hiba: {e}", 500

@app.route('/dshield_block.rsc')
def get_dshield_file():
    """DShield Block lista fájl letöltése"""
    try:
        return send_file(DSHIELD_FILE, as_attachment=True, download_name="dshield_block.rsc")
    except FileNotFoundError:
        return "A DShield Block lista fájl még nem lett generálva. Kérjük, indítsa el a frissítést.", 404

@app.route('/spamhaus_drop.rsc')
def serve_spamhaus_list():
    """Szolgaltatja a Spamhaus DROP listat"""
    try:
        if os.path.exists(SPAMHAUS_FILE):
            return send_file(SPAMHAUS_FILE, as_attachment=True, download_name='spamhaus_drop.rsc')
        else:
            return "Spamhaus lista nem talalhato!", 404
    except Exception as e:
        return f"Hiba: {e}", 500

@app.route('/status')
def status():
    """Status informacio JSON formatumban"""
    global LAST_UPDATE, LAST_SPAMHAUS_UPDATE, LAST_DSHIELD_UPDATE
    
    # Magyar IP lista adatok
    hu_file_exists = os.path.exists(MIKROTIK_FILE)
    hu_file_size = os.path.getsize(MIKROTIK_FILE) if hu_file_exists else 0
    hu_ip_count = 0
    if hu_file_exists:
        try:
            with open(MIKROTIK_FILE, 'r', encoding='utf-8') as f:
                hu_ip_count = len([line for line in f.readlines() if line.strip() and line.strip().startswith('/ip firewall')])
        except:
            pass
    
    # Spamhaus lista adatok
    spamhaus_file_exists = os.path.exists(SPAMHAUS_FILE)
    spamhaus_file_size = os.path.getsize(SPAMHAUS_FILE) if spamhaus_file_exists else 0
    spamhaus_ip_count = 0
    if spamhaus_file_exists:
        try:
            with open(SPAMHAUS_FILE, 'r', encoding='utf-8') as f:
                spamhaus_ip_count = len([line for line in f.readlines() if line.strip() and line.strip().startswith('/ip firewall')])
        except:
            pass
    
    # DShield lista adatok
    dshield_file_exists = os.path.exists(DSHIELD_FILE)
    dshield_file_size = os.path.getsize(DSHIELD_FILE) if dshield_file_exists else 0
    dshield_ip_count = 0
    if dshield_file_exists:
        try:
            with open(DSHIELD_FILE, 'r', encoding='utf-8') as f:
                dshield_ip_count = len([line for line in f.readlines() if line.strip() and line.strip().startswith('/ip firewall')])
        except:
            pass
    
    return jsonify({
        'hungarian_ips': {
            'file_exists': hu_file_exists,
            'file_size': hu_file_size,
            'ip_count': hu_ip_count,
            'last_update': LAST_UPDATE.strftime('%Y-%m-%d %H:%M:%S') if LAST_UPDATE else 'Soha',
            'filename': MIKROTIK_FILE
        },
        'spamhaus_drop': {
            'file_exists': spamhaus_file_exists,
            'file_size': spamhaus_file_size,
            'ip_count': spamhaus_ip_count,
            'last_update': LAST_SPAMHAUS_UPDATE.strftime('%Y-%m-%d %H:%M:%S') if LAST_SPAMHAUS_UPDATE else 'Soha',
            'filename': SPAMHAUS_FILE
        },
        'dshield_block': {
            'file_exists': dshield_file_exists,
            'file_size': dshield_file_size,
            'ip_count': dshield_ip_count,
            'last_update': LAST_DSHIELD_UPDATE.strftime('%Y-%m-%d %H:%M:%S') if LAST_DSHIELD_UPDATE else 'Soha',
            'filename': DSHIELD_FILE
        },
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/')
def index():
    """Egyszeru fooldal"""
    global LAST_UPDATE, LAST_SPAMHAUS_UPDATE, LAST_DSHIELD_UPDATE
    
    # Magyar IP lista adatok
    hu_status_info = ""
    if os.path.exists(MIKROTIK_FILE):
        hu_file_size = os.path.getsize(MIKROTIK_FILE)
        with open(MIKROTIK_FILE, 'r', encoding='utf-8') as f:
            hu_ip_count = len([line for line in f.readlines() if line.strip() and line.strip().startswith('/ip firewall')])
        
        hu_status_info = f"""
        <h3>Magyar IP Lista</h3>
        <p><strong>Fajl allapot:</strong> ✅ Elerheto</p>
        <p><strong>Fajl meret:</strong> {hu_file_size} byte</p>
        <p><strong>IP cimek szama:</strong> {hu_ip_count}</p>
        <p><strong>Utolso frissites:</strong> {LAST_UPDATE.strftime('%Y-%m-%d %H:%M:%S') if LAST_UPDATE else 'Soha'}</p>
        <p><a href="/hu_ip_list.rsc">Magyar IP lista letoltese</a></p>
        """
    else:
        hu_status_info = "<h3>Magyar IP Lista</h3><p><strong>Fajl allapot:</strong> ❌ Nem elerheto</p>"
    
    # Spamhaus DROP lista adatok
    spamhaus_status_info = ""
    if os.path.exists(SPAMHAUS_FILE):
        spamhaus_file_size = os.path.getsize(SPAMHAUS_FILE)
        with open(SPAMHAUS_FILE, 'r', encoding='utf-8') as f:
            spamhaus_ip_count = len([line for line in f.readlines() if line.strip() and line.strip().startswith('/ip firewall')])
        
        spamhaus_status_info = f"""
        <h3>Spamhaus DROP Lista</h3>
        <p><strong>Fajl allapot:</strong> ✅ Elerheto</p>
        <p><strong>Fajl meret:</strong> {spamhaus_file_size} byte</p>
        <p><strong>IP cimek szama:</strong> {spamhaus_ip_count}</p>
        <p><strong>Utolso frissites:</strong> {LAST_SPAMHAUS_UPDATE.strftime('%Y-%m-%d %H:%M:%S') if LAST_SPAMHAUS_UPDATE else 'Soha'}</p>
        <p><a href="/spamhaus_drop.rsc">Spamhaus DROP lista letoltese</a></p>
        """
    else:
        spamhaus_status_info = "<h3>Spamhaus DROP Lista</h3><p><strong>Fajl allapot:</strong> ❌ Nem elerheto</p>"
    
    # DShield Block lista adatok
    dshield_status_info = ""
    if os.path.exists(DSHIELD_FILE):
        dshield_file_size = os.path.getsize(DSHIELD_FILE)
        with open(DSHIELD_FILE, 'r', encoding='utf-8') as f:
            dshield_ip_count = len([line for line in f.readlines() if line.strip() and line.strip().startswith('/ip firewall')])
        
        dshield_status_info = f"""
        <h3>DShield Block Lista</h3>
        <p><strong>Fajl allapot:</strong> ✅ Elerheto</p>
        <p><strong>Fajl meret:</strong> {dshield_file_size} byte</p>
        <p><strong>IP cimek szama:</strong> {dshield_ip_count}</p>
        <p><strong>Utolso frissites:</strong> {LAST_DSHIELD_UPDATE.strftime('%Y-%m-%d %H:%M:%S') if LAST_DSHIELD_UPDATE else 'Soha'}</p>
        <p><a href="/dshield_block.rsc">DShield Block lista letoltese</a></p>
        """
    else:
        dshield_status_info = "<h3>DShield Block Lista</h3><p><strong>Fajl allapot:</strong> ❌ Nem elerheto</p>"
    
    return f"""
    <html>
    <head><title>IP Biztonsagi Lista Szerver</title></head>
    <body>
        <h1>IP Biztonsagi Lista Szerver</h1>
        <p><em>Harom kulonbozo forrásból származó IP listák MikroTik RouterOS számára</em></p>
        {hu_status_info}
        <hr>
        {spamhaus_status_info}
        <hr>
        {dshield_status_info}
        <hr>
        <p><a href="/status">JSON status</a></p>
        <hr>
        <p><em>Automatikus frissites naponta egyszer</em></p>
        <h3>Hasznalat MikroTik RouterOS-ben:</h3>
        <ul>
            <li><strong>Magyar IP-k engedélyezése:</strong> HU_IP lista használata</li>
            <li><strong>Spam IP-k blokkolása:</strong> SPAMHAUS_DROP lista használata</li>
            <li><strong>Tamadó IP-k blokkolása:</strong> DSHIELD_BLOCK lista használata</li>
        </ul>
    </body>
    </html>
    """

def schedule_updates():
    """Utemezi a napi frissiteseket"""
    # Naponta 2:00-kor frissit mindharom listat
    schedule.every().day.at("02:00").do(update_ip_list)
    schedule.every().day.at("02:15").do(update_spamhaus_list)  # 15 perccel késleltetett indítás
    schedule.every().day.at("02:30").do(update_dshield_list)   # 30 perccel késleltetett indítás
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Ellenorzés percenként

def main():
    """Foprogram - Flask szerver inditasa utemezett frissitesekkel"""
    print("=== IP Biztonsagi Lista Szerver ===")
    
    # Elso frissites inditaskor mindharom listara
    print("Kezdeti IP lista frissitese...")
    update_ip_list()
    print("Kezdeti Spamhaus DROP lista frissitese...")
    update_spamhaus_list()
    print("Kezdeti DShield Block lista frissitese...")
    update_dshield_list()
    
    # Utemezett frissitesek inditasa hatterben
    scheduler_thread = threading.Thread(target=schedule_updates, daemon=True)
    scheduler_thread.start()
    print("Utemezett frissitesek beallitva:")
    print("  - Magyar IP lista: naponta 2:00-kor")
    print("  - Spamhaus DROP lista: naponta 2:15-kor")
    print("  - DShield Block lista: naponta 2:30-kor")
    
    # Flask szerver inditasa
    print("Flask szerver inditasa...")
    print("Szerver port: 5000")
    print("Szerver mindenhonnan elerheto (0.0.0.0)")
    print("")
    
    # Elerheto IP cimek megjelenitse
    ip_addresses = get_local_ip_addresses()
    print("Elerheto URL-ek:")
    
    for ip in ip_addresses:
        print(f"  - http://{ip}:5000/")
        print(f"  - http://{ip}:5000/hu_ip_list.rsc (Magyar IP lista)")
        print(f"  - http://{ip}:5000/spamhaus_drop.rsc (Spamhaus DROP lista)")
        print(f"  - http://{ip}:5000/dshield_block.rsc (DShield Block lista)")
        print(f"  - http://{ip}:5000/status")
        print("")
    
    print("FONTOS: Halozati tuzfalon keresztuli elereseshez:")
    print("  - Engedjelyezze a 5000-es portot a Windows tuzfalban")
    print("  - Router-ben allitson be port forwardingot ha szukseges")
    print("")
    print("MIKROTIK ROUTER HASZNALAT:")
    print("  - Magyar IP-k: HU_IP address list")
    print("  - Spamhaus DROP: SPAMHAUS_DROP address list")
    print("  - DShield Block: DSHIELD_BLOCK address list")
    print("")
    print("A szerver leallitasahoz nyomja meg a Ctrl+C kombinaciot")
    
    try:
        # Fejlesztői szerver figyelmeztetés elrejtése
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nSzerver leallitasa...")
    except Exception as e:
        print(f"Hiba a szerver inditasakor: {e}")

if __name__ == "__main__":
    main()