# Hungarian IP List Flask Server

A Flask-based web server that automatically updates the Hungarian IP block list and serves it to MikroTik routers in RouterOS command format.

## Requirements

- Python 3.6+
- flask library
- requests library
- schedule library

**Supported Operating Systems:**
- Windows (with detailed firewall setup)
- Linux (with systemd service integration)
- Any OS with Python 3.6+ support

## Installation

1. Clone or download the project:
   ```bash
   git clone https://github.com/kovtom/magyar-ip-lista-server.git
   cd magyar-ip-lista-server
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Or individually:
   ```bash
   pip install flask requests schedule
   ```

## Usage

### Starting the server:
```bash
python hulista.py
```

The server automatically:
1. Downloads and updates the IP list on startup
2. Starts a Flask web server on port 5000
3. Schedules daily updates (every day at 2:00 AM)

### Available URLs:

- **http://localhost:5000/** - Main page with status information
- **http://localhost:5000/hu_ip_list.txt** - Download MikroTik commands
- **http://localhost:5000/status** - JSON status information

## MikroTik Configuration

### 1. Script Installation:

1. Open MikroTik RouterOS WebFig or WinBox interface
2. Navigate to **System > Scripts** menu
3. Create a new script named **"HU_IP_Update"**
4. Copy the content of `mikrotik_update_script.rsc` file
5. **Modify the SERVER_URL variable** to your server's IP address:
   ```
   :local SERVER_URL "http://192.168.1.100:5000/hu_ip_list.txt"
   ```

### 2. Scheduled Execution Setup:

1. Navigate to **System > Scheduler** menu
2. Create a new task:
   - **Name:** HU_IP_Daily_Update
   - **Start Date:** today
   - **Start Time:** 03:00:00
   - **Interval:** 1d 00:00:00
   - **On Event:** HU_IP_Update

### 3. First Run (Test):

You can run the script manually in **System > Scripts** menu using the **Run Script** button.

## Features

### Flask Server:
- **Automatic updates**: Updates IP list daily at 2:00 AM
- **Web interface**: Status can be checked from browser
- **JSON API**: For programmatic access
- **Fixed filename**: Always `hu_ip_list.txt` (no need to change in MikroTik)

### MikroTik Script:
- **Automatic download**: Using HTTP GET requests
- **List refresh**: Removes old, loads new list
- **Error handling**: Detailed logging and error checking
- **Statistics**: Reports number of processed items

## Security Benefits

✅ **No passwords needed**: MikroTik pulls updates via HTTP  
✅ **Automatic**: No manual intervention required  
✅ **Centralized**: One server serves all routers  
✅ **Logged**: All operations are logged  

## Output Files

- **hu_ip_list.txt** - MikroTik commands (fixed name, constantly updated)

## Example Output

```
/ip firewall address-list add list=HU_IP address=2.58.168.0/22
/ip firewall address-list add list=HU_IP address=2.59.196.0/22
/ip firewall address-list add list=HU_IP address=5.28.0.0/21
...
```

## Network Configuration

### Windows Firewall Settings

#### 1. Windows Defender Firewall Configuration

**Command Line Method (as Administrator):**
```cmd
# Add inbound rule
netsh advfirewall firewall add rule name="Hungarian IP List Server" dir=in action=allow protocol=TCP localport=5000

# Add outbound rule (optional)
netsh advfirewall firewall add rule name="Hungarian IP List Server OUT" dir=out action=allow protocol=TCP localport=5000
```

**Graphical Method:**
1. Open **Windows Defender Firewall with Advanced Security**
2. Click **Inbound Rules**
3. Click **New Rule...**
4. Select **Port** option -> **Next**
5. Select **TCP** -> **Specific Local Ports** -> enter: `5000`
6. Select **Allow the connection** -> **Next**
7. Check all network profiles (Domain, Private, Public)
8. Give a name to the rule: "Hungarian IP List Server"

#### 2. PowerShell Command Line Method:
```powershell
# Inbound rule
New-NetFirewallRule -DisplayName "Hungarian IP List Server" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow

