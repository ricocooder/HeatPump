# HeatPump Control System

FastAPI-based control dashboard for a residential heat pump system running on Raspberry Pi.
Monitors temperatures, controls pump efficiency, manages heating schedules, and provides a real-time web dashboard.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    HEAT SOURCES                                  │
│                                                                  │
│   ┌──────────────────┐      ┌──────────────────┐                │
│   │  POMPA CIEPŁA    │      │      PIEC         │                │
│   │  (Heat Pump)     │      │   (Gas Boiler)    │                │
│   └────────┬─────────┘      └────────┬──────────┘                │
│            └──────────┬─────────────┘                            │
│                       ▼                                          │
│           ┌───────────────────────┐                              │
│           │   ZAWÓR 3-DROGOWY     │                              │
│           │  (3-Way Valve)        │                              │
│           └──────┬──────────┬─────┘                              │
│                  │          │                                    │
│           ┌──────▼───┐  ┌───▼──────────────────────┐            │
│           │  BOJLER   │  │  ZAWÓR MIESZAJĄCY        │            │
│           │ (Boiler)  │  │  (Mixing Valve)          │            │
│           └──────────┘  └───────────┬───────────────┘            │
│                                     ▼                            │
│                          ┌──────────────────┐                   │
│                          │   PODŁOGÓWKA     │                   │
│                          │ (Floor Heating)  │                   │
│                          └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Hardware — GPIO Pin Map

| GPIO (BCM) | Function                        | Direction |
|------------|---------------------------------|-----------|
| GPIO 17    | Pump relay 1                    | OUT       |
| GPIO 27    | Pump relay 2                    | OUT       |
| GPIO 22    | Pump relay 3                    | OUT       |
| GPIO 23    | Pump relay 4                    | OUT       |
| GPIO 5     | Pump relay 5                    | OUT       |
| GPIO 6     | Pump relay 6                    | OUT       |
| GPIO 13    | Pump relay 7                    | OUT       |
| GPIO 19    | Pump relay 8                    | OUT       |
| GPIO 16    | Pump efficiency bit 0 (LSB)     | OUT       |
| GPIO 20    | Pump efficiency bit 1           | OUT       |
| GPIO 21    | Pump efficiency bit 2 (MSB)     | OUT       |
| 1-Wire     | DS18B20 temperature sensors (up to 6) | IN   |
| SPI CE0    | MCP3008 ADC (current/voltage)   | SPI       |

**Pump efficiency encoding (NC logic — 0 = active):**

| Level | Bit2 | Bit1 | Bit0 |
|-------|------|------|------|
| 7     | 0    | 0    | 0    |
| 6     | 0    | 0    | 1    |
| 5     | 0    | 1    | 0    |
| 4     | 1    | 0    | 0    |
| 3     | 0    | 1    | 1    |
| 2     | 1    | 0    | 1    |
| 1     | 1    | 1    | 0    |
| 0     | 1    | 1    | 1    |

**Temperature sensors (DS18B20) — channel assignments:**

| Index | Sensor             |
|-------|--------------------|
| 0     | Temperatura zewnętrzna (outdoor) |
| 1     | Bojler (boiler)    |
| 2     | Podłogówka (floor) |
| 3     | Spare 1            |
| 4     | Spare 2            |
| 5     | Spare 3            |

**MCP3008 ADC channels:**

| ADC Channel | Measurement |
|-------------|-------------|
| CH6         | Current (prąd) |
| CH7         | Voltage (napięcie) |

---

## Raspberry Pi Setup — Fresh Installation

### 1. Flash the OS

Download **Raspberry Pi OS Lite (64-bit)** from https://www.raspberrypi.com/software/
Use **Raspberry Pi Imager** to flash to SD card.

In Imager advanced settings (gear icon), before flashing:
- Enable SSH
- Set username/password
- Set Wi-Fi SSID and password
- Set hostname (e.g. `heatpump`)

### 2. Boot and connect

```bash
# Find Pi on your network:
ping heatpump.local

# SSH in:
ssh pi@heatpump.local
```

### 3. Set a static IP address

Edit the DHCP client configuration:

