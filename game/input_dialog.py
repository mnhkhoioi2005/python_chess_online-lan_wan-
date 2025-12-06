"""
InputDialog - Hop thoai nhap text trong Pygame
Ho tro: nhap text, paste tu clipboard, Enter/ESC
"""
import pygame
import pygame.scrap

class InputDialog:
    def __init__(self, screen, title="Nhap URL Server", default_text="", placeholder="Vi du: 0.tcp.ngrok.io:12345"):
        self.screen = screen
        self.width = 700
        self.height = 350
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2
        
        self.title = title
        self.text = default_text
        self.placeholder = placeholder
        self.active = True
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # Fonts
        try:
            self.font_title = pygame.font.Font(None, 48)
            self.font_text = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 26)
        except:
            self.font_title = pygame.font.SysFont('arial', 48)
            self.font_text = pygame.font.SysFont('arial', 36)
            self.font_small = pygame.font.SysFont('arial', 26)
        
        # Colors
        self.bg_color = (50, 50, 70)
        self.input_bg = (70, 70, 90)
        self.input_active = (90, 90, 120)
        self.text_color = (255, 255, 255)
        self.placeholder_color = (120, 120, 140)
        self.button_color = (50, 150, 50)
        self.button_hover = (70, 180, 70)
        
        # Buttons
        self.ok_button = pygame.Rect(self.x + 150, self.y + 260, 140, 60)
        self.cancel_button = pygame.Rect(self.x + 410, self.y + 260, 140, 60)
        self.paste_button = pygame.Rect(self.x + 570, self.y + 145, 110, 50)
    
    def run(self):
        """
        Chạy dialog và trả về text hoặc None
        
        Returns:
            str: Text đã nhập, hoặc None nếu Cancel
        """
        clock = pygame.time.Clock()
        
        while self.active:
            dt = clock.tick(60) / 1000.0
            self.cursor_timer += dt
            
            if self.cursor_timer >= 0.5:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        # Enter = OK
                        return self.text.strip() if self.text.strip() else None
                    elif event.key == pygame.K_ESCAPE:
                        # ESC = Cancel
                        return None
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    elif event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
                        # Ctrl+V = Paste
                        try:
                            # Try pyperclip first
                            try:
                                import pyperclip
                                clipboard = pyperclip.paste()
                                self.text += clipboard
                            except ImportError:
                                # Fallback to pygame (chỉ hoạt động trên một số platform)
                                try:
                                    pygame.scrap.init()
                                    clipboard = pygame.scrap.get(pygame.SCRAP_TEXT)
                                    if clipboard:
                                        self.text += clipboard.decode('utf-8', errors='ignore')
                                except:
                                    pass
                        except:
                            pass
                    else:
                        # Thêm ký tự
                        if event.unicode.isprintable():
                            self.text += event.unicode
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    
                    # Click OK
                    if self.ok_button.collidepoint(x, y):
                        return self.text.strip() if self.text.strip() else None
                    
                    # Click Cancel
                    if self.cancel_button.collidepoint(x, y):
                        return None
                    
                    # Click Paste
                    if self.paste_button.collidepoint(x, y):
                        try:
                            try:
                                import pyperclip
                                self.text = pyperclip.paste()
                            except ImportError:
                                try:
                                    pygame.scrap.init()
                                    clipboard = pygame.scrap.get(pygame.SCRAP_TEXT)
                                    if clipboard:
                                        self.text = clipboard.decode('utf-8', errors='ignore')
                                except:
                                    pass
                        except:
                            pass
            
            self.draw()
            pygame.display.flip()
        
        return None
    
    def draw(self):
        """Vẽ dialog"""
        # Làm tối background
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Dialog box
        dialog_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, self.bg_color, dialog_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), dialog_rect, 3)
        
        # Title
        title_surf = self.font_title.render(self.title, True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.x + self.width // 2, self.y + 50))
        self.screen.blit(title_surf, title_rect)
        
        # Hint text
        hint = self.font_small.render(self.placeholder, True, (180, 180, 180))
        self.screen.blit(hint, (self.x + 20, self.y + 105))
        
        # Input box
        input_rect = pygame.Rect(self.x + 20, self.y + 145, 540, 50)
        pygame.draw.rect(self.screen, self.input_active, input_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), input_rect, 2)
        
        # Text trong input
        if self.text:
            text_surf = self.font_text.render(self.text, True, self.text_color)
        else:
            # Placeholder khi rỗng
            text_surf = self.font_text.render(self.placeholder, True, self.placeholder_color)
        
        # Scroll nếu text dài
        text_x = input_rect.x + 10
        if text_surf.get_width() > input_rect.width - 20:
            text_x = input_rect.right - text_surf.get_width() - 10
        self.screen.blit(text_surf, (text_x, input_rect.y + 10))
        
        # Cursor (chỉ hiện khi có text)
        if self.text and self.cursor_visible:
            cursor_x = min(text_x + text_surf.get_width() + 2, input_rect.right - 5)
            pygame.draw.line(self.screen, self.text_color,
                           (cursor_x, input_rect.y + 10),
                           (cursor_x, input_rect.bottom - 10), 2)
        
        # Button Paste
        mouse_pos = pygame.mouse.get_pos()
        paste_color = self.button_hover if self.paste_button.collidepoint(mouse_pos) else (100, 100, 150)
        pygame.draw.rect(self.screen, paste_color, self.paste_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.paste_button, 2)
        paste_text = self.font_small.render("Paste", True, self.text_color)
        paste_text_rect = paste_text.get_rect(center=self.paste_button.center)
        self.screen.blit(paste_text, paste_text_rect)
        
        # Hint cho Ctrl+V
        hint_cv = self.font_small.render("Ctrl+V", True, (150, 150, 150))
        self.screen.blit(hint_cv, (self.x + 580, self.y + 200))
        
        # Button OK
        ok_color = self.button_hover if self.ok_button.collidepoint(mouse_pos) else self.button_color
        pygame.draw.rect(self.screen, ok_color, self.ok_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.ok_button, 2)
        ok_text = self.font_text.render("OK", True, self.text_color)
        ok_text_rect = ok_text.get_rect(center=self.ok_button.center)
        self.screen.blit(ok_text, ok_text_rect)
        
        # Button Cancel
        cancel_color = (150, 50, 50) if self.cancel_button.collidepoint(mouse_pos) else (100, 50, 50)
        pygame.draw.rect(self.screen, cancel_color, self.cancel_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.cancel_button, 2)
        cancel_text = self.font_text.render("Huy", True, self.text_color)
        cancel_text_rect = cancel_text.get_rect(center=self.cancel_button.center)
        self.screen.blit(cancel_text, cancel_text_rect)
        
        # Hint: Enter = OK, ESC = Cancel
        hint_keys = self.font_small.render("Enter = OK  |  ESC = Huy", True, (150, 150, 150))
        hint_keys_rect = hint_keys.get_rect(center=(self.x + self.width // 2, self.y + self.height - 20))
        self.screen.blit(hint_keys, hint_keys_rect)
