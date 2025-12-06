import pygame
import sys

class IPDialog:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 36)
        self.input_font = pygame.font.Font(None, 32)
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.BLUE = (0, 100, 200)
        
        # Dialog box
        self.dialog_width = 400
        self.dialog_height = 200
        self.dialog_x = (screen_width - self.dialog_width) // 2
        self.dialog_y = (screen_height - self.dialog_height) // 2
        
        # Input box
        self.input_box = pygame.Rect(self.dialog_x + 50, self.dialog_y + 80, 300, 40)
        
        # Buttons
        self.ok_button = pygame.Rect(self.dialog_x + 100, self.dialog_y + 140, 80, 35)
        self.cancel_button = pygame.Rect(self.dialog_x + 220, self.dialog_y + 140, 80, 35)
        
        # Input state
        self.ip_text = "localhost"
        self.active = True
        self.cursor_pos = len(self.ip_text)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return "ok"
            elif event.key == pygame.K_ESCAPE:
                return "cancel"
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.ip_text = self.ip_text[:self.cursor_pos-1] + self.ip_text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.ip_text), self.cursor_pos + 1)
            else:
                # Add character
                if len(self.ip_text) < 20:  # Limit length
                    char = event.unicode
                    if char.isprintable():
                        self.ip_text = self.ip_text[:self.cursor_pos] + char + self.ip_text[self.cursor_pos:]
                        self.cursor_pos += 1
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.ok_button.collidepoint(event.pos):
                return "ok"
            elif self.cancel_button.collidepoint(event.pos):
                return "cancel"
        
        return None
    
    def draw(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Dialog background
        dialog_rect = pygame.Rect(self.dialog_x, self.dialog_y, self.dialog_width, self.dialog_height)
        pygame.draw.rect(screen, self.WHITE, dialog_rect)
        pygame.draw.rect(screen, self.BLACK, dialog_rect, 3)
        
        # Title
        title_text = self.font.render("Enter Server IP", True, self.BLACK)
        title_rect = title_text.get_rect(center=(self.dialog_x + self.dialog_width//2, self.dialog_y + 30))
        screen.blit(title_text, title_rect)
        
        # Input box
        pygame.draw.rect(screen, self.WHITE, self.input_box)
        pygame.draw.rect(screen, self.BLACK, self.input_box, 2)
        
        # Input text
        text_surface = self.input_font.render(self.ip_text, True, self.BLACK)
        screen.blit(text_surface, (self.input_box.x + 5, self.input_box.y + 8))
        
        # Cursor
        if pygame.time.get_ticks() % 1000 < 500:  # Blinking cursor
            cursor_x = self.input_box.x + 5 + self.input_font.size(self.ip_text[:self.cursor_pos])[0]
            pygame.draw.line(screen, self.BLACK, (cursor_x, self.input_box.y + 5), (cursor_x, self.input_box.y + 30), 2)
        
        # Buttons
        pygame.draw.rect(screen, self.BLUE, self.ok_button)
        pygame.draw.rect(screen, self.BLACK, self.ok_button, 2)
        
        pygame.draw.rect(screen, self.GRAY, self.cancel_button)
        pygame.draw.rect(screen, self.BLACK, self.cancel_button, 2)
        
        # Button text
        ok_text = self.font.render("OK", True, self.WHITE)
        ok_rect = ok_text.get_rect(center=self.ok_button.center)
        screen.blit(ok_text, ok_rect)
        
        cancel_text = self.font.render("Cancel", True, self.WHITE)
        cancel_rect = cancel_text.get_rect(center=self.cancel_button.center)
        screen.blit(cancel_text, cancel_rect)
    
    def get_ip(self):
        return self.ip_text if self.ip_text.strip() else "localhost"
