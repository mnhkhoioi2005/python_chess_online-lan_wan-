"""
SimpleLobbyServer - Server đơn giản cho 1vs1 online chess
Sử dụng network_server.py có sẵn nhưng với wrapper để dễ sử dụng
"""
import socket
import threading
import json
from datetime import datetime

class SimpleLobbyServer:
    """
    Server đơn giản: Host tạo phòng, Guest join vào
    Sau đó forward data giữa 2 players
    """
    def __init__(self, host='127.0.0.1', port=12347):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        
        # Game state
        self.host_client = None
        self.guest_client = None
        self.host_username = None
        self.guest_username = None
        
        # Player limit
        self.max_players = 2
        self.connected_count = 0
        
        self.lock = threading.Lock()
    
    def start(self):
        """Khởi động server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(2)  # Chỉ cần 2 clients
            self.running = True
            
            print(f"🎮 Lobby Server đang chạy trên {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_sock, addr = self.server_socket.accept()
                    print(f"✅ Client kết nối từ {addr}")
                    
                    # Xử lý client
                    threading.Thread(
                        target=self.handle_client,
                        args=(client_sock, addr),
                        daemon=True
                    ).start()
                    
                except Exception as e:
                    if self.running:
                        print(f"❌ Lỗi accept connection: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Lỗi khởi động server: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_sock, addr):
        """Xử lý 1 client"""
        buffer = ""
        is_host = False
        
        try:
            # Kiểm tra số lượng players
            with self.lock:
                if self.connected_count >= self.max_players:
                    # Phòng đã đầy - Từ chối connection
                    print(f"❌ Từ chối {addr} - Phòng đã đầy ({self.max_players}/{self.max_players})")
                    self.send(client_sock, {
                        'type': 'error',
                        'error': 'room_full',
                        'message': f'Phòng đã đầy! ({self.max_players}/{self.max_players} players)'
                    })
                    client_sock.close()
                    return
                
                # Tăng count
                self.connected_count += 1
                print(f"📊 Players: {self.connected_count}/{self.max_players}")
            
            with self.lock:
                if self.host_client is None:
                    # Client đầu tiên = Host
                    self.host_client = client_sock
                    is_host = True
                    print(f"🎮 Host đã kết nối: {addr}")
                    
                    # Gửi thông báo cho host
                    self.send(client_sock, {
                        'type': 'role',
                        'role': 'host',
                        'color': 'white',
                        'message': 'Đang chờ đối thủ...'
                    })
                    
                elif self.guest_client is None:
                    # Client thứ 2 = Guest
                    self.guest_client = client_sock
                    is_host = False
                    print(f"🎮 Guest đã kết nối: {addr}")
                    
                    # Gửi thông báo cho guest
                    self.send(client_sock, {
                        'type': 'role',
                        'role': 'guest',
                        'color': 'black',
                        'message': 'Đã tham gia!'
                    })
                    
                    # Thông báo cho host là game bắt đầu
                    self.send(self.host_client, {
                        'type': 'game_start',
                        'message': 'Đối thủ đã vào! Trận đấu bắt đầu!'
                    })
                    
                    # Thông báo cho guest
                    self.send(client_sock, {
                        'type': 'game_start',
                        'message': 'Trận đấu bắt đầu!'
                    })
                    
                    print("🎉 Trận đấu bắt đầu!")
                    
                else:
                    # Đã đủ 2 người
                    self.send(client_sock, {
                        'type': 'error',
                        'message': 'Phòng đã đầy!'
                    })
                    client_sock.close()
                    return
            
            # Loop nhận và forward data
            while self.running:
                data = client_sock.recv(4096).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                
                # Xử lý từng message (tách bởi newline)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            msg = json.loads(line)
                            self.handle_message(msg, client_sock, is_host)
                        except json.JSONDecodeError:
                            pass
                        
        except Exception as e:
            print(f"❌ Lỗi xử lý client: {e}")
        finally:
            # Cleanup khi client disconnect
            with self.lock:
                # Giảm count
                self.connected_count = max(0, self.connected_count - 1)
                print(f"📊 Players: {self.connected_count}/{self.max_players}")
                
                if client_sock == self.host_client:
                    print("❌ Host đã ngắt kết nối")
                    self.host_client = None
                    # Thông báo cho guest
                    if self.guest_client:
                        try:
                            self.send(self.guest_client, {
                                'type': 'opponent_disconnected',
                                'message': 'Đối thủ đã ngắt kết nối!'
                            })
                        except:
                            pass
                elif client_sock == self.guest_client:
                    print("❌ Guest đã ngắt kết nối")
                    self.guest_client = None
                    # Thông báo cho host
                    if self.host_client:
                        try:
                            self.send(self.host_client, {
                                'type': 'opponent_disconnected',
                                'message': 'Đối thủ đã ngắt kết nối!'
                            })
                        except:
                            pass
            
            try:
                client_sock.close()
            except:
                pass
    
    def handle_message(self, msg, sender, is_host):
        """Xử lý message từ client và forward cho client còn lại"""
        msg_type = msg.get('type', '')
        
        # Forward message cho đối thủ
        with self.lock:
            if is_host and self.guest_client:
                self.send(self.guest_client, msg)
            elif not is_host and self.host_client:
                self.send(self.host_client, msg)
    
    def send(self, sock, data):
        """Gửi data đến client"""
        try:
            message = json.dumps(data) + '\n'
            sock.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"⚠️ Lỗi gửi data: {e}")
    
    def stop(self):
        """Dừng server"""
        self.running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        if self.host_client:
            try:
                self.host_client.close()
            except:
                pass
        
        if self.guest_client:
            try:
                self.guest_client.close()
            except:
                pass
        
        print("🛑 Server đã dừng")


if __name__ == "__main__":
    # Test server
    server = SimpleLobbyServer(host='127.0.0.1', port=12347)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Đang dừng server...")
        server.stop()
