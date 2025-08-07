# Network Access Configuration

## Windows Firewall Settings

### 1. Windows Defender Firewall Configuration

#### Command Line Method (as Administrator):
```cmd
# Add inbound rule
netsh advfirewall firewall add rule name="Hungarian IP List Server" dir=in action=allow protocol=TCP localport=5000

# Add outbound rule (optional)
netsh advfirewall firewall add rule name="Hungarian IP List Server OUT" dir=out action=allow protocol=TCP localport=5000
```

#### Graphical Method:
1. Open **Windows Defender Firewall with Advanced Security**
2. Click **Inbound Rules**
3. Click **New Rule...**
4. Select **Port** option -> **Next**
5. Select **TCP** -> **Specific Local Ports** -> enter: `5000`
6. Select **Allow the connection** -> **Next**
7. Check all network profiles (Domain, Private, Public)
8. Give a name to the rule: "Hungarian IP List Server"

### 2. PowerShell Command Line Method:
```powershell
# Inbound rule
New-NetFirewallRule -DisplayName "Hungarian IP List Server" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow

# List display
Get-NetFirewallRule -DisplayName "Hungarian IP List Server"
```

## Router Settings (if needed)

### Port Forwarding Configuration:

If you want to access the server from outside the local network:

1. Log in to the router admin interface (usually 192.168.1.1 or 192.168.0.1)
2. Find the **Port Forwarding** or **Virtual Server** menu
3. Add a new rule:
   - **Service Name**: Hungarian IP List
   - **External Port**: 5000
   - **Internal Port**: 5000
   - **Internal IP**: [server machine IP address]
   - **Protocol**: TCP

### Dynamic DNS (optional):

If you don't have a static IP address, you can use dynamic DNS service:
- No-IP (https://www.noip.com)
- DuckDNS (https://www.duckdns.org)
- DynDNS (https://dyn.com)

## Security Notes

⚠️ **WARNING**: If you make the server publicly accessible:

1. **Use strong passwords** for all network devices
2. **Update regularly** the operating system
3. **Monitor network traffic**
4. **Use VPN** if possible
5. **Limit access** only to necessary IP addresses

## Testing

### On local network:
```bash
# From Windows
curl http://192.168.1.100:5000/status

# Or in browser:
http://192.168.1.100:5000/
```

### From MikroTik RouterOS:
```
/tool fetch url=http://192.168.1.100:5000/hu_ip_list.rsc dst-path="hu_ip_list.rsc"
```

## Troubleshooting

### Server not accessible remotely:

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

### Common issues:

- **Port occupied**: Change port to 5001 or 8080
- **IP address change**: Use static IP or dynamic DNS
- **ISP blocking**: Some internet service providers block certain ports

## Useful Commands

### List active network connections:
```cmd
netstat -an | findstr :5000
```

### List network interfaces:
```cmd
ipconfig /all
```

### Accessibility testing:
```cmd
# Local testing
curl http://localhost:5000/status

# Remote testing
curl http://[server-ip]:5000/status
```

## Linux Service Configuration

### Installing as systemd service:

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

### Linux Firewall Configuration:

#### UFW (Ubuntu):
```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

#### firewalld (CentOS/RHEL):
```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

#### iptables:
```bash
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

### Service Management Commands:

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
