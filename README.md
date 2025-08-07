# Raspberry Pi Generator Control System

A complete generator monitoring and control system for Raspberry Pi with touchscreen interface, designed to replicate the original generator control panel exactly.

## 🎯 Features

- **Full Generator Panel Replica** - Exact visual and functional match to original hardware panel
- **Touchscreen Interface** - Optimized for Raspberry Pi official DSI touchscreen
- **Network Communication** - Via USR-TCP232-410S serial-to-ethernet converter
- **Automatic Startup** - Runs as systemd service in kiosk mode
- **Dual Network Support** - Ethernet for generator communication, WiFi for remote access
- **Wayland Compatible** - Works with modern Raspberry Pi OS

## 🖥️ System Requirements

- Raspberry Pi 4 (recommended) with official DSI touchscreen
- Fresh Raspberry Pi OS (64-bit with desktop)
- USR-TCP232-410S serial-to-ethernet converter
- Generator controller with RS232/RS485 interface
- Ethernet connection between Pi and USR device

## 🔧 Hardware Setup

### Network Configuration
- **Raspberry Pi Ethernet:** Static IP `192.168.0.1/24`
- **USR-TCP232-410S:** Static IP `192.168.0.7` (TCP Server, port 8899)
- **WiFi:** Preserved for remote access

### RS232 Cable Requirements
- **Type:** DB9 female-to-female straight-through cable
- **NOT null-modem** - USR device handles signal conversion
- **Length:** Maximum 15 meters (shorter preferred)
- **Shielded cable recommended** for noise immunity

## 📁 Project Files

### Core Application
- `raspberry_pi_generator_control.py` - Main generator panel application
- `raspberry_pi_generator_control_touch.py` - Touchscreen-optimized version (optional)
- `usr_data_fetcher.py` - USR device communication test utility

### System Configuration
- `generator-panel-wayland.service` - Systemd service for Wayland (recommended)
- `generator-panel.service` - Systemd service for Xorg (legacy)
- `disable_screen_sleep.desktop` - Autostart script to prevent screen sleep

### Documentation
- `RASPBERRY_PI_DEPLOYMENT_GUIDE.md` - Complete deployment and troubleshooting guide
- `raspberry_pi_setup.md` - Basic setup instructions

## 🚀 Quick Start

1. **Flash fresh Raspberry Pi OS** (64-bit with desktop)
2. **Install dependencies:**
   ```bash
   sudo apt update && sudo apt install -y python3-tk xinput-calibrator evtest
   ```
3. **Configure network:**
   ```bash
   sudo nmcli connection modify 'Wired connection 1' ipv4.addresses 192.168.0.1/24 ipv4.method manual
   sudo nmcli connection up 'Wired connection 1'
   ```
4. **Install systemd service:**
   ```bash
   sudo cp generator-panel-wayland.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable generator-panel-wayland.service
   ```
5. **Configure display rotation (if needed):**
   ```bash
   mkdir -p ~/.config/autostart
   cp disable_screen_sleep.desktop ~/.config/autostart/
   # For 180° rotation, add rotate_display.desktop to autostart
   ```

## 🎮 Control Interface

### Control Buttons
- **Emergency Stop** (Red) - Immediate generator shutdown
- **Auto Mode** (Orange) - Automatic operation mode
- **Manual Mode** (Orange) - Manual control mode  
- **Alarm Reset** (Orange) - Clear alarm conditions
- **Start/Stop** (Green) - Generator start/stop control

### Navigation
- **Overview** - Main status display
- **Alarms** - Alarm history and status
- **Settings** - System configuration
- **About** - System information

## 🔧 Troubleshooting

### Touchscreen Issues
- Verify device: `ls /dev/input/event*`
- Test events: `sudo evtest /dev/input/event0`
- Check X11 input: `xinput list`

### Network Issues
- Test USR connection: `python3 usr_data_fetcher.py`
- Verify IP configuration: `ip addr show`
- Check service logs: `sudo journalctl -u generator-panel-wayland.service -f`

### Display Rotation
- For Wayland: `WAYLAND_DISPLAY=wayland-0 wlr-randr --output DSI-1 --transform 180`
- Make persistent via autostart desktop file

## 📋 Service Management

```bash
# Check status
sudo systemctl status generator-panel-wayland.service

# View logs
sudo journalctl -u generator-panel-wayland.service -f

# Restart service
sudo systemctl restart generator-panel-wayland.service

# Stop service
sudo systemctl stop generator-panel-wayland.service
```

## 🌐 Network Architecture

```
Generator Controller ←→ USR-TCP232-410S (192.168.0.7) ←→ Raspberry Pi (192.168.0.1)
                                                              ↕
                                                         WiFi Network (Remote Access)
```

## 📖 Complete Documentation

See `RASPBERRY_PI_DEPLOYMENT_GUIDE.md` for comprehensive setup instructions, troubleshooting, and advanced configuration options.

## 🎯 System Status

- ✅ **Touchscreen Interface** - Fully functional
- ✅ **Network Communication** - Dual interface setup
- ✅ **Display Rotation** - 180° rotation support
- ✅ **Automatic Startup** - Systemd service integration
- ✅ **Wayland Compatibility** - Modern Pi OS support
- ✅ **Production Ready** - Stable and robust operation

## 🔗 Hardware Connections

1. **Power:** Raspberry Pi power supply
2. **Display:** Official DSI touchscreen ribbon cable
3. **Ethernet:** Pi to USR-TCP232-410S device
4. **Serial:** USR device to generator controller (RS232 cable)
5. **WiFi:** Preserved for remote SSH access

---

**Generator Control System - Complete solution for Raspberry Pi generator monitoring and control**
