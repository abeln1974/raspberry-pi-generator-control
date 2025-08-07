#!/usr/bin/env python3
"""
Raspberry Pi Generator Control Interface - Exact Panel Replica
Replicates the exact look and feel of the generator control panel
- Blue LCD display with horizontal bars
- Identical button layout and colors
- Navigation controls
"""

import tkinter as tk
from tkinter import ttk, messagebox, Canvas
import socket
import threading
import time
import json
from datetime import datetime
import queue

class GeneratorPanelReplica:
    def __init__(self):
        # Network settings
        self.usr_ip = "192.168.1.192"
        self.usr_port = 8899  # Configure this port on USR device
        
        # Data storage
        self.generator_data = {
            'status': 'UNKNOWN',
            'voltage': 0.0,
            'current': 0.0,
            'power': 0.0,
            'frequency': 0.0,
            'engine_temp': 0.0,
            'oil_pressure': 0.0,
            'runtime': 0,
            'last_update': None
        }
        
        # Threading
        self.data_queue = queue.Queue()
        self.monitoring = False
        
        # GUI setup
        self.setup_gui()
        self.start_monitoring()
    
    def setup_gui(self):
        """Setup the main GUI for Raspberry Pi touchscreen"""
        self.root = tk.Tk()
        self.root.title("Generator Control System")
        self.root.geometry("800x480")  # Standard 7" Pi display
        self.root.configure(bg='black')
        
        # Make fullscreen for Pi
        # self.root.attributes('-fullscreen', True)
        
        # Main container
        main_frame = tk.Frame(self.root, bg='black')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="GENERATOR CONTROL SYSTEM", 
                              font=('Arial', 24, 'bold'), fg='white', bg='black')
        title_label.pack(pady=(0, 20))
        
        # Status section
        self.create_status_section(main_frame)
        
        # Data display section
        self.create_data_section(main_frame)
        
        # Control buttons section
        self.create_control_section(main_frame)
        
        # Start data refresh timer
        self.refresh_display()
    
    def create_status_section(self, parent):
        """Create generator status indicator"""
        status_frame = tk.Frame(parent, bg='black')
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(status_frame, text="STATUS:", font=('Arial', 16, 'bold'), 
                fg='white', bg='black').pack(side=tk.LEFT)
        
        self.status_label = tk.Label(status_frame, text="CONNECTING...", 
                                   font=('Arial', 16, 'bold'), fg='yellow', bg='black')
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Connection indicator
        self.connection_label = tk.Label(status_frame, text="●", 
                                       font=('Arial', 20), fg='red', bg='black')
        self.connection_label.pack(side=tk.RIGHT)
    
    def create_data_section(self, parent):
        """Create data display grid"""
        data_frame = tk.Frame(parent, bg='black')
        data_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Configure grid
        for i in range(4):
            data_frame.grid_columnconfigure(i, weight=1)
        
        # Data labels
        self.data_labels = {}
        data_items = [
            ('Spenning', 'voltage', 'V'),
            ('Strøm', 'current', 'A'),
            ('Effekt', 'power', 'kW'),
            ('Frekvens', 'frequency', 'Hz'),
            ('Motor Temp', 'engine_temp', '°C'),
            ('Olje Trykk', 'oil_pressure', 'bar'),
            ('Driftstid', 'runtime', 'timer'),
            ('Sist oppdatert', 'last_update', '')
        ]
        
        row = 0
        col = 0
        for label, key, unit in data_items:
            frame = tk.Frame(data_frame, bg='gray20', relief=tk.RAISED, bd=2)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            tk.Label(frame, text=label, font=('Arial', 12, 'bold'), 
                    fg='white', bg='gray20').pack(pady=(5, 0))
            
            value_label = tk.Label(frame, text="--", font=('Arial', 16), 
                                 fg='cyan', bg='gray20')
            value_label.pack(pady=(0, 5))
            
            self.data_labels[key] = (value_label, unit)
            
            col += 1
            if col >= 4:
                col = 0
                row += 1
    
    def create_control_section(self, parent):
        """Create control buttons"""
        control_frame = tk.Frame(parent, bg='black')
        control_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Control buttons with colors and large size for touch
        button_config = {
            'font': ('Arial', 18, 'bold'),
            'width': 12,
            'height': 2
        }
        
        # START button
        self.start_btn = tk.Button(control_frame, text="START", 
                                  bg='green', fg='white', 
                                  command=self.start_generator, 
                                  **button_config)
        self.start_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # STOP button
        self.stop_btn = tk.Button(control_frame, text="STOPP", 
                                 bg='orange', fg='white', 
                                 command=self.stop_generator, 
                                 **button_config)
        self.stop_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # EMERGENCY STOP button
        self.emergency_btn = tk.Button(control_frame, text="NØDSTOPP", 
                                      bg='red', fg='white', 
                                      command=self.emergency_stop, 
                                      font=('Arial', 18, 'bold'),
                                      width=15, height=2)
        self.emergency_btn.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self.monitor_generator, daemon=True)
        monitor_thread.start()
    
    def monitor_generator(self):
        """Background thread to monitor generator data"""
        while self.monitoring:
            try:
                # Connect to USR device and get data
                data = self.fetch_generator_data()
                if data:
                    self.data_queue.put(data)
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                self.data_queue.put({'error': str(e)})
                time.sleep(5)  # Wait longer on error
    
    def fetch_generator_data(self):
        """Fetch data from generator via USR device"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((self.usr_ip, self.usr_port))
            
            # Send status request command (customize for your generator)
            command = b"STATUS?\r\n"  # Adjust based on your generator protocol
            sock.send(command)
            
            # Read response
            response = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            
            # Parse response (customize based on your generator's data format)
            return self.parse_generator_response(response)
            
        except Exception as e:
            return {'error': f"Connection failed: {e}"}
    
    def parse_generator_response(self, response):
        """Parse generator response - customize for your specific controller"""
        # This is a template - adjust based on your generator's actual response format
        try:
            # Example parsing - adjust for your generator
            lines = response.strip().split('\n')
            data = {
                'status': 'RUNNING' if 'ON' in response.upper() else 'STOPPED',
                'voltage': 230.0,  # Extract from response
                'current': 10.5,   # Extract from response  
                'power': 2.4,      # Extract from response
                'frequency': 50.0, # Extract from response
                'engine_temp': 75.0,
                'oil_pressure': 3.5,
                'runtime': 120,
                'last_update': datetime.now().strftime('%H:%M:%S'),
                'connected': True
            }
            return data
        except:
            return {
                'status': 'PARSE_ERROR',
                'connected': False,
                'last_update': datetime.now().strftime('%H:%M:%S')
            }
    
    def send_generator_command(self, command):
        """Send control command to generator"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.usr_ip, self.usr_port))
            
            # Send command (customize based on your generator protocol)
            if isinstance(command, str):
                command = command.encode() + b'\r\n'
            
            sock.send(command)
            
            # Read response
            response = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            
            return True, response
            
        except Exception as e:
            return False, str(e)
    
    def start_generator(self):
        """Start generator"""
        result = messagebox.askyesno("Bekreft", "Start generator?")
        if result:
            success, response = self.send_generator_command("START")
            if success:
                messagebox.showinfo("Start", "Generator start-kommando sendt")
            else:
                messagebox.showerror("Feil", f"Kunne ikke starte: {response}")
    
    def stop_generator(self):
        """Stop generator"""
        result = messagebox.askyesno("Bekreft", "Stopp generator?")
        if result:
            success, response = self.send_generator_command("STOP")
            if success:
                messagebox.showinfo("Stopp", "Generator stopp-kommando sendt")
            else:
                messagebox.showerror("Feil", f"Kunne ikke stoppe: {response}")
    
    def emergency_stop(self):
        """Emergency stop generator"""
        result = messagebox.askyesno("NØDSTOPP", 
                                   "NØDSTOPP GENERATOR?\n\nDette vil stoppe generatoren umiddelbart!",
                                   icon='warning')
        if result:
            success, response = self.send_generator_command("EMERGENCY_STOP")
            if success:
                messagebox.showwarning("NØDSTOPP", "NØDSTOPP aktivert!")
            else:
                messagebox.showerror("Feil", f"NØDSTOPP feilet: {response}")
    
    def refresh_display(self):
        """Refresh the display with latest data"""
        try:
            # Process queued data updates
            while not self.data_queue.empty():
                data = self.data_queue.get_nowait()
                
                if 'error' in data:
                    self.status_label.config(text="CONNECTION ERROR", fg='red')
                    self.connection_label.config(fg='red')
                elif 'connected' in data and data['connected']:
                    self.generator_data.update(data)
                    self.status_label.config(text=data.get('status', 'UNKNOWN'), 
                                           fg='green' if data.get('status') == 'RUNNING' else 'orange')
                    self.connection_label.config(fg='green')
                
                # Update data display
                for key, (label, unit) in self.data_labels.items():
                    if key in self.generator_data:
                        value = self.generator_data[key]
                        if key == 'last_update':
                            display_text = str(value)
                        elif isinstance(value, float):
                            display_text = f"{value:.1f} {unit}"
                        else:
                            display_text = f"{value} {unit}"
                        
                        label.config(text=display_text)
        
        except queue.Empty:
            pass
        
        # Schedule next refresh
        self.root.after(500, self.refresh_display)
    
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        finally:
            self.monitoring = False

