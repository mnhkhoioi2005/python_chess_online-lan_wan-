import pygame
import sys
import os
from game.database import Database

class LoginMenu:
    def __init__(self, db):
        self.screen = pygame.display.get_surface()
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        
        pygame.display.set_caption("Chess Game - Login")
        
        self.db = db 
        self.mode = "login" 
        
        # --- MÀU SẮC HIỆN ĐẠI ---
        self.COLOR_BG_OVERLAY = (0, 0, 0, 180) 
        self.COLOR_CARD_BG = (30, 30, 30, 230)
        self.COLOR_INPUT_BG = (50, 50, 50)
        self.COLOR_INPUT_BORDER_ACTIVE = (52, 152, 219) 
        self.COLOR_INPUT_BORDER_INACTIVE = (100, 100, 100)
        self.COLOR_TEXT = (240, 240, 240)
        self.COLOR_PLACEHOLDER = (150, 150, 150)
        
        self.BTN_GREEN = (46, 204, 113)
        self.BTN_BLUE = (52, 152, 219)
        self.BTN_RED = (231, 76, 60)
        
        self.load_assets()
        
        self.inputs = {
            "username": "", "password": "",
            "fullname": "", "email": "", "phone": ""
        }
        self.active_key = None
        self.message = ""

        # --- LAYOUT CARD ---
        self.card_width = 500
        self.card_height_login = 450
        self.card_height_register = 650
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2
        
        self.update_layout()

    def update_layout(self):
        h = self.card_height_login if self.mode == "login" else self.card_height_register
        self.card_rect = pygame.Rect(0, 0, self.card_width, h)
        self.card_rect.center = (self.center_x, self.center_y)
        
        cx = self.card_rect.centerx
        start_y = self.card_rect.top + 100
        gap = 65
        
        if self.mode == "login":
            self.login_user_rect = pygame.Rect(cx - 180, start_y, 360, 50)
            self.login_pass_rect = pygame.Rect(cx - 180, start_y + gap, 360, 50)
            self.login_btn_rect = pygame.Rect(cx - 180, start_y + 2*gap + 10, 360, 50)
            self.switch_to_reg_rect = pygame.Rect(cx - 150, start_y + 3*gap, 300, 30)
        else:
            start_y = self.card_rect.top + 90
            gap = 60
            self.reg_user_rect = pygame.Rect(cx - 180, start_y, 360, 45)
            self.reg_pass_rect = pygame.Rect(cx - 180, start_y + gap, 360, 45)
            self.reg_name_rect = pygame.Rect(cx - 180, start_y + 2*gap, 360, 45)
            self.reg_email_rect = pygame.Rect(cx - 180, start_y + 3*gap, 360, 45)
            self.reg_phone_rect = pygame.Rect(cx - 180, start_y + 4*gap, 360, 45)
            self.reg_btn_rect = pygame.Rect(cx - 180, start_y + 5*gap + 15, 360, 50)
            self.switch_to_login_rect = pygame.Rect(cx - 150, start_y + 6*gap + 10, 300, 30)

        self.exit_btn_rect = pygame.Rect(self.card_rect.right - 40, self.card_rect.top + 10, 30, 30)

    def load_assets(self):
        try:
            base_path = os.path.dirname(os.path.dirname(__file__))
            font_path = os.path.join(base_path, "assets", "fonts")
            img_path = os.path.join(base_path, "assets", "images")
            self.font = pygame.font.Font(os.path.join(font_path, "Roboto-Regular.ttf"), 24)
            self.font_small = pygame.font.Font(os.path.join(font_path, "Roboto-Regular.ttf"), 18)
            self.font_title = pygame.font.Font(os.path.join(font_path, "Roboto-Bold.ttf"), 40)
        except:
            self.font = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 20)
            self.font_title = pygame.font.Font(None, 50)
            
        try:
            self.bg_image = pygame.image.load(os.path.join(img_path, "game_bg.png"))
            self.bg_image = pygame.transform.scale(self.bg_image, (self.screen_width, self.screen_height))
        except:
            self.bg_image = None

    def draw_input(self, rect, key, placeholder, is_password=False):
        color_border = self.COLOR_INPUT_BORDER_ACTIVE if self.active_key == key else self.COLOR_INPUT_BORDER_INACTIVE
        pygame.draw.rect(self.screen, self.COLOR_INPUT_BG, rect, border_radius=8)
        pygame.draw.rect(self.screen, color_border, rect, 2, border_radius=8)
        
        text_val = self.inputs[key]
        if is_password: text_val = "*" * len(text_val) 
        
        if text_val:
            surf = self.font.render(text_val, True, self.COLOR_TEXT)
        else:
            surf = self.font.render(placeholder, True, self.COLOR_PLACEHOLDER)
            
        text_y = rect.centery - surf.get_height() // 2
        self.screen.blit(surf, (rect.x + 15, text_y))

    def draw(self):
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill((40, 44, 52))
            
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(self.COLOR_BG_OVERLAY)
        self.screen.blit(overlay, (0,0))

        shadow_rect = self.card_rect.copy()
        shadow_rect.move_ip(5, 5)
        pygame.draw.rect(self.screen, (0,0,0, 100), shadow_rect, border_radius=20)
        
        card_surf = pygame.Surface(self.card_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(card_surf, self.COLOR_CARD_BG, card_surf.get_rect(), border_radius=20)
        pygame.draw.rect(card_surf, (255,255,255, 30), card_surf.get_rect(), 1, border_radius=20)
        self.screen.blit(card_surf, self.card_rect.topleft)

        # --- (SỬA) Dùng chữ X thường thay vì ký tự đặc biệt ---
        pygame.draw.circle(self.screen, self.BTN_RED, self.exit_btn_rect.center, 15)
        x_txt = self.font_small.render("X", True, (255,255,255))
        self.screen.blit(x_txt, (self.exit_btn_rect.centerx - x_txt.get_width()//2, self.exit_btn_rect.centery - x_txt.get_height()//2))
        # -----------------------------------------------------

        if self.mode == "login":
            title = self.font_title.render("WELCOME BACK", True, self.COLOR_TEXT)
            self.screen.blit(title, (self.card_rect.centerx - title.get_width()//2, self.card_rect.top + 40))
            
            self.draw_input(self.login_user_rect, "username", "Tên đăng nhập")
            self.draw_input(self.login_pass_rect, "password", "Mật khẩu", True)
            
            pygame.draw.rect(self.screen, self.BTN_BLUE, self.login_btn_rect, border_radius=10)
            txt = self.font.render("ĐĂNG NHẬP", True, (255,255,255))
            self.screen.blit(txt, (self.login_btn_rect.centerx - txt.get_width()//2, self.login_btn_rect.centery - txt.get_height()//2))
            
            switch_txt = self.font_small.render("Chưa có tài khoản? Đăng ký ngay", True, self.BTN_GREEN)
            self.screen.blit(switch_txt, (self.switch_to_reg_rect.centerx - switch_txt.get_width()//2, self.switch_to_reg_rect.centery - switch_txt.get_height()//2))

        else:
            title = self.font_title.render("TẠO TÀI KHOẢN", True, self.COLOR_TEXT)
            self.screen.blit(title, (self.card_rect.centerx - title.get_width()//2, self.card_rect.top + 30))
            
            self.draw_input(self.reg_user_rect, "username", "Tên đăng nhập (*)")
            self.draw_input(self.reg_pass_rect, "password", "Mật khẩu (*)", True)
            self.draw_input(self.reg_name_rect, "fullname", "Họ và tên")
            self.draw_input(self.reg_email_rect, "email", "Email")
            self.draw_input(self.reg_phone_rect, "phone", "Số điện thoại")
            
            pygame.draw.rect(self.screen, self.BTN_GREEN, self.reg_btn_rect, border_radius=10)
            txt = self.font.render("ĐĂNG KÝ", True, (255,255,255))
            self.screen.blit(txt, (self.reg_btn_rect.centerx - txt.get_width()//2, self.reg_btn_rect.centery - txt.get_height()//2))
            
            back_txt = self.font_small.render("Đã có tài khoản? Đăng nhập", True, self.BTN_BLUE)
            self.screen.blit(back_txt, (self.switch_to_login_rect.centerx - back_txt.get_width()//2, self.switch_to_login_rect.centery - back_txt.get_height()//2))

        if self.message:
            color = self.BTN_RED if "Error" in self.message or "failed" in self.message or "tồn tại" in self.message else self.BTN_GREEN
            msg_surf = self.font_small.render(self.message, True, color)
            self.screen.blit(msg_surf, (self.card_rect.centerx - msg_surf.get_width()//2, self.card_rect.bottom - 30))

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    self.message = ""
                    
                    if self.exit_btn_rect.collidepoint(pos):
                        return None
                    
                    if self.mode == "login":
                        if self.login_user_rect.collidepoint(pos): self.active_key = "username"
                        elif self.login_pass_rect.collidepoint(pos): self.active_key = "password"
                        elif self.switch_to_reg_rect.collidepoint(pos): 
                            self.mode = "register"
                            self.update_layout()
                            self.active_key = None
                        elif self.login_btn_rect.collidepoint(pos):
                            success, data = self.db.login_user(self.inputs["username"], self.inputs["password"])
                            if success: return data
                            else: self.message = "Đăng nhập thất bại! Sai tên hoặc mật khẩu."
                        else: self.active_key = None
                        
                    else: 
                        if self.reg_user_rect.collidepoint(pos): self.active_key = "username"
                        elif self.reg_pass_rect.collidepoint(pos): self.active_key = "password"
                        elif self.reg_name_rect.collidepoint(pos): self.active_key = "fullname"
                        elif self.reg_email_rect.collidepoint(pos): self.active_key = "email"
                        elif self.reg_phone_rect.collidepoint(pos): self.active_key = "phone"
                        elif self.switch_to_login_rect.collidepoint(pos): 
                            self.mode = "login"
                            self.update_layout()
                            self.active_key = None
                        elif self.reg_btn_rect.collidepoint(pos):
                            if len(self.inputs["username"]) < 3 or len(self.inputs["password"]) < 3:
                                self.message = "Error: Tên/Mật khẩu quá ngắn!"
                            else:
                                success, msg = self.db.register_user(
                                    self.inputs["username"], self.inputs["password"],
                                    self.inputs["fullname"], self.inputs["email"], self.inputs["phone"]
                                )
                                self.message = msg
                                if success: 
                                    self.inputs["password"] = ""
                        else: self.active_key = None
                
                if event.type == pygame.KEYDOWN:
                    if self.active_key:
                        if event.key == pygame.K_BACKSPACE:
                            self.inputs[self.active_key] = self.inputs[self.active_key][:-1]
                        elif event.key == pygame.K_TAB:
                            pass 
                        else:
                            self.inputs[self.active_key] += event.unicode
                            
            self.draw()
            pygame.time.Clock().tick(60)