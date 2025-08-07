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

# Flask szerver inicializalasa
app = Flask(__name__)

# Globalis valtozok
MIKROTIK_FILE = "hu_ip_list.rsc"
LAST_UPDATE = None

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

@app.route('/status')
def status():
    """Status informacio JSON formatumban"""
    global LAST_UPDATE
    
    file_exists = os.path.exists(MIKROTIK_FILE)
    file_size = os.path.getsize(MIKROTIK_FILE) if file_exists else 0
    
    # IP cimek szamanak meghatarozasa
    ip_count = 0
    if file_exists:
        try:
            with open(MIKROTIK_FILE, 'r', encoding='utf-8') as f:
                ip_count = len(f.readlines())
        except:
            pass
    
    return jsonify({
        'file_exists': file_exists,
        'file_size': file_size,
        'ip_count': ip_count,
        'last_update': LAST_UPDATE.strftime('%Y-%m-%d %H:%M:%S') if LAST_UPDATE else 'Soha',
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/')
def index():
    """Egyszeru fooldal"""
    global LAST_UPDATE
    
    status_info = ""
    if os.path.exists(MIKROTIK_FILE):
        file_size = os.path.getsize(MIKROTIK_FILE)
        with open(MIKROTIK_FILE, 'r', encoding='utf-8') as f:
            ip_count = len(f.readlines())
        
        status_info = f"""
        <p><strong>Fajl allapot:</strong> ✅ Elerheto</p>
        <p><strong>Fajl meret:</strong> {file_size} byte</p>
        <p><strong>IP cimek szama:</strong> {ip_count}</p>
        <p><strong>Utolso frissites:</strong> {LAST_UPDATE.strftime('%Y-%m-%d %H:%M:%S') if LAST_UPDATE else 'Soha'}</p>
        <p><a href="/hu_ip_list.rsc">IP lista letoltese</a></p>
        """
    else:
        status_info = "<p><strong>Fajl allapot:</strong> ❌ Nem elerheto</p>"
    
    return f"""
    <html>
    <head><title>Magyar IP Lista Szerver</title></head>
    <body>
        <h1>Magyar IP Lista Szerver</h1>
        {status_info}
        <p><a href="/status">JSON status</a></p>
        <hr>
        <p><em>Automatikus frissites naponta egyszer</em></p>
    </body>
    </html>
    """

def schedule_updates():
    """Utemezi a napi frissiteseket"""
    # Naponta 2:00-kor frissit
    schedule.every().day.at("02:00").do(update_ip_list)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Ellenorzi minden percben

def main():
    """Foprogram - Flask szerver inditasa utemezett frissitesekkel"""
    print("=== Magyar IP Lista Flask Szerver ===")
    
    # Elso frissites inditaskor
    print("Kezdeti IP lista frissitese...")
    update_ip_list()
    
    # Utemezett frissitesek inditasa hatterben
    scheduler_thread = threading.Thread(target=schedule_updates, daemon=True)
    scheduler_thread.start()
    print("Utemezett frissitesek beallitva (naponta 2:00-kor)")
    
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
        print(f"  - http://{ip}:5000/hu_ip_list.rsc")
        print(f"  - http://{ip}:5000/status")
        print("")
    
    print("FONTOS: Halozati tuzfalon keresztuli elereseshez:")
    print("  - Engedjelyezze a 5000-es portot a Windows tuzfalban")
    print("  - Router-ben allitson be port forwardingot ha szukseges")
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