"""
HostWaitingScreen - Màn hình chờ đối thủ cho host
Hiển thị URL Ngrok để gửi cho bạn bè
"""
import pygame

class HostWaitingScreen:
    def __init__(self, screen, ngrok_url, user, room_id=""):
        self.screen = screen
        self.ngrok_url = ngrok_url
        self.user = user
        self.room_id = room_id
        self.running = True
        self.player_joined = False
        
        # Fonts
        try:
            self.font_big = pygame.font.Font(None, 56)
            self.font_medium = pygame.font.Font(None, 40)
            self.font_small = pygame.font.Font(None, 30)
            self.font_tiny = pygame.font.Font(None, 24)
        except:
            self.font_big = pygame.font.SysFont('arial', 56)
            self.font_medium = pygame.font.SysFont('arial', 40)
            self.font_small = pygame.font.SysFont('arial', 30)
            self.font_tiny = pygame.font.SysFont('arial', 24)
        
        # Copy button
        self.copy_button = pygame.Rect(0, 0, 220, 70)
        self.copy_button.center = (screen.get_width() // 2, 430)
        
        # Cancel button
        self.cancel_button = pygame.Rect(50, screen.get_height() - 80, 200, 60)
        
        # Animation
        self.dots = 0
        self.dot_timer = 0
        self.copied_timer = 0
        self.show_copied = False
        
        # Colors
        self.bg_color = (40, 40, 60)
        self.accent_color = (100, 200, 100)
    
    def set_player_joined(self, player_name):
        """Gọi hàm này khi có player join"""
        self.player_joined = True
        self.joined_player = player_name
    
    def run(self):
        """
        Main loop - đợi đối thủ join
        
        Returns:
            bool: True nếu có người join, False nếu cancel
        """
        clock = pygame.time.Clock()
        
        while self.running:
            dt = clock.tick(60) / 1000.0
            
            # Animation dots
            self.dot_timer += dt
            if self.dot_timer >= 0.5:
                self.dots = (self.dots + 1) % 4
                self.dot_timer = 0
            
            # Copied message timer
            if self.show_copied:
                self.copied_timer += dt
                if self.copied_timer >= 2.0:
                    self.show_copied = False
                    self.copied_timer = 0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    
                    # Click Copy button
                    if self.copy_button.collidepoint(x, y):
                        self.copy_to_clipboard()
                    
                    # Click Cancel button
                    if self.cancel_button.collidepoint(x, y):
                        return False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    elif event.key == pygame.K_c and (event.mod & pygame.KMOD_CTRL):
                        # Ctrl+C = Copy
                        self.copy_to_clipboard()
            
            # Check nếu có player joined
            if self.player_joined:
                # TODO: Có thể thêm animation hiển thị tên người join
                return True
            
            self.draw()
            pygame.display.flip()
        
        return False
    
    def copy_to_clipboard(self):
        """Copy URL vào clipboard"""
        try:
            try:
                import pyperclip
                pyperclip.copy(self.ngrok_url)
                self.show_copied = True
                self.copied_timer = 0
                print(f"Da copy URL vào clipboard: {self.ngrok_url}")
            except ImportError:
                # Fallback
                try:
                    import pygame.scrap
                    pygame.scrap.init()
                    pygame.scrap.put(pygame.SCRAP_TEXT, self.ngrok_url.encode('utf-8'))
                    self.show_copied = True
                    self.copied_timer = 0
                    print(f"Da copy URL: {self.ngrok_url}")
                except:
                    print("⚠️ Không thể copy. Vui lòng chọn URL bằng chuột")
        except Exception as e:
            print(f"⚠️ Lỗi copy: {e}")
    
    def draw(self):
        """Vẽ UI"""
        self.screen.fill(self.bg_color)
        
        # Title với animation
        title_text = "Dang cho doi thu" + "." * self.dots
        title = self.font_big.render(title_text, True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Host info
        info1 = self.font_medium.render(f"Host: {self.user['username']}", True, (200, 200, 200))
        info1_rect = info1.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(info1, info1_rect)
        
        if self.room_id:
            info2 = self.font_small.render(f"Phong: {self.room_id}", True, (180, 180, 180))
            info2_rect = info2.get_rect(center=(self.screen.get_width() // 2, 190))
            self.screen.blit(info2, info2_rect)
        
        # Hướng dẫn
        guide = self.font_medium.render("Gui URL nay cho ban be:", True, (255, 255, 100))
        guide_rect = guide.get_rect(center=(self.screen.get_width() // 2, 260))
        self.screen.blit(guide, guide_rect)
        
        # URL Box - Nổi bật
        url_box_width = min(self.screen.get_width() - 100, 900)
        url_box = pygame.Rect(
            (self.screen.get_width() - url_box_width) // 2,
            310,
            url_box_width,
            70
        )
        
        # Vẽ shadow
        shadow_box = url_box.copy()
        shadow_box.x += 4
        shadow_box.y += 4
        pygame.draw.rect(self.screen, (20, 20, 30), shadow_box, border_radius=10)
        
        # Vẽ box chính
        pygame.draw.rect(self.screen, (70, 70, 90), url_box, border_radius=10)
        pygame.draw.rect(self.screen, self.accent_color, url_box, 4, border_radius=10)
        
        # URL text
        url_text = self.font_medium.render(self.ngrok_url, True, self.accent_color)
        url_text_rect = url_text.get_rect(center=url_box.center)
        
        # Nếu text quá dài, scale xuống
        if url_text.get_width() > url_box.width - 20:
            scale_factor = (url_box.width - 20) / url_text.get_width()
            new_size = int(40 * scale_factor)
            scaled_font = pygame.font.Font(None, new_size)
            url_text = scaled_font.render(self.ngrok_url, True, self.accent_color)
            url_text_rect = url_text.get_rect(center=url_box.center)
        
        self.screen.blit(url_text, url_text_rect)
        
        # Copy Button
        mouse_pos = pygame.mouse.get_pos()
        button_color = (70, 180, 70) if self.copy_button.collidepoint(mouse_pos) else (50, 150, 50)
        pygame.draw.rect(self.screen, button_color, self.copy_button, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.copy_button, 3, border_radius=10)
        
        copy_text = self.font_medium.render("Copy URL", True, (255, 255, 255))
        copy_text_rect = copy_text.get_rect(center=self.copy_button.center)
        self.screen.blit(copy_text, copy_text_rect)
        
        # Copied message
        if self.show_copied:
            copied_msg = self.font_small.render("Da copy!", True, (100, 255, 100))
            copied_rect = copied_msg.get_rect(center=(self.screen.get_width() // 2, 510))
            self.screen.blit(copied_msg, copied_rect)
        
        # Hướng dẫn chi tiết
        instructions = [
            "1. Click 'Copy URL' hoac nhan Ctrl+C",
            "2. Gui URL cho ban qua Zalo/Discord/Messenger",
            "3. Ban se dung URL nay de Join vao game"
        ]
        
        y_offset = 560
        for instruction in instructions:
            inst_text = self.font_small.render(instruction, True, (180, 180, 180))
            inst_rect = inst_text.get_rect(center=(self.screen.get_width() // 2, y_offset))
            self.screen.blit(inst_text, inst_rect)
            y_offset += 40
        
        # Cancel button
        cancel_color = (150, 70, 70) if self.cancel_button.collidepoint(mouse_pos) else (100, 50, 50)
        pygame.draw.rect(self.screen, cancel_color, self.cancel_button, border_radius=8)
        pygame.draw.rect(self.screen, (255, 255, 255), self.cancel_button, 2, border_radius=8)
        
        cancel_text = self.font_small.render("Huy", True, (255, 255, 255))
        cancel_text_rect = cancel_text.get_rect(center=self.cancel_button.center)
        self.screen.blit(cancel_text, cancel_text_rect)
        
        # ESC hint
        esc_text = self.font_tiny.render("Nhan ESC de huy", True, (150, 150, 150))
        self.screen.blit(esc_text, (self.screen.get_width() - 200, self.screen.get_height() - 30))
