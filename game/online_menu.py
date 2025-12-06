"""
OnlineMenu - Menu chọn Host hoặc Join game online
Tích hợp Ngrok để chơi qua Internet
"""
import pygame
import threading
import time
from game.ngrok_helper import NgrokHelper
from game.lobby_server import SimpleLobbyServer
from game.online_client import OnlineClient
from game.input_dialog import InputDialog
from game.host_waiting_screen import HostWaitingScreen

class OnlineMenu:
    def __init__(self, user):
        self.screen = pygame.display.get_surface()
        self.user = user
        self.ngrok = None
        self.server = None
        self.client = None
        
        # Fonts
        try:
            self.font_big = pygame.font.Font(None, 70)
            self.font_medium = pygame.font.Font(None, 45)
            self.font_small = pygame.font.Font(None, 32)
        except:
            self.font_big = pygame.font.SysFont('arial', 70)
            self.font_medium = pygame.font.SysFont('arial', 45)
            self.font_small = pygame.font.SysFont('arial', 32)
        
        # Buttons
        center_x = self.screen.get_width() // 2
        self.host_button = pygame.Rect(center_x - 200, 250, 400, 90)
        self.join_button = pygame.Rect(center_x - 200, 370, 400, 90)
        self.back_button = pygame.Rect(center_x - 150, 520, 300, 70)
        
        # Colors
        self.bg_color = (40, 40, 60)
    
    def run(self):
        """Main loop"""
        clock = pygame.time.Clock()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    
                    # Host Game
                    if self.host_button.collidepoint(x, y):
                        result = self.host_game()
                        if result:
                            return result
                    
                    # Join Game
                    if self.join_button.collidepoint(x, y):
                        result = self.join_game()
                        if result:
                            return result
                    
                    # Back
                    if self.back_button.collidepoint(x, y):
                        return None
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
            
            self.draw()
            pygame.display.flip()
            clock.tick(60)
    
    def host_game(self):
        """
        Host game - Tạo server + Tunnel (Serveo > LocalTunnel > Ngrok)
        
        Returns:
            dict hoặc None
        """
        print("\n" + "="*60)
        print("HOSTING ONLINE GAME")
        print("="*60)
        
        # 1. Start Lobby Server
        print("\n1. Starting Server...")
        self.server = SimpleLobbyServer(host='127.0.0.1', port=12347)
        server_thread = threading.Thread(target=self.server.start, daemon=True)
        server_thread.start()
        time.sleep(1)
        print("   SUCCESS: Server ready")
        
        # 2. Create Ngrok tunnel (TCP support)
        print("\n2. Creating tunnel...")
        print("   Starting Ngrok tunnel...")
        
        self.ngrok = NgrokHelper()
        tunnel_url = self.ngrok.start_tunnel(12347)
        
        if not tunnel_url:
            print("   ERROR: Could not create tunnel!")
            self.show_error_message("Cannot create tunnel", 
                                   "All tunnel services failed.\nCheck internet connection.")
            self.cleanup_host()
            return None
        
        print(f"   SUCCESS: Public URL: {tunnel_url}")
        
        # 3. Connect host client đến server của mình
        print("\n3. Connecting host client...")
        self.client = OnlineClient('127.0.0.1', 12347)
        if not self.client.connect(self.user['username']):
            print("   ERROR: Cannot connect to server")
            self.cleanup_host()
            return None
        print("   SUCCESS: Host client connected")
        
        # 4. Hiển thị màn hình chờ với URL
        print("\n4. Waiting for opponent...")
        print(f"   Share this URL: {tunnel_url}")
        
        waiting_screen = HostWaitingScreen(self.screen, tunnel_url, self.user)
        
        # Check trong thread nếu có người join
        def check_game_start():
            msg = self.client.wait_for_message('game_start', timeout=300)  # 5 phút
            if msg:
                waiting_screen.player_joined = True
        
        check_thread = threading.Thread(target=check_game_start, daemon=True)
        check_thread.start()
        
        player_joined = waiting_screen.run()
        
        if player_joined:
            print("\n5. Player joined! Starting game...")
            # Trả về info để main.py khởi động game
            return {
                'mode': 'online_host',
                'client': self.client,
                'user': self.user,
                'ngrok': self.ngrok,
                'server': self.server
            }
        else:
            print("\nCancelled or timeout")
            self.cleanup_host()
            return None
    
    def join_game(self):
        """
        Join game - Nhập URL và kết nối
        
        Returns:
            dict hoặc None
        """
        print("\n" + "="*60)
        print("🔗 JOINING ONLINE GAME")
        print("="*60)
        
        # 1. Hiển thị dialog nhập URL
        dialog = InputDialog(
            self.screen,
            "Nhập URL Server",
            "",
            "Ví dụ: 0.tcp.ngrok.io:12345"
        )
        url = dialog.run()
        
        if not url:
            return None
        
        print(f"\n📡 URL nhập vào: {url}")
        
        # 2. Parse URL
        try:
            if ':' in url:
                host, port = url.rsplit(':', 1)
                port = int(port)
            else:
                host = url
                port = 12347
        except Exception as e:
            print(f"❌ URL không hợp lệ: {e}")
            self.show_error_message("URL không hợp lệ", 
                                   f"Format: host:port")
            return None
        
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        
        # 3. Hiển thị màn hình connecting
        self.show_connecting_message(f"Đang kết nối đến {host}:{port}...")
        
        # 4. Kết nối đến server
        self.client = OnlineClient(host, port)
        
        if self.client.connect(self.user['username']):
            print("✅ Kết nối thành công!")
            
            # Đợi game_start message
            self.show_connecting_message("Đang chờ game bắt đầu...")
            msg = self.client.wait_for_message('game_start', timeout=10)
            
            if msg:
                print("🎉 Game bắt đầu!")
                return {
                    'mode': 'online_guest',
                    'client': self.client,
                    'user': self.user
                }
            else:
                print("❌ Timeout chờ game start")
                self.show_error_message("Timeout", 
                                       "Không nhận được phản hồi từ server")
                self.client.disconnect()
                return None
        else:
            print("❌ Kết nối thất bại!")
            # Hiển thị error message từ client nếu có
            error_msg = self.client.error_message if self.client.error_message else "Kiểm tra URL và thử lại"
            self.show_error_message("Kết nối thất bại", error_msg)
            return None
    
    def cleanup_host(self):
        """Cleanup resources khi host"""
        if self.client:
            self.client.disconnect()
            self.client = None
        
        if self.ngrok:
            self.ngrok.stop_tunnel()
            self.ngrok = None
        
        if self.server:
            self.server.stop()
            self.server = None
    
    def show_error_message(self, title, message):
        """Hiển thị error message"""
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        
        clock = pygame.time.Clock()
        start_time = time.time()
        
        while time.time() - start_time < 3:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return
            
            self.screen.blit(overlay, (0, 0))
            
            # Title
            title_surf = self.font_medium.render(f"{title}", True, (255, 100, 100))
            title_rect = title_surf.get_rect(center=(self.screen.get_width() // 2, 
                                                     self.screen.get_height() // 2 - 30))
            self.screen.blit(title_surf, title_rect)
            
            # Message
            msg_surf = self.font_small.render(message, True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=(self.screen.get_width() // 2,
                                                 self.screen.get_height() // 2 + 20))
            self.screen.blit(msg_surf, msg_rect)
            
            pygame.display.flip()
            clock.tick(60)
    
    def show_connecting_message(self, message):
        """Hiển thị connecting message"""
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        
        self.screen.blit(overlay, (0, 0))
        
        msg_surf = self.font_medium.render(message, True, (255, 255, 100))
        msg_rect = msg_surf.get_rect(center=(self.screen.get_width() // 2,
                                             self.screen.get_height() // 2))
        self.screen.blit(msg_surf, msg_rect)
        
        pygame.display.flip()
        time.sleep(0.5)
    
    def draw(self):
        """Vẽ menu"""
        self.screen.fill(self.bg_color)
        
        # Title
        title = self.font_big.render("ONLINE MULTIPLAYER", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 130))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_small.render("", True, (180, 180, 180))
        subtitle_rect = subtitle.get_rect(center=(self.screen.get_width() // 2, 185))
        self.screen.blit(subtitle, subtitle_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Button Host
        host_color = (70, 180, 70) if self.host_button.collidepoint(mouse_pos) else (50, 150, 50)
        pygame.draw.rect(self.screen, host_color, self.host_button, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.host_button, 3, border_radius=10)
        host_text = self.font_medium.render("Host Game", True, (255, 255, 255))
        host_text_rect = host_text.get_rect(center=self.host_button.center)
        self.screen.blit(host_text, host_text_rect)
        
        # Button Join
        join_color = (70, 150, 180) if self.join_button.collidepoint(mouse_pos) else (50, 100, 150)
        pygame.draw.rect(self.screen, join_color, self.join_button, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.join_button, 3, border_radius=10)
        join_text = self.font_medium.render("Join Game", True, (255, 255, 255))
        join_text_rect = join_text.get_rect(center=self.join_button.center)
        self.screen.blit(join_text, join_text_rect)
        
        # Button Back
        back_color = (150, 70, 70) if self.back_button.collidepoint(mouse_pos) else (100, 50, 50)
        pygame.draw.rect(self.screen, back_color, self.back_button, border_radius=8)
        pygame.draw.rect(self.screen, (255, 255, 255), self.back_button, 3, border_radius=8)
        back_text = self.font_small.render("Quay Lai", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_text_rect)
        
        # Hint
        hint = self.font_small.render("ESC = Quay lai", True, (120, 120, 120))
        self.screen.blit(hint, (20, self.screen.get_height() - 40))
