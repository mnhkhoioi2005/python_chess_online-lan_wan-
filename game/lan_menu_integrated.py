import pygame
import sys
import threading
import time
import socket
from game.network_server import ChessServer
from game.online_game import OnlineChessGame
import os

class LANMenu:
    def __init__(self, screen_width, screen_height):
        # (SỬA) Không cần set_mode, main.py đã quản lý
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.get_surface() # Lấy màn hình có sẵn
        pygame.display.set_caption("LAN Chess Game")
        self.clock = pygame.time.Clock()
        
        # --- (MỚI) Sao chép màu sắc và font từ menu.py ---
        self.COLOR_BG = (245, 245, 245)
        self.COLOR_TITLE = (50, 50, 50)
        self.COLOR_TEXT_LIGHT = (255, 255, 255)
        self.COLOR_TEXT_DARK = (40, 40, 40)
        self.COLOR_STATUS = (230, 126, 34) # Màu cam cho status

        self.BTN_GREEN = (46, 204, 113)
        self.BTN_GREEN_HOVER = (39, 174, 96)
        self.BTN_BLUE = (52, 152, 219)
        self.BTN_BLUE_HOVER = (41, 128, 185)
        self.BTN_GRAY = (149, 165, 166)
        self.BTN_GRAY_HOVER = (127, 140, 141)
        self.BTN_RED = (231, 76, 60)
        
        self.load_assets() # Tải font và bg

        # Buttons
        button_width, button_height = 300, 60
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        self.host_button_rect = pygame.Rect(center_x - button_width//2, center_y - 60, button_width, button_height)
        self.join_button_rect = pygame.Rect(center_x - button_width//2, center_y + 20, button_width, button_height)
        self.back_button_rect = pygame.Rect(center_x - button_width//2, center_y + 100, button_width, button_height)
        
        self.servers = []
        self.scanning = False
        self.hosting = False
        self.status_message = ""
        self.local_ip = self.get_local_ip()
        
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"
            
    def load_assets(self):
        """(MỚI) Tải font và ảnh nền"""
        font_path = os.path.join("assets", "fonts")
        img_path = os.path.join("assets", "images")

        try:
            self.title_font = pygame.font.Font(os.path.join(font_path, "Roboto-Bold.ttf"), 80)
            self.button_font = pygame.font.Font(os.path.join(font_path, "Roboto-Regular.ttf"), 40)
            self.text_font = pygame.font.Font(os.path.join(font_path, "Roboto-Regular.ttf"), 30)
            self.ip_font = pygame.font.Font(os.path.join(font_path, "Roboto-Bold.ttf"), 50)
        except pygame.error:
            print("Không tìm thấy font. Dùng font mặc định.")
            self.title_font = pygame.font.Font(None, 80)
            self.button_font = pygame.font.Font(None, 50)
            self.text_font = pygame.font.Font(None, 40)
            self.ip_font = pygame.font.Font(None, 60)
            
        try:
            self.bg_image = pygame.image.load(os.path.join(img_path, "menu_bg.png"))
            self.bg_image = pygame.transform.scale(self.bg_image, (self.screen_width, self.screen_height))
        except pygame.error:
            print("Không tìm thấy ảnh nền. Dùng màu nền.")
            self.bg_image = None
            
    def draw_button(self, rect, text, base_color, hover_color, mouse_pos):
        """(MỚI) Hàm vẽ nút bo tròn"""
        is_hovered = rect.collidepoint(mouse_pos)
        color = hover_color if is_hovered else base_color
        pygame.draw.rect(self.screen, color, rect, border_radius=15)
        btn_text = self.button_font.render(text, True, self.COLOR_TEXT_LIGHT)
        text_rect = btn_text.get_rect(center=rect.center)
        self.screen.blit(btn_text, text_rect)
    
    def draw(self, mouse_pos):
        """(SỬA) Vẽ giao diện đẹp"""
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(self.COLOR_BG)
        
        # Title
        title_text = self.title_font.render("LAN MULTIPLAYER", True, self.COLOR_TITLE)
        title_rect = title_text.get_rect(center=(self.screen_width//2, 100))
        self.screen.blit(title_text, title_rect)
        
        # IP info
        ip_text = self.ip_font.render(f"Your IP: {self.local_ip}", True, self.BTN_RED)
        ip_rect = ip_text.get_rect(center=(self.screen_width//2, 180))
        self.screen.blit(ip_text, ip_rect)
        
        # Status message
        if self.status_message:
            status_text = self.text_font.render(self.status_message, True, self.COLOR_STATUS)
            status_rect = status_text.get_rect(center=(self.screen_width//2, 240))
            self.screen.blit(status_text, status_rect)
        
        # Nút bấm
        self.draw_button(self.host_button_rect, "HOST GAME", self.BTN_GREEN, self.BTN_GREEN_HOVER, mouse_pos)
        self.draw_button(self.join_button_rect, "JOIN GAME", self.BTN_BLUE, self.BTN_BLUE_HOVER, mouse_pos)
        self.draw_button(self.back_button_rect, "BACK", self.BTN_GRAY, self.BTN_GRAY_HOVER, mouse_pos)
        
        pygame.display.flip()
    
    def host_game(self):
        """Host game và mở bàn cờ"""
        self.hosting = True
        self.status_message = "Starting server... Please wait"
        self.draw(pygame.mouse.get_pos())
        
        server_thread = threading.Thread(
            target=self.start_server_thread, 
            args=(self.local_ip, 12345), 
            daemon=True
        )
        server_thread.start()
        time.sleep(1)
        
        self.status_message = "Server ready! Waiting for opponent..."
        self.draw(pygame.mouse.get_pos())
        
        print("=" * 50)
        print("🎮 HOSTING CHESS GAME")
        print(f"📍 Your IP Address: {self.local_ip}")
        print("✅ Server started successfully! Opening board...")
        
        try:
            game = OnlineChessGame(server_ip=self.local_ip, is_host=True)
            game.run()
        except Exception as e:
            print(f"❌ Host game error: {e}")
            import traceback
            traceback.print_exc()
        
        print("🏁 Game ended!")
        self.hosting = False
        self.status_message = ""
    
    def start_server_thread(self, host, port):
        """Start server in thread"""
        server = ChessServer(host, port)
        try:
            server.start()
        except Exception as e:
            print(f"Server error: {e}")
    
    def join_game(self):
        """Scan và join game"""
        self.scanning = True
        self.status_message = "Scanning for games on LAN..."
        self.draw(pygame.mouse.get_pos())
        
        print("🔍 JOINING CHESS GAME")
        print("📡 Enter IP address to connect...")
        
        self.scanning = False
        self.status_message = "Enter IP address to connect"
        self.draw(pygame.mouse.get_pos())
        ip = self.get_manual_ip()
        if ip:
            print(f"🔗 Connecting to {ip}...")
            self.connect_to_game(ip)
        
        self.status_message = ""
    
    def get_manual_ip(self):
        """Nhập IP thủ công"""
        ip = ""
        input_active = True
        
        while input_active:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return ip if ip else "localhost"
                    elif event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_BACKSPACE:
                        ip = ip[:-1]
                    else:
                        # Chỉ chấp nhận số và dấu chấm
                        char = event.unicode
                        if char.isdigit() or char == '.':
                            ip += char
            
            # Vẽ dialog nhập IP
            if self.bg_image:
                self.screen.blit(self.bg_image, (0, 0))
            else:
                self.screen.fill(self.COLOR_BG)
            
            title_text = self.ip_font.render("Enter Server IP:", True, self.COLOR_TITLE)
            title_rect = title_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 100))
            self.screen.blit(title_text, title_rect)
            
            hint_text = self.text_font.render("Press Enter to connect, Esc to cancel", True, self.COLOR_TEXT_DARK)
            hint_rect = hint_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
            self.screen.blit(hint_text, hint_rect)
            
            # Input box
            input_rect = pygame.Rect(self.screen_width//2 - 200, self.screen_height//2, 400, 60)
            pygame.draw.rect(self.screen, (255, 255, 255), input_rect, border_radius=10)
            pygame.draw.rect(self.screen, self.COLOR_TITLE, input_rect, 2, border_radius=10)
            
            display_ip = ip if ip else "localhost"
            ip_text = self.ip_font.render(display_ip, True, self.COLOR_TITLE)
            self.screen.blit(ip_text, (input_rect.x + 15, input_rect.y + 10))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return None
    
    def show_server_list(self, servers):
        """Show list of found servers"""
        selected = 0
        
        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(servers)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(servers)
                    elif event.key == pygame.K_RETURN:
                        return servers[selected]['ip']
                    elif event.key == pygame.K_ESCAPE:
                        return None
            
            if self.bg_image:
                self.screen.blit(self.bg_image, (0, 0))
            else:
                self.screen.fill(self.COLOR_BG)
            
            title_text = self.ip_font.render("Select Server:", True, self.COLOR_TITLE)
            title_rect = title_text.get_rect(center=(self.screen_width//2, 150))
            self.screen.blit(title_text, title_rect)
            
            for i, server in enumerate(servers):
                y_pos = 250 + i * 70
                server_rect = pygame.Rect(self.screen_width//2 - 250, y_pos, 500, 60)
                
                is_hovered = server_rect.collidepoint(mouse_pos)
                is_selected = (i == selected)
                
                base_color = self.BTN_GREEN if is_selected else (255, 255, 255)
                hover_color = self.BTN_GREEN_HOVER if is_selected else (240, 240, 240)
                
                color = hover_color if is_hovered else base_color
                text_color = self.COLOR_TEXT_LIGHT if is_selected else self.COLOR_TEXT_DARK
                
                pygame.draw.rect(self.screen, color, server_rect, border_radius=10)
                pygame.draw.rect(self.screen, self.COLOR_TITLE, server_rect, 2, border_radius=10)
                
                server_text = self.button_font.render(f"{server['name']} ({server['ip']})", True, text_color)
                text_rect = server_text.get_rect(center=server_rect.center)
                self.screen.blit(server_text, text_rect)
            
            pygame.display.flip()
    
    def connect_to_game(self, ip):
        """Connect to game"""
        print("🎲 Opening chess board...")
        try:
            game = OnlineChessGame(server_ip=ip, is_host=False)
            game.run()
            print("🏁 Game ended!")
        except Exception as e:
            print(f"❌ Connection error: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_click(self, pos):
        if self.host_button_rect.collidepoint(pos):
            return "host"
        elif self.join_button_rect.collidepoint(pos):
            return "join"
        elif self.back_button_rect.collidepoint(pos):
            return "back"
        return None
    
    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    result = self.handle_click(event.pos)
                    if result == "host":
                        self.host_game()
                        return "game_ended"
                    elif result == "join":
                        self.join_game()
                        return "game_ended"
                    elif result == "back":
                        return "back"
            
            self.draw(mouse_pos)
            pygame.time.Clock().tick(60)
        
        return None