```bash
sudo nano /etc/dhcpcd.conf
```

Add at the bottom (adjust to your network):

```
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 8.8.4.4
```

Save and reboot:

```bash
sudo reboot
```

### 4. Update the system

```bash
sudo apt update && sudo apt upgrade -y
```

### 5. Enable 1-Wire (DS18B20 sensors)

```bash
sudo nano /boot/config.txt
```

Add at the bottom:

```
dtoverlay=w1-gpio
```

Save, then reboot:

```bash
sudo reboot
```

After reboot, load the modules and verify sensors are detected:

```bash
sudo modprobe w1-gpio
sudo modprobe w1-therm

ls /sys/bus/w1/devices/
# Should show entries like: 28-00000674869d  28-0000067518ab  ...
```

Each `28-xxxxxxxxxxxx` entry is one DS18B20 sensor.

### 6. Enable SPI (MCP3008 ADC)

```bash
sudo raspi-config
```

Navigate to: **Interface Options → SPI → Enable**

Verify:

```bash
ls /dev/spidev*
# Should show: /dev/spidev0.0  /dev/spidev0.1
```

### 7. Install Python 3 and pip

```bash
sudo apt install -y python3 python3-pip python3-venv git
```

### 8. Install Adafruit libraries for MCP3008

```bash
pip3 install adafruit-circuitpython-mcp3xxx
```

Or into a virtualenv (recommended — see step 10).

### 9. Clone the project

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/HeatPump.git
cd HeatPump
```

### 10. Create virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
pip install adafruit-circuitpython-mcp3xxx RPi.GPIO
```

### 11. Create the database

The SQLite database is created automatically on first run. If you need to reset it:

```bash
rm -f myDB.db
```

It will be recreated with empty tables when the app starts.

### 12. Test run

```bash
source venv/bin/activate
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Open a browser and navigate to `http://heatpump.local:8000`

---

## Autostart with systemd

Create a service file:

```bash
sudo nano /etc/systemd/system/heatpump.service
```

Paste the following (adjust `User` and paths if needed):

```ini
[Unit]
Description=HeatPump Control System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/HeatPump
ExecStart=/home/pi/HeatPump/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5s
Environment=HEATPUMP_DB_PATH=/home/pi/HeatPump/myDB.db

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable heatpump
sudo systemctl start heatpump

# Check status:
sudo systemctl status heatpump

# View logs:
sudo journalctl -u heatpump -f
```

---

## Configuration

Settings are stored in `config.json` (created automatically on first run).
You can also modify settings through the web UI at `/settings`.

**config.json example:**

```json
{
  "set_temp": [0, 55.0, 35.0],
  "pump_interval": [0, 900, 600],
  "pump_temp_offset": [0, 3.0, 2.0],
  "sensor_index_list": [0, 1, 2, 3],
  "picked_lang": "pl",
  "sezon": "zima",
  "godzina": [...],
  "descriptions": ["", "Bojler", "Podłogówka"]
}
```

---

## Web Interface

| URL                    | Description                        |
|------------------------|------------------------------------|
| `/`                    | Live dashboard with SVG diagram    |
| `/stream`              | SSE stream (used by dashboard)     |
| `/history`             | Plotly charts — temperature, current, efficiency |
| `/api/data`            | JSON API for chart data            |
| `/settings`            | Temperature setpoints, intervals, amplitudes |
| `/harmonogram`         | Weekly heating schedule grid       |
| `/temp_sensor_config`  | Assign physical sensors to roles   |
| `/raspberrypi`         | System info, DB backup, language   |

---

## Project Structure

