# Generator Control System - Fresh Raspberry Pi OS Deployment

## 🎯 Quick Deployment Steps for New OS

### 1. Initial Setup (Fresh Raspberry Pi OS)
```bash
# Enable SSH and setup user
sudo systemctl enable ssh
sudo systemctl start ssh

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3-tk python3-requests xinput-calibrator evtest -y
```

### 2. Setup Passwordless SSH from Development Machine
```bash
# From your development machine (Mr-Power):
ssh-keygen -t rsa -b 4096 -C "lars@generator-system"
ssh-copy-id lars@192.168.1.25
```

### 3. Copy Files to Raspberry Pi
```bash
# Copy all necessary files
scp raspberry_pi_generator_control.py lars@192.168.1.25:~/
scp generator-panel.service lars@192.168.1.25:~/
scp disable_screen_sleep.desktop lars@192.168.1.25:~/
```

### 4. Configure Display and Touchscreen
```bash
# SSH to Pi
ssh lars@192.168.1.25

# Disable screen sleep permanently
mkdir -p ~/.config/autostart
mv ~/disable_screen_sleep.desktop ~/.config/autostart/

# Enable touchscreen events (run after X11 is up)
DISPLAY=:0 xinput set-prop 'raspberrypi-ts' 'libinput Send Events Mode Enabled' 1 0
```

### 5. Install and Start Service
```bash
# Install systemd service
sudo mv ~/generator-panel.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable generator-panel.service
sudo systemctl start generator-panel.service

# Check status
sudo systemctl status generator-panel.service
```

### 6. Verify Everything Works
```bash
# Check touchscreen device
xinput list | grep raspberrypi-ts

# Check touch events enabled
DISPLAY=:0 xinput list-props 'raspberrypi-ts' | grep "Send Events Mode Enabled"

# Monitor logs
sudo journalctl -u generator-panel.service -f
```

---

## 🔧 Hardware Configuration

### USR-TCP232-410S Settings (192.168.1.192)
- **Web Access**: http://192.168.1.192 (admin/admin)
- **TCP Server**: Port 8899
- **RS232 Config**:
  - Baud: 9600
  - Data: 8
  - Parity: None
  - Stop: 1
  - Flow Control: None

### Raspberry Pi Touchscreen
- **Device**: Official Raspberry Pi DSI Touchscreen
- **Input Device**: `/dev/input/event0` as `raspberrypi-ts`
- **Resolution**: 800x480

---

## 🚨 Troubleshooting

### Touchscreen Not Responding
```bash
# Check if touchscreen is detected
xinput list

# Check if events are enabled
DISPLAY=:0 xinput list-props 'raspberrypi-ts' | grep "Send Events Mode Enabled"

# If disabled, enable:
DISPLAY=:0 xinput set-prop 'raspberrypi-ts' 'libinput Send Events Mode Enabled' 1 0
```

### Service Not Starting
```bash
# Check service status
sudo systemctl status generator-panel.service

# Check logs
sudo journalctl -u generator-panel.service -n 50

# Manual test
DISPLAY=:0 python3 ~/raspberry_pi_generator_control.py
```

### Screen Sleep Issues
```bash
# Manual disable (temporary)
DISPLAY=:0 xset s off
DISPLAY=:0 xset -dpms
DISPLAY=:0 xset s noblank

# Check autostart file exists
ls -la ~/.config/autostart/disable_screen_sleep.desktop
```

---

## 📋 File Checklist
- ✅ `raspberry_pi_generator_control.py` - Main application
- ✅ `generator-panel.service` - Systemd service
- ✅ `disable_screen_sleep.desktop` - Screen sleep prevention
- ✅ This deployment guide

---

## 🎉 Expected Result
- Generator panel starts automatically at boot
- Touchscreen responds to all buttons
- Screen never sleeps or turns off
- Perfect replica of original generator panel interface
- No conflicts with other software

---

## 🔄 Service Management Commands
```bash
# Start service
sudo systemctl start generator-panel.service

# Stop service
sudo systemctl stop generator-panel.service

# Restart service
sudo systemctl restart generator-panel.service

# Check status
sudo systemctl status generator-panel.service

# View logs
sudo journalctl -u generator-panel.service -f

# Disable autostart
sudo systemctl disable generator-panel.service

# Enable autostart
sudo systemctl enable generator-panel.service
```
