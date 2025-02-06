# Smart Lighting Control System
An intelligent IoT-based lighting control system featuring automated scheduling, remote management, and safety features. Built with MicroPython (ESP32/8266) and Python (Desktop GUI).

## Table of Contents
- [Key Features](#key-features)
- [Hardware Requirements](#hardware-requirements)
- [Wiring Diagram](#wiring-diagram)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Safety Considerations](#safety-considerations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Key Features

### Microcontroller (ESP32/ESP8266)
- **WiFi Connectivity**: Dual-mode (STA + AP) with automatic fallback
- **Smart Scheduling**: Weekly programming with overnight support
- **Safety Protocols**: 
  - **12-hour maximum runtime limiter**
  - **Thermal overload protection simulation**
  - **Watchdog timer** for system recovery
- **REST API**: Secure endpoints for control/monitoring
- **OTA Updates**: Secure firmware updates with rollback
- **Energy Monitoring**: Current sensing capability (optional)
- **Time Management**: NTP sync with DST awareness

### Desktop Application
- **Cross-platform GUI**: Windows/macOS/Linux support
- **Device Discovery**: Automatic network detection via mDNS
- **Visual Programming**: Drag-and-drop schedule builder
- **Real-time Monitoring**: Energy usage dashboard
- **Preset Modes**: Vacation/Random/Party configurations
- **Security**: AES-256 encrypted communications
- **Multi-device Management**: Control multiple units simultaneously

## Hardware Requirements

### Essential Components
| Component | Specification |
|-----------|---------------|
| Microcontroller | ESP32 or ESP8266 |
| Relay Module | 5V/10A Optoisolated |
| Power Supply | 5V 2A (For ESP + Relays) |
| Level Shifter | 3.3V-5V (If using 5V relays) |

### Optional Components
- DS18B20 Temperature Sensor
- ACS712 Current Sensor
- Motion Sensor (PIR)
- Ambient Light Sensor

## Wiring Diagram

```plaintext
ESP32/8266 Wiring:
===================
        ┌───────────────┐
        │   ESP32       │
        │               │
GPIO12  ├──▶Relay IN1   │
3.3V    ├──▶Relay VCC   │
GND     ├──▶Relay GND   │
        │               │
        └───────────────┘

Safety Features:
- 1N4007 Flyback Diode across relay coil
- 220Ω Resistor in series with GPIO
- MOV (Metal Oxide Varistor) at power input
```

## Installation

### Microcontroller Setup
**Flash MicroPython:**
```bash
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 firmware.bin
```

**Upload System Files:**
```bash
ampy -p /dev/ttyUSB0 put main.py
ampy -p /dev/ttyUSB0 put config.json
```

**Required Libraries:**
```bash
mpremote mip install umqtt.simple urequests ucryptolib
```

### Desktop Application
**Install Dependencies:**
```bash
pip install -r requirements.txt
```
*requirements.txt:*
```
pyqt5==5.15.9
qasync==0.23.0
zeroconf==0.38.7
aiohttp==3.8.4
```

**Run Application:**
```bash
python lighting_app.py
```

## Configuration

### Microcontroller
**Edit `config.json`:**
```json
{
  "wifi": {
    "ssid": "YOUR_NETWORK",
    "password": "YOUR_PASSWORD"
  },
  "ntp_server": "pool.ntp.org",
  "timezone": "Europe/Paris",
  "api_key": "GENERATE_SECURE_KEY"
}
```

**Initial Setup:**
- Connect to **LightCtrl-XXXX** AP (Password: **Setup1234**)
- Access web interface at `192.168.4.1`

### Desktop App
- **First Run Wizard**: Automatic device discovery + manual IP entry fallback
- **Security Settings**: Enable TLS encryption + admin password configuration

## Usage

### Basic Operations
- **Schedule Programming**: Drag time blocks on weekly calendar
- **Manual Control**: Temporary override (15-240 mins)
- **Energy Monitoring**: Real-time power consumption reports

### Advanced Features
- **Vacation Mode**: Random activation patterns
- **Group Control**: Sync multiple devices
- **API Integration**:
  ```bash
  curl -H "X-API-Key: YOUR_KEY" http://device-ip/status
  ```

## Safety Considerations

### Electrical Safety
- **Use proper enclosures** (IP-rated for outdoor)
- **Maintain 30cm separation** between AC/DC circuits

### Network Security
- **Change default API keys**
- Enable **HTTPS with Let's Encrypt**

### Thermal Management
- **Maximum ambient temperature**: 40°C
- Enable **thermal shutdown** in config

## Troubleshooting

| Issue                  | Solution                          |
|------------------------|-----------------------------------|
| No WiFi Connection     | Check AP mode at `192.168.4.1`    |
| Schedule Not Working   | Verify NTP sync status            |
| OTA Update Failed      | Ensure 2x free space of firmware  |


## License
This project is licensed under the MIT License.

**Documentation Version**: 2.1.0  
**Last Updated**: 2023-11-15  
**Project Maintainer**: Mohammad Amin Zakouri 

**Hardware Compatibility**: ESP32-WROOM, ESP8266-12F
