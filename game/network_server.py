import socket
import threading
import json
import time

class ChessServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.running = False
    
    def start(self):
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(2)
            self.running = True
            print(f"Server started on {self.host}:{self.port}")
            print("Waiting for players...")
            
            while self.running and len(self.clients) < 2:
                client_socket, addr = self.socket.accept()
                self.clients.append(client_socket)
                print(f"Player {len(self.clients)} connected from {addr}")
                
                player_color = 'white' if len(self.clients) == 1 else 'black'
                self.send_to_client(client_socket, {
                    'type': 'player_info',
                    'color': player_color,
                    'player_number': len(self.clients)
                })
                
                threading.Thread(target=self.handle_client, args=(client_socket, len(self.clients))).start()
            
            if len(self.clients) == 2:
                print("Game started! Both players connected.")
                self.broadcast({'type': 'game_start'})
                
        except Exception as e:
            if self.running:
                print(f"Server error: {e}")
    
    def handle_client(self, client_socket, player_num):
        """(SỬA) Dùng buffer để xử lý các tin nhắn bị dính liền"""
        buffer = ""
        try:
            while self.running:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                
                while '\n' in buffer:
                    message_str, buffer = buffer.split('\n', 1)
                    
                    try:
                        message = json.loads(message_str)
                        self.process_message(message, client_socket, player_num)
                    except json.JSONDecodeError:
                        print(f"Lỗi đọc JSON (tin nhắn bị hỏng): {message_str}")
                
        except Exception as e:
            if self.running:
                print(f"Client {player_num} error: {e}")
        finally:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()
            print(f"Client {player_num} disconnected.")
            # (MỚI) Báo cho người chơi còn lại biết
            self.broadcast({'type': 'game_over', 'winner': 'you', 'reason': 'opponent_disconnected'})
    
    def process_message(self, message, sender_socket, player_num):
        """(SỬA) Đã sửa lỗi logic. Server phải là trọng tài."""
        
        msg_type = message.get('type')
        
        if msg_type == 'move':
            # Chỉ broadcast nước đi, không cần làm gì khác
            self.broadcast(message, exclude=sender_socket)
            print(f"Player {player_num} moved: {message['from_pos']} -> {message['to_pos']}")
        
        elif msg_type == 'surrender':
            # Báo cho người kia thắng
            self.broadcast({'type': 'game_over', 'winner': 'you', 'reason': 'opponent_surrendered'}, exclude=sender_socket)
            # Báo cho người gửi biết họ đã thua
            self.send_to_client(sender_socket, {'type': 'game_over', 'winner': 'opponent', 'reason': 'you_surrendered'})
    
    def send_to_client(self, client_socket, message):
        """(SỬA) Thêm ký tự \n vào cuối mỗi tin nhắn"""
        try:
            client_socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
        except:
            # Client có thể đã ngắt kết nối
            if client_socket in self.clients:
                self.clients.remove(client_socket)
    
    def broadcast(self, message, exclude=None):
        for client in self.clients[:]: # Dùng [:] để tạo bản sao
            if client != exclude:
                self.send_to_client(client, message)
    
    def stop(self):
        self.running = False
        for client in self.clients:
            client.close()
        self.socket.close()
        print("Server shut down.")

if __name__ == "__main__":
    server = ChessServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()