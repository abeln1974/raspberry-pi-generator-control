#!/usr/bin/env python3
"""
Raspberry Pi Generator Control Interface - Touchscreen Optimized
Specifically optimized for Raspberry Pi touchscreen with larger buttons and better touch handling
"""

import tkinter as tk
from tkinter import ttk, messagebox, Canvas
import socket
import threading
import time
import json
from datetime import datetime
import queue

class TouchOptimizedGeneratorPanel:
    def __init__(self):
        # Network settings
        self.usr_ip = "192.168.1.192"
        self.usr_port = 8899
        
        # Generator data storage
        self.generator_data = {
            'voltage_l1': 230.0,
            'voltage_l2': 230.0, 
            'voltage_l3': 230.0,
            'current_l1': 10.5,
            'current_l2': 10.3,
            'current_l3': 10.8,
            'power': 7.2,
            'frequency': 50.0,
            'engine_temp': 75,
            'oil_pressure': 3.5,
            'fuel_level': 85,
            'runtime': 240,
            'status': 'STOPPED',
            'mode': 'MANUAL',
            'alarms': [],
            'connected': False
        }
        
        # UI state
        self.current_screen = 0
        self.data_queue = queue.Queue()
        self.monitoring = False
        
        # Setup the touchscreen-optimized interface
        self.setup_touch_gui()
        self.start_monitoring()
    
    def setup_touch_gui(self):
        """Create touchscreen-optimized interface"""
        self.root = tk.Tk()
        self.root.title("Generator Control Panel")
        
        # Fullscreen and touch optimizations
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#2c2c2c', cursor='none')  # Hide cursor for touch
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#2c2c2c')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create exit button in corner (for testing)
        exit_btn = tk.Button(main_frame, text="×", font=('Arial', 16, 'bold'),
                           bg='#ff4444', fg='white', command=self.exit_app,
                           width=3, height=1)
        exit_btn.place(x=screen_width-100, y=10)
        
        # Create the blue LCD display area (larger for touch)
        self.create_large_lcd_display(main_frame)
        
        # Create large navigation buttons
        self.create_large_navigation_buttons(main_frame)
        
        # Create large control buttons (optimized for touch)
        self.create_large_control_buttons(main_frame)
        
        # Bind touch events for better responsiveness
        self.root.bind('<Button-1>', self.on_touch_down)
        self.root.bind('<ButtonRelease-1>', self.on_touch_up)
        
        # Start display refresh
        self.refresh_display()
    
    def create_large_lcd_display(self, parent):
        """Create larger LCD display for better visibility"""
        # LCD frame with blue background (larger)
        lcd_frame = tk.Frame(parent, bg='#1a4a80', relief=tk.SUNKEN, bd=5, height=280)
        lcd_frame.pack(fill=tk.X, pady=(0, 20))
        lcd_frame.pack_propagate(False)
        
        # LCD display canvas (larger)
        self.lcd_canvas = Canvas(lcd_frame, bg='#2060b0', height=260, highlightthickness=0)
        self.lcd_canvas.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Initialize LCD display
        self.update_lcd_display()
    
    def create_large_navigation_buttons(self, parent):
        """Create larger navigation buttons for touch"""
        nav_frame = tk.Frame(parent, bg='#2c2c2c')
        nav_frame.pack(anchor=tk.E, pady=(0, 15))
        
        # Larger button style for touch
        button_style = {
            'font': ('Arial', 24, 'bold'),
            'width': 4,
            'height': 2,
            'bg': '#00bcd4',
            'fg': 'white',
            'relief': tk.RAISED,
            'bd': 3,
            'activebackground': '#00acc1'
        }
        
        # Navigation buttons with touch-friendly spacing
        self.left_btn = tk.Button(nav_frame, text="◀", command=self.nav_left, **button_style)
        self.left_btn.pack(side=tk.LEFT, padx=8)
        
        self.enter_btn = tk.Button(nav_frame, text="▶", command=self.nav_enter, **button_style)
        self.enter_btn.pack(side=tk.LEFT, padx=8)
        
        self.right_btn = tk.Button(nav_frame, text="▶", command=self.nav_right, **button_style)
        self.right_btn.pack(side=tk.LEFT, padx=8)
        
        self.menu_btn = tk.Button(nav_frame, text="⚙", command=self.nav_menu, **button_style)
        self.menu_btn.pack(side=tk.LEFT, padx=8)
    
    def create_large_control_buttons(self, parent):
        """Create extra large control buttons optimized for touch"""
        button_frame = tk.Frame(parent, bg='#2c2c2c')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=30)
        
        # Extra large buttons for touch
        buttons = [
            {
                'text': '●',
                'bg': '#d32f2f',
                'fg': 'white',
                'font': ('Arial', 48, 'bold'),
                'command': self.emergency_stop,
                'tooltip': 'NØDSTOPP'
            },
            {
                'text': 'Auto',
                'bg': '#ffa000',
                'fg': 'black',
                'font': ('Arial', 20, 'bold'),
                'command': self.set_auto_mode,
                'tooltip': 'Automatisk Modus'
            },
            {
                'text': '✋',
                'bg': '#ffa000',
                'fg': 'black', 
                'font': ('Arial', 36, 'bold'),
                'command': self.set_manual_mode,
                'tooltip': 'Manuell Modus'
            },
            {
                'text': '⚠',
                'bg': '#ffa000',
                'fg': 'black',
                'font': ('Arial', 36, 'bold'),
                'command': self.alarm_reset,
                'tooltip': 'Alarm Reset'
            },
            {
                'text': 'I',
                'bg': '#388e3c',
                'fg': 'white',
                'font': ('Arial', 48, 'bold'),
                'command': self.start_generator,
                'tooltip': 'START'
            }
        ]
        
        self.control_buttons = []
        for i, btn_config in enumerate(buttons):
            btn = tk.Button(
                button_frame,
                text=btn_config['text'],
                bg=btn_config['bg'],
                fg=btn_config['fg'],
                font=btn_config['font'],
                command=btn_config['command'],
                width=12,
                height=4,  # Extra tall for touch
                relief=tk.RAISED,
                bd=5,
                activebackground=btn_config['bg'],
                activeforeground=btn_config['fg']
            )
            btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=8)
            self.control_buttons.append(btn)
            
            # Add visual feedback for touch
            btn.bind('<Button-1>', lambda e, b=btn: self.button_pressed(b))
            btn.bind('<ButtonRelease-1>', lambda e, b=btn: self.button_released(b))
    
    def button_pressed(self, button):
        """Visual feedback when button is pressed"""
        button.configure(relief=tk.SUNKEN, bd=2)
        self.root.update()
    
    def button_released(self, button):
        """Visual feedback when button is released"""
        button.configure(relief=tk.RAISED, bd=5)
        self.root.update()
    
    def on_touch_down(self, event):
        """Handle touch down events"""
        pass
    
    def on_touch_up(self, event):
        """Handle touch up events"""
        pass
    
    def update_lcd_display(self):
        """Update the LCD display with current data"""
        self.lcd_canvas.delete("all")
        
        # Display title (larger font)
        titles = ["HOVEDSKJERM", "SPENNINGER", "STRØMMER", "EFFEKT", "MOTOR"]
        title = titles[self.current_screen % len(titles)]
        
        self.lcd_canvas.create_text(250, 30, text=title, fill='white', 
                                   font=('Arial', 20, 'bold'))
        
        if self.current_screen == 0:  # Main screen
            self.draw_main_screen()
        elif self.current_screen == 1:  # Voltages
            self.draw_voltage_screen()
        elif self.current_screen == 2:  # Currents
            self.draw_current_screen()
        elif self.current_screen == 3:  # Power
            self.draw_power_screen()
        elif self.current_screen == 4:  # Engine
            self.draw_engine_screen()
    
    def draw_main_screen(self):
        """Draw main overview screen with larger elements"""
        y_pos = 70
        line_height = 35
        
        # Status (larger)
        status_color = 'green' if self.generator_data['status'] == 'RUNNING' else 'red'
        self.lcd_canvas.create_text(30, y_pos, text=f"Status: {self.generator_data['status']}", 
                                   fill=status_color, font=('Arial', 16, 'bold'), anchor='w')
        
        # Power bar (larger)
        y_pos += line_height
        self.lcd_canvas.create_text(30, y_pos, text="Effekt:", fill='white', 
                                   font=('Arial', 14), anchor='w')
        self.draw_large_horizontal_bar(150, y_pos-8, self.generator_data['power'], 10.0, 'cyan')
        
        # Frequency (larger)
        y_pos += line_height  
        self.lcd_canvas.create_text(30, y_pos, text=f"Frekvens: {self.generator_data['frequency']:.1f} Hz", 
                                   fill='white', font=('Arial', 14), anchor='w')
        
        # Runtime (larger)
        y_pos += line_height
        hours = self.generator_data['runtime'] // 60
        minutes = self.generator_data['runtime'] % 60
        self.lcd_canvas.create_text(30, y_pos, text=f"Driftstid: {hours:02d}:{minutes:02d}", 
                                   fill='white', font=('Arial', 14), anchor='w')
    
    def draw_voltage_screen(self):
        """Draw voltage screen with larger bars"""
        y_pos = 70
        
        phases = ['L1', 'L2', 'L3']
        voltages = [self.generator_data['voltage_l1'], 
                   self.generator_data['voltage_l2'],
                   self.generator_data['voltage_l3']]
        
        for i, (phase, voltage) in enumerate(zip(phases, voltages)):
            y = y_pos + i * 45
            self.lcd_canvas.create_text(30, y, text=f"{phase}:", fill='white', 
                                       font=('Arial', 14, 'bold'), anchor='w')
            self.lcd_canvas.create_text(70, y, text=f"{voltage:.1f}V", fill='yellow', 
                                       font=('Arial', 14), anchor='w')
            self.draw_large_horizontal_bar(150, y-8, voltage, 250.0, 'yellow')
    
    def draw_current_screen(self):
        """Draw current screen with larger bars"""
        y_pos = 70
        
        phases = ['L1', 'L2', 'L3']
        currents = [self.generator_data['current_l1'],
                   self.generator_data['current_l2'], 
                   self.generator_data['current_l3']]
        
        for i, (phase, current) in enumerate(zip(phases, currents)):
            y = y_pos + i * 45
            self.lcd_canvas.create_text(30, y, text=f"{phase}:", fill='white', 
                                       font=('Arial', 14, 'bold'), anchor='w')
            self.lcd_canvas.create_text(70, y, text=f"{current:.1f}A", fill='cyan', 
                                       font=('Arial', 14), anchor='w')
            self.draw_large_horizontal_bar(150, y-8, current, 20.0, 'cyan')
    
    def draw_power_screen(self):
        """Draw power screen with larger elements"""
        y_pos = 70
        line_height = 45
        
        self.lcd_canvas.create_text(30, y_pos, text=f"Aktiv effekt: {self.generator_data['power']:.1f} kW", 
                                   fill='white', font=('Arial', 14), anchor='w')
        self.draw_large_horizontal_bar(30, y_pos + 20, self.generator_data['power'], 10.0, 'green')
        
        y_pos += 60
        apparent_power = self.generator_data['power'] * 1.05
        self.lcd_canvas.create_text(30, y_pos, text=f"Tilsynelatende: {apparent_power:.1f} kVA", 
                                   fill='white', font=('Arial', 14), anchor='w')
    
    def draw_engine_screen(self):
        """Draw engine parameters screen with larger elements"""
        y_pos = 70
        line_height = 45
        
        # Engine temperature (larger)
        self.lcd_canvas.create_text(30, y_pos, text="Motortemp:", fill='white', 
                                   font=('Arial', 14), anchor='w')
        self.lcd_canvas.create_text(130, y_pos, text=f"{self.generator_data['engine_temp']}°C", 
                                   fill='orange', font=('Arial', 14), anchor='w')
        self.draw_large_horizontal_bar(200, y_pos-8, self.generator_data['engine_temp'], 100.0, 'orange')
        
        # Oil pressure (larger)
        y_pos += line_height
        self.lcd_canvas.create_text(30, y_pos, text="Oljetrykk:", fill='white', 
                                   font=('Arial', 14), anchor='w')
        self.lcd_canvas.create_text(130, y_pos, text=f"{self.generator_data['oil_pressure']:.1f} bar", 
                                   fill='green', font=('Arial', 14), anchor='w')
        self.draw_large_horizontal_bar(200, y_pos-8, self.generator_data['oil_pressure'], 5.0, 'green')
        
        # Fuel level (larger)
        y_pos += line_height
        self.lcd_canvas.create_text(30, y_pos, text="Drivstoff:", fill='white', 
                                   font=('Arial', 14), anchor='w')
        self.lcd_canvas.create_text(130, y_pos, text=f"{self.generator_data['fuel_level']}%", 
                                   fill='yellow', font=('Arial', 14), anchor='w')
        self.draw_large_horizontal_bar(200, y_pos-8, self.generator_data['fuel_level'], 100.0, 'yellow')
    
    def draw_large_horizontal_bar(self, x, y, value, max_value, color):
        """Draw larger horizontal bar graph for touch visibility"""
        bar_width = 280
        bar_height = 20
        
        # Background bar (larger)
        self.lcd_canvas.create_rectangle(x, y, x + bar_width, y + bar_height, 
                                        fill='#003366', outline='white', width=2)
        
        # Value bar (larger)
        fill_width = (value / max_value) * bar_width
        if fill_width > bar_width:
            fill_width = bar_width
            color = 'red'
            
        if fill_width > 0:
            self.lcd_canvas.create_rectangle(x, y, x + fill_width, y + bar_height, 
                                           fill=color, outline='')
    
    # Navigation functions
    def nav_left(self):
        self.current_screen = (self.current_screen - 1) % 5
        self.update_lcd_display()
    
    def nav_right(self):
        self.current_screen = (self.current_screen + 1) % 5
        self.update_lcd_display()
    
    def nav_enter(self):
        pass
    
    def nav_menu(self):
        messagebox.showinfo("Menu", "Systeminnstillinger")
    
    # Control button functions with touch feedback
    def emergency_stop(self):
        """Emergency stop with immediate visual feedback"""
        self.show_touch_feedback("NØDSTOPP AKTIVERT!")
        result = messagebox.askyesno("NØDSTOPP", 
                                   "NØDSTOPP GENERATOR?\n\nDette vil stoppe generatoren umiddelbart!",
                                   icon='warning')
        if result:
            success, response = self.send_generator_command("EMERGENCY_STOP")
            if success:
                messagebox.showwarning("NØDSTOPP", "NØDSTOPP aktivert!")
                self.generator_data['status'] = 'EMERGENCY_STOP'
    
    def set_auto_mode(self):
        self.show_touch_feedback("AUTO MODUS")
        self.generator_data['mode'] = 'AUTO'
        messagebox.showinfo("Modus", "Automatisk modus aktivert")
        self.update_mode_buttons()
    
    def set_manual_mode(self):
        self.show_touch_feedback("MANUELL MODUS")
        self.generator_data['mode'] = 'MANUAL'  
        messagebox.showinfo("Modus", "Manuell modus aktivert")
        self.update_mode_buttons()
    
    def alarm_reset(self):
        self.show_touch_feedback("ALARM RESET")
        success, response = self.send_generator_command("ALARM_RESET")
        if success:
            self.generator_data['alarms'] = []
            messagebox.showinfo("Alarm", "Alarmer tilbakestilt")
    
    def start_generator(self):
        if self.generator_data['status'] == 'RUNNING':
            self.show_touch_feedback("STOPPER GENERATOR")
            result = messagebox.askyesno("Stopp", "Stopp generator?")
            if result:
                success, response = self.send_generator_command("STOP")
                if success:
                    messagebox.showinfo("Stopp", "Generator stoppet")
                    self.generator_data['status'] = 'STOPPED'
        else:
            self.show_touch_feedback("STARTER GENERATOR")
            result = messagebox.askyesno("Start", "Start generator?")
            if result:
                success, response = self.send_generator_command("START")
                if success:
                    messagebox.showinfo("Start", "Generator startet")
                    self.generator_data['status'] = 'RUNNING'
        
        self.update_start_button()
    
    def show_touch_feedback(self, message):
        """Show immediate visual feedback for touch"""
        # Flash the screen briefly
        self.root.configure(bg='white')
        self.root.update()
        self.root.after(100, lambda: self.root.configure(bg='#2c2c2c'))
    
    def update_mode_buttons(self):
        """Update mode button highlighting"""
        self.control_buttons[1].configure(relief=tk.RAISED)
        self.control_buttons[2].configure(relief=tk.RAISED)
        
        if self.generator_data['mode'] == 'AUTO':
            self.control_buttons[1].configure(relief=tk.SUNKEN)
        else:
            self.control_buttons[2].configure(relief=tk.SUNKEN)
    
    def update_start_button(self):
        """Update start/stop button based on status"""
        if self.generator_data['status'] == 'RUNNING':
            self.control_buttons[4].configure(text='O', bg='#d32f2f')
        else:
            self.control_buttons[4].configure(text='I', bg='#388e3c')
    
    def send_generator_command(self, command):
        """Send command to generator via USR device"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.usr_ip, self.usr_port))
            
            if isinstance(command, str):
                command = command.encode() + b'\r\n'
            
            sock.send(command)
            response = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            
            return True, response
            
        except Exception as e:
            return False, str(e)
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self.monitor_generator, daemon=True)
        monitor_thread.start()
    
    def monitor_generator(self):
        """Background monitoring of generator data"""
        while self.monitoring:
            try:
                import random
                self.generator_data.update({
                    'voltage_l1': 230 + random.uniform(-5, 5),
                    'voltage_l2': 230 + random.uniform(-5, 5),
                    'voltage_l3': 230 + random.uniform(-5, 5),
                    'current_l1': 10 + random.uniform(-2, 2),
                    'current_l2': 10 + random.uniform(-2, 2),
                    'current_l3': 10 + random.uniform(-2, 2),
                    'power': 7.2 + random.uniform(-1, 1),
                    'frequency': 50.0 + random.uniform(-0.2, 0.2),
                    'engine_temp': 75 + random.uniform(-5, 5),
                    'oil_pressure': 3.5 + random.uniform(-0.5, 0.5),
                    'fuel_level': max(0, 85 - random.uniform(0, 0.1)),
                    'connected': True
                })
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)
    
    def refresh_display(self):
        """Refresh the display periodically"""
        self.update_lcd_display()
        self.update_mode_buttons()
        self.update_start_button()
        
        self.root.after(1000, self.refresh_display)
    
    def exit_app(self):
        """Exit the application"""
        self.monitoring = False
        self.root.quit()
    
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        finally:
            self.monitoring = False

if __name__ == "__main__":
    print("Starting Touch-Optimized Generator Panel...")
    app = TouchOptimizedGeneratorPanel()
    app.run()