# List display
Get-NetFirewallRule -DisplayName "Hungarian IP List Server"
```

### Router Settings (if needed)

#### Port Forwarding Configuration:

If you want to access the server from outside the local network:

1. Log in to the router admin interface (usually 192.168.1.1 or 192.168.0.1)
2. Find the **Port Forwarding** or **Virtual Server** menu
3. Add a new rule:
   - **Service Name**: Hungarian IP List
   - **External Port**: 5000
   - **Internal Port**: 5000
   - **Internal IP**: [server machine IP address]
   - **Protocol**: TCP

#### Dynamic DNS (optional):

If you don't have a static IP address, you can use dynamic DNS service:
- No-IP (https://www.noip.com)
- DuckDNS (https://www.duckdns.org)
- DynDNS (https://dyn.com)

### Linux Service Configuration

#### Installing as systemd service:

1. **Create service file**:
   ```bash
   sudo nano /etc/systemd/system/hulista.service
   ```

2. **Service file content**:
   ```ini
   [Unit]
   Description=Hungarian IP List Flask Server
   After=network.target
   Wants=network.target

   [Service]
   Type=simple
   User=hulista
   Group=hulista
   WorkingDirectory=/opt/hulista
   ExecStart=/usr/bin/python3 /opt/hulista/hulista.py
   Restart=always
   RestartSec=10
   Environment=PYTHONUNBUFFERED=1

   [Install]
   WantedBy=multi-user.target
   ```

3. **Create user and directory**:
   ```bash
   sudo useradd -r -s /bin/false hulista
   sudo mkdir -p /opt/hulista
   sudo cp -r * /opt/hulista/
   sudo chown -R hulista:hulista /opt/hulista
   ```

4. **Install Python dependencies**:
   ```bash
   cd /opt/hulista
   sudo pip3 install -r requirements.txt
   ```

5. **Enable and start service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable hulista.service
   sudo systemctl start hulista.service
   ```

6. **Check service status**:
   ```bash
   sudo systemctl status hulista.service
   sudo journalctl -u hulista.service -f
   ```

#### Linux Firewall Configuration:

**UFW (Ubuntu):**
```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

**firewalld (CentOS/RHEL):**
```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

**iptables:**
```bash
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

#### Service Management Commands:

```bash
# Start service
sudo systemctl start hulista.service

# Stop service
sudo systemctl stop hulista.service

# Restart service
sudo systemctl restart hulista.service

# View logs
sudo journalctl -u hulista.service

# View real-time logs
sudo journalctl -u hulista.service -f

# Check if service is running
sudo systemctl is-active hulista.service
```

### Security Notes

⚠️ **WARNING**: If you make the server publicly accessible:

1. **Use strong passwords** for all network devices
2. **Update regularly** the operating system
3. **Monitor network traffic**
4. **Use VPN** if possible
5. **Limit access** only to necessary IP addresses

### Testing Network Configuration

#### On local network:
```bash
# From Windows
curl http://192.168.1.100:5000/status

# Or in browser:
http://192.168.1.100:5000/
```

#### From MikroTik RouterOS:
```
/tool fetch url=http://192.168.1.100:5000/hu_ip_list.txt
```

#### Useful Commands:

**Windows:**
```cmd
# List active network connections
netstat -an | findstr :5000

# List network interfaces
ipconfig /all

# Local testing
curl http://localhost:5000/status

# Remote testing
curl http://[server-ip]:5000/status
```

**Linux:**
```bash
# List active network connections
netstat -an | grep :5000

# List network interfaces
ip addr show

# Local testing
curl http://localhost:5000/status

# Remote testing
curl http://[server-ip]:5000/status
```

## Troubleshooting

### Server won't start:
- Check if port 5000 is available
- Install missing libraries

### MikroTik won't download:
- Check network connectivity
- Ensure SERVER_URL is correct
- Check MikroTik log files

### List doesn't update:
- Check server log output
- Ensure source URL is accessible

### Network Access Issues:

#### Server not accessible remotely:

1. **Check Windows firewall**:
   ```cmd
   netsh advfirewall firewall show rule name="Hungarian IP List Server"
   ```

2. **Test port locally**:
   ```cmd
   telnet localhost 5000
   ```

3. **Check network connection**:
   ```cmd
   ping 192.168.1.100
   ```

4. **Check router settings**

#### Common network issues:

- **Port occupied**: Change port to 5001 or 8080
- **IP address change**: Use static IP or dynamic DNS
- **ISP blocking**: Some internet service providers block certain ports

## Files in Project

- **hulista.py** - Flask server main program
- **mikrotik_update_script.rsc** - MikroTik RouterOS script
- **hu_ip_list.txt** - Generated MikroTik commands (automatically updated)
- **README.md** - This comprehensive documentation (English)
- **README_hu.md** - Hungarian documentation
- **network_setup.md** - Network configuration guide (English) *[deprecated - content merged into README.md]*
- **network_setup_hu.md** - Network configuration guide (Hungarian)

## Language Support

- 🇬🇧 **English**: README.md, network_setup.md
- 🇭🇺 **Magyar**: README_hu.md, network_setup_hu.md

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