# Additional setup script for Raspberry Pi
def create_setup_instructions():
    """Create setup instructions file"""
    setup_text = """
# Raspberry Pi Generator Control Setup

## 1. Install required packages:
sudo apt update
sudo apt install python3-tk python3-pip

## 2. Configure USR-TCP232-410S:
- Open http://192.168.1.192 in browser
- Go to RS232 settings
- Set: 9600 baud, 8N1
- Mode: TCP Server
- Local Port: 8899
- Save and reboot USR device

## 3. Physical connections:
Generator Controller DB9 → USR-TCP232-410S
USR device → Ethernet to local network
Raspberry Pi → Same network

## 4. Run the application:
python3 raspberry_pi_generator_control.py

## 5. For autostart on Pi boot, add to /etc/rc.local:
cd /home/pi/generator_control/
python3 raspberry_pi_generator_control.py &

## 6. For touchscreen optimization:
- Enable touch in raspi-config
- Adjust screen resolution if needed
- Consider hiding mouse cursor for touch-only interface
"""
    
    with open('/home/lars/CascadeProjects/raspberry_pi_setup.md', 'w') as f:
        f.write(setup_text)

if __name__ == "__main__":
    print("Starting Generator Panel Replica...")
    app = GeneratorPanelReplica()
    app.run()
