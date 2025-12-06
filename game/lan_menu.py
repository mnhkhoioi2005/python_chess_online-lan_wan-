import pygame
import sys
from .lan_discovery import LANDiscovery
import threading
import time

class LANMenu:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("LAN Game Setup")
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.discovery = LANDiscovery()
        self.servers = []
        self.selected_server = None
        self.scanning = False
        
    def run(self):
        clock = pygame.time.Clock()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:  # Host game
                        return "host"
                    elif event.key == pygame.K_2:  # Scan for games
                        self.start_scan()
                    elif event.key == pygame.K_3:  # Manual IP
                        return "manual"
                    elif event.key == pygame.K_ESCAPE:
                        return None
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_pos = pygame.mouse.get_pos()
                        selected = self.handle_server_click(mouse_pos)
                        if selected:
                            return selected
            
            self.draw()
            pygame.display.flip()
            clock.tick(60)
    
    def start_scan(self):
        if not self.scanning:
            self.scanning = True
            self.servers = []
            threading.Thread(target=self.scan_thread, daemon=True).start()
    
    def scan_thread(self):
        self.servers = self.discovery.scan_for_servers(timeout=3)
        self.scanning = False
    
    def handle_server_click(self, mouse_pos):
        # Kiểm tra click vào server list
        start_y = 300
        for i, server in enumerate(self.servers):
            rect = pygame.Rect(50, start_y + i * 40, 700, 35)
            if rect.collidepoint(mouse_pos):
                return server['ip']
        return None
    
    def draw(self):
        self.screen.fill((40, 40, 40))
        
        # Title
        title = self.font.render("LAN Chess Game", True, (255, 255, 255))
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 50))
        
        # Options
        options = [
            "1. Host a Game (Others can join you)",
            "2. Scan for Games on LAN",
            "3. Manual IP Entry",
            "",
            "ESC. Back to Main Menu"
        ]
        
        y = 150
        for option in options:
            color = (200, 200, 200) if option else (100, 100, 100)
            text = self.small_font.render(option, True, color)
            self.screen.blit(text, (50, y))
            y += 30
        
        # Server list
        if self.scanning:
            scan_text = self.small_font.render("Scanning for games...", True, (255, 255, 0))
            self.screen.blit(scan_text, (50, 280))
        elif self.servers:
            servers_text = self.small_font.render("Found Games (Click to join):", True, (0, 255, 0))
            self.screen.blit(servers_text, (50, 280))
            
            y = 300
            for server in self.servers:
                server_text = f"{server['name']} - {server['ip']}:{server['port']}"
                text = self.small_font.render(server_text, True, (255, 255, 255))
                
                # Highlight on hover
                mouse_pos = pygame.mouse.get_pos()
                rect = pygame.Rect(50, y, 700, 35)
                if rect.collidepoint(mouse_pos):
                    pygame.draw.rect(self.screen, (60, 60, 60), rect)
                
                self.screen.blit(text, (55, y + 5))
                y += 40
        elif hasattr(self, 'servers') and len(self.servers) == 0 and not self.scanning:
            no_games = self.small_font.render("No games found. Try scanning again or host your own.", True, (255, 100, 100))
            self.screen.blit(no_games, (50, 280))
