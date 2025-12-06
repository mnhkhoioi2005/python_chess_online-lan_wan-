"""
OnlineClient - Client kết nối đến server online
Wrapper đơn giản cho việc kết nối và giao tiếp với server
"""
import socket
import json
import threading

class OnlineClient:
    def __init__(self, host, port=12347):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.username = None
        self.role = None  # 'host' hoặc 'guest'
        self.color = None  # 'white' hoặc 'black'
        self.error_message = None  # Lưu error message từ server
        
        # Message queue
        self.messages = []
        self.message_lock = threading.Lock()
        
        # Message callback (for real-time handling)
        self.message_callback = None
        
        # Receive thread
        self.receive_thread = None
        self.running = False
    
    def set_message_callback(self, callback):
        """
        Đặt callback để xử lý messages real-time
        
        Args:
            callback: Function(message_dict) được gọi khi nhận message
        """
        self.message_callback = callback
    
    def connect(self, username="Player"):
        """
        Kết nối đến server
        
        Args:
            username: Tên người chơi
            
        Returns:
            bool: True nếu kết nối thành công
        """
        try:
            print(f"🔌 Đang kết nối đến {self.host}:{self.port}...")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10s timeout
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(None)  # Bỏ timeout sau khi connect
            
            self.connected = True
            self.username = username
            self.running = True
            
            # Start receive thread
            self.receive_thread = threading.Thread(
                target=self._receive_loop,
                daemon=True
            )
            self.receive_thread.start()
            
            print(f"✅ Đã kết nối thành công!")
            
            # Đợi nhận role từ server (hoặc error nếu phòng đầy)
            import time
            timeout = 5
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Check for error message first
                error_msg = None
                with self.message_lock:
                    for msg in list(self.messages):
                        if msg.get('type') == 'error':
                            error_msg = msg
                            self.messages.remove(msg)
                            break
                
                if error_msg:
                    error_code = error_msg.get('error', 'unknown')
                    error_text = error_msg.get('message', 'Unknown error')
                    
                    if error_code == 'room_full':
                        print(f"❌ Phòng đã đầy: {error_text}")
                        self.error_message = error_text
                        self.disconnect()
                        return False
                    else:
                        print(f"❌ Server error: {error_text}")
                        self.error_message = error_text
                        self.disconnect()
                        return False
                
                # Check for role message
                role_msg = None
                with self.message_lock:
                    for msg in list(self.messages):
                        if msg.get('type') == 'role':
                            role_msg = msg
                            self.messages.remove(msg)
                            break
                
                if role_msg:
                    self.role = role_msg.get('role')
                    self.color = role_msg.get('color')
                    print(f"🎮 Vai trò: {self.role} ({self.color})")
                    return True
                
                time.sleep(0.1)
            
            print("❌ Timeout chờ phản hồi từ server")
            self.error_message = "Timeout chờ phản hồi từ server"
            self.disconnect()
            return False
            
        except socket.timeout:
            print(f"❌ Timeout khi kết nối đến {self.host}:{self.port}")
            return False
        except ConnectionRefusedError:
            print(f"❌ Server từ chối kết nối. Kiểm tra server có đang chạy không?")
            return False
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
            return False
    
    def _receive_loop(self):
        """Thread nhận messages từ server"""
        buffer = ""
        
        try:
            while self.running and self.connected:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    print("❌ Server đã ngắt kết nối")
                    self.connected = False
                    break
                
                buffer += data
                
                # Xử lý từng message
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            msg = json.loads(line)
                            
                            # Call callback if set
                            if self.message_callback:
                                try:
                                    self.message_callback(msg)
                                except Exception as e:
                                    print(f"⚠️ Lỗi trong callback: {e}")
                            
                            # Add to queue
                            with self.message_lock:
                                self.messages.append(msg)
                            
                            # Debug
                            msg_type = msg.get('type', 'unknown')
                            print(f"📥 Nhận: {msg_type}")
                            
                        except json.JSONDecodeError as e:
                            print(f"⚠️ Lỗi parse JSON: {e}")
                            
        except Exception as e:
            if self.running:
                print(f"❌ Lỗi nhận data: {e}")
            self.connected = False
    
    def send(self, data):
        """
        Gửi data đến server
        
        Args:
            data: dict - Data cần gửi
            
        Returns:
            bool: True nếu gửi thành công
        """
        if not self.connected:
            print("⚠️ Chưa kết nối đến server")
            return False
        
        try:
            message = json.dumps(data) + '\n'
            self.socket.sendall(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"❌ Lỗi gửi data: {e}")
            self.connected = False
            return False
    
    def send_move(self, from_pos, to_pos, piece, captured_piece=None):
        """Gửi nước đi"""
        return self.send({
            'type': 'move',
            'from_pos': from_pos,
            'to_pos': to_pos,
            'piece': piece,
            'captured_piece': captured_piece
        })
    
    def send_chat(self, message):
        """Gửi chat message"""
        return self.send({
            'type': 'chat',
            'username': self.username,
            'message': message
        })
    
    def get_messages(self):
        """
        Lấy tất cả messages đã nhận
        
        Returns:
            list: Danh sách messages
        """
        with self.message_lock:
            msgs = self.messages.copy()
            self.messages.clear()
            return msgs
    
    def wait_for_message(self, msg_type, timeout=None):
        """
        Đợi message với type cụ thể
        
        Args:
            msg_type: Loại message cần đợi
            timeout: Timeout (giây), None = đợi vô hạn
            
        Returns:
            dict: Message, hoặc None nếu timeout
        """
        import time
        start_time = time.time()
        
        while True:
            with self.message_lock:
                for msg in self.messages:
                    if msg.get('type') == msg_type:
                        self.messages.remove(msg)
                        return msg
            
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                return None
            
            time.sleep(0.1)
    
    def disconnect(self):
        """Ngắt kết nối"""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        print("🔌 Đã ngắt kết nối")
    
    def is_connected(self):
        """Check xem có đang kết nối không"""
        return self.connected
    
    def __del__(self):
        """Cleanup"""
        self.disconnect()


if __name__ == "__main__":
    # Test client
    print("=== ONLINE CLIENT TEST ===")
    
    host = input("Server host (localhost): ").strip() or "localhost"
    port = input("Server port (12347): ").strip() or "12347"
    
    client = OnlineClient(host, int(port))
    
    if client.connect("TestPlayer"):
        print(f"\n✅ Kết nối thành công!")
        print(f"Role: {client.role}")
        print(f"Color: {client.color}")
        
        # Test send message
        client.send_chat("Hello from test client!")
        
        input("\nNhấn Enter để ngắt kết nối...")
        client.disconnect()
    else:
        print("\n❌ Không thể kết nối")
