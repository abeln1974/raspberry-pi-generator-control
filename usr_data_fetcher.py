#!/usr/bin/env python3
"""
Script for fetching data from USR-TCP232-410S serial-to-ethernet converter
Device IP: 192.168.1.192
Credentials: admin/admin
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import socket
import time
from urllib.parse import urljoin

class USRDataFetcher:
    def __init__(self, host="192.168.1.192", username="admin", password="admin"):
        self.host = host
        self.base_url = f"http://{host}/"
        self.auth = HTTPBasicAuth(username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
    
    def test_connection(self):
        """Test basic connectivity to the device"""
        try:
            response = self.session.get(self.base_url, timeout=5)
            print(f"✓ Connection successful: {response.status_code}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def get_status(self):
        """Get current device status"""
        endpoints = [
            "status.shtml",
            "status",
            "api/status",
            "status.json"
        ]
        
        for endpoint in endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✓ Status from {endpoint}:")
                    print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
                    return response.text
            except Exception as e:
                print(f"✗ {endpoint}: {e}")
        return None
    
    def get_ip_config(self):
        """Get IP configuration"""
        try:
            response = self.session.get(urljoin(self.base_url, "ipconfig.shtml"))
            if response.status_code == 200:
                print("✓ IP Config:")
                print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
                return response.text
        except Exception as e:
            print(f"✗ IP Config: {e}")
        return None
    
    def test_websocket_page(self):
        """Test websocket interface page"""
        try:
            response = self.session.get(urljoin(self.base_url, "websocket.shtml"))
            if response.status_code == 200:
                print("✓ WebSocket page accessible")
                print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
                return response.text
        except Exception as e:
            print(f"✗ WebSocket page: {e}")
        return None
    
    def test_tcp_connection(self, port=8080):
        """Test direct TCP connection (common for USR devices)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.host, port))
            sock.close()
            if result == 0:
                print(f"✓ TCP port {port} is open")
                return True
            else:
                print(f"✗ TCP port {port} is closed")
                return False
        except Exception as e:
            print(f"✗ TCP test failed: {e}")
            return False
    
    def scan_common_ports(self):
        """Scan common ports used by USR devices"""
        common_ports = [23, 80, 8080, 8899, 8080, 1030, 1031]
        open_ports = []
        
        for port in common_ports:
            if self.test_tcp_connection(port):
                open_ports.append(port)
        
        return open_ports
    
    def fetch_all_data(self):
        """Fetch all available data from the device"""
        print(f"=== USR-TCP232-410S Data Fetcher ===")
        print(f"Target: {self.host}")
        print("=" * 40)
        
        # Test basic connection
        if not self.test_connection():
            return
        
        # Get status information
        print("\n--- Status Information ---")
        self.get_status()
        
        # Get IP configuration
        print("\n--- IP Configuration ---")
        self.get_ip_config()
        
        # Test WebSocket interface
        print("\n--- WebSocket Interface ---")
        self.test_websocket_page()
        
        # Scan for open ports
        print("\n--- Port Scan ---")
        open_ports = self.scan_common_ports()
        print(f"Open ports: {open_ports}")

def main():
    """Main function"""
    fetcher = USRDataFetcher()
    fetcher.fetch_all_data()

if __name__ == "__main__":
    main()