```
HeatPump/
├── app.py                    # FastAPI entry point, scheduler, lifespan
├── requirements.txt          # Python dependencies
├── config.json               # Persisted user settings (auto-created)
├── myDB.db                   # SQLite database (auto-created)
├── simulate_data.py          # Test data generator (dev only)
│
├── core/
│   ├── state.py              # Thread-safe AppState, constants
│   └── config_manager.py     # JSON config load/save
│
├── hardware/
│   ├── gpio_interface.py     # RPi.GPIO abstraction (real/mock)
│   ├── temp_sensor.py        # DS18B20 1-Wire reader
│   ├── adc_reader.py         # MCP3008 SPI ADC reader
│   └── set_outputs.py        # GPIO relay control, pump efficiency
│
├── services/
│   ├── pump_efi.py           # Pump efficiency control logic
│   ├── database.py           # SQLite read/write operations
│   ├── disk_space.py         # Disk usage reporting
│   └── map_value.py          # Value range mapping utility
│
├── routes/
│   ├── dashboard.py          # GET / — main dashboard
│   ├── stream.py             # GET /stream — SSE endpoint
│   ├── settings_route.py     # GET/POST /settings
│   ├── harmonogram_route.py  # GET/POST /harmonogram
│   ├── sensor_config.py      # GET/POST /temp_sensor_config
│   ├── raspberrypi_route.py  # GET/POST /raspberrypi
│   └── history_route.py      # GET /history + GET /api/data
│
├── templates/
│   ├── new_base.html         # Bootstrap 5 base with navbar
│   ├── new_index.html        # Dashboard with SVG + SSE
│   ├── new_history.html      # Plotly charts
│   ├── settings.html         # Settings form
│   ├── harmonogram.html      # Weekly schedule grid
│   ├── temp_sensor_config.html  # Sensor assignment
│   └── raspberrypi.html      # System settings
│
└── _archive/                 # Old Flask-based files (kept for reference)
```

---

## Database

The SQLite database stores time-series data in separate tables:

| Table  | Content                  |
|--------|--------------------------|
| temp1  | Sensor 1 temperature (°C) |
| temp2  | Sensor 2 temperature (°C) |
| temp3  | Sensor 3 temperature (°C) |
| temp4  | Sensor 4 temperature (°C) |
| temp5  | Sensor 5 temperature (°C) |
| cur    | Current (A)              |
| volt   | Voltage (V)              |
| efi    | Pump efficiency (0–7)    |

Each row: `(date TEXT, time TEXT, value REAL)`

**Clear all data:**

```bash
sqlite3 myDB.db
```

```sql
DELETE FROM temp1;
DELETE FROM temp2;
DELETE FROM temp3;
DELETE FROM temp4;
DELETE FROM temp5;
DELETE FROM cur;
DELETE FROM volt;
DELETE FROM efi;
.quit
```

**Backup database:**

Use the "Save DB" button on the `/raspberrypi` page, or manually:

```bash
cp myDB.db myDB_backup_$(date +%Y%m%d).db
```

---

## Development / Testing

Generate test data without a Raspberry Pi:

```bash
# Generate 24 hours of historical data:
python3 simulate_data.py --hours 24

# Live simulation (one point every 4 seconds):
python3 simulate_data.py --live

# Clear recent data and regenerate:
python3 simulate_data.py --clear --hours 12
```

The app automatically detects whether it is running on a Raspberry Pi
(by checking for `/sys/bus/w1/devices/`). On a dev machine, all GPIO
and sensor operations are replaced with mock implementations that log
to stdout — the web interface works fully without hardware.

---

## Troubleshooting

**Sensors not detected:**

```bash
# Check 1-Wire is enabled:
ls /sys/bus/w1/devices/

# Load modules manually:
sudo modprobe w1-gpio
sudo modprobe w1-therm

# Verify dtoverlay is in /boot/config.txt:
grep w1 /boot/config.txt
```

**App won't start — port in use:**

```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

**Database locked:**

```bash
sudo systemctl stop heatpump
fuser myDB.db
```

**Check service logs:**

```bash
sudo journalctl -u heatpump -n 100
```

**GPIO permission denied:**

```bash
sudo usermod -aG gpio pi
# Then log out and back in
```

---

## Dependencies

```
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
jinja2>=3.1.0
python-multipart>=0.0.9
apscheduler>=3.10.4
RPi.GPIO                    # Raspberry Pi only
adafruit-circuitpython-mcp3xxx  # Raspberry Pi only
```

Install all:

```bash
pip install -r requirements.txt
pip install RPi.GPIO adafruit-circuitpython-mcp3xxx  # on Pi only
```
