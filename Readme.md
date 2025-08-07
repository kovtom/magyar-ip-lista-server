# Hungarian IP List Flask Server

A Flask-based web server that automatically updates the Hungarian IP block list and serves it to MikroTik routers in RouterOS command format.

## Requirements

- Python 3.6+
- flask library
- requests library
- schedule library

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

For detailed network setup instructions including firewall configuration and remote access, see [network_setup.md](network_setup.md).

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

## Files in Project

- **hulista.py** - Flask server main program
- **mikrotik_update_script.rsc** - MikroTik RouterOS script
- **hu_ip_list.txt** - Generated MikroTik commands (automatically updated)
- **README.md** - This documentation (English)
- **README_hu.md** - Hungarian documentation
- **network_setup.md** - Network configuration guide (English)
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
