import socket
import threading
import json
import requests

class GameServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        
        self.clients = {}
        self.positions = {}
        
        # Get and print IP addresses
        print("\n=== Server Network Information ===")
        
        # Local IP (for same network players)
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Local IP (for same network): {local_ip}")
        
        # Alternative method to get local IP
        try:
            # This creates a temporary connection to get the correct local IP
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            temp_sock.connect(("8.8.8.8", 80))
            alternative_local_ip = temp_sock.getsockname()[0]
            temp_sock.close()
            if alternative_local_ip != local_ip:
                print(f"Alternative Local IP: {alternative_local_ip}")
        except:
            pass
        
        # Public IP (for internet players, requires port forwarding)
        try:
            public_ip = requests.get('https://api.ipify.org').text
            print(f"Public IP (requires port forwarding): {public_ip}")
        except:
            print("Couldn't get public IP address")
        
        print(f"Port: {port}")
        print("\nPlayers on the same network should use the Local IP.")
        print("Waiting for connections...\n")
        
    def handle_client(self, conn, addr):
        player_id = addr[1]
        self.positions[player_id] = {"x": 100, "y": 100}
        
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                
                data = json.loads(data)
                self.positions[player_id] = data
                
                # Send all players' positions
                conn.send(json.dumps(self.positions).encode())
                
            except:
                break
            
        print(f"Client {addr} disconnected")
        del self.positions[player_id]
        conn.close()
        
    def start(self):
        while True:
            conn, addr = self.server.accept()
            print(f"Connected to {addr}")
            
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    server = GameServer()
    server.start() 