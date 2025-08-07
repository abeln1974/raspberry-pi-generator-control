# Raspberry Pi Generator Control Setup

## 1. Install required packages:
```bash
sudo apt update
sudo apt install python3-tk python3-pip
pip3 install requests
```

## 2. Configure USR-TCP232-410S:
- Open http://192.168.1.192 in browser
- Login with admin/admin
- Go to RS232 settings (`sernet1.shtml?0`)
- Set: **9600 baud, 8N1, TCP Server mode**
- Local Port: **8899**
- Save and reboot USR device

## 3. Physical connections:
```
Generator Controller DB9 ↔ USR-TCP232-410S serial port
USR device ↔ Ethernet to local network  
Raspberry Pi ↔ Same network (WiFi/Ethernet)
```

## 4. Test connection:
```bash
# Test if USR device is reachable
ping 192.168.1.192

# Test if serial port is working
telnet 192.168.1.192 8899
```

## 5. Run the application:
```bash
python3 raspberry_pi_generator_control.py
```

## 6. For autostart on Pi boot:
Add to `/etc/rc.local` (before `exit 0`):
```bash
cd /home/pi/generator_control/
python3 raspberry_pi_generator_control.py &
```

## 7. Touchscreen optimization:
- Enable touch interface in `raspi-config`
- For fullscreen: uncomment line in code: `self.root.attributes('-fullscreen', True)`
- Hide mouse cursor: add `sudo apt install unclutter` and start unclutter

## 8. Generator Protocol Configuration:
**Important:** Modify the commands in the Python script based on your specific generator controller:

```python
# In parse_generator_response() - customize for your controller
# In send_generator_command() - adjust START/STOP commands
```

Common generator commands:
- `STATUS?` or `#STATUS` - get status
- `START` or `#START` - start generator  
- `STOP` or `#STOP` - stop generator
- `EMERGENCY` - emergency stop

## Network Diagram:
```
[Generator] ←RS232→ [USR-TCP232-410S] ←Ethernet→ [Router] ←WiFi→ [Raspberry Pi + Display]
     ↑                                                                      ↓
   Physical                                                            GUI Control
   Connection                                                          + Data Display
```
