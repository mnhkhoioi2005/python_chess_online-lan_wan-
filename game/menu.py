import pygame
import sys
import os
from game.database import Database

class MainMenu:
    def __init__(self, current_user=None, db=None): 
        self.screen = pygame.display.get_surface()
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.db = db 
        
        self.current_user = current_user
        self.is_admin = (current_user and current_user.get('role') == 'admin')
        
        self.show_dropdown = False
        self.show_profile_modal = False
        self.is_editing_profile = False 
        
        self.edit_data = {}
        self.active_edit_key = None
        self.match_history = []
        
        # --- MÀU SẮC ---
        self.COLOR_BG = (245, 245, 245)
        self.COLOR_TITLE = (50, 50, 50)
        self.COLOR_TEXT_LIGHT = (255, 255, 255)
        self.COLOR_TEXT_DARK = (40, 40, 40)
        
        self.BTN_GREEN = (46, 204, 113)
        self.BTN_GREEN_HOVER = (39, 174, 96)
        self.BTN_BLUE = (52, 152, 219)
        self.BTN_BLUE_HOVER = (41, 128, 185)
        self.BTN_RED = (231, 76, 60)
        self.BTN_RED_HOVER = (192, 57, 43)
        self.BTN_GRAY = (149, 165, 166)
        self.BTN_GRAY_HOVER = (127, 140, 141)
        self.BTN_ORANGE = (230, 126, 34)
        self.BTN_ORANGE_HOVER = (211, 84, 0)
        self.BTN_PURPLE = (155, 89, 182)
        self.BTN_PURPLE_HOVER = (142, 68, 173)
        
        self.load_assets()
        self.menu_state = "main"

        # Layout Menu
        button_width, button_height = 450, 70
        center_x = self.screen_width // 2
        y_start_main = self.screen_height // 2 - 230
        button_spacing_main = 85
        
        self.vs_player_button_rect = pygame.Rect(center_x - button_width//2, y_start_main, button_width, button_height)
        self.vs_ai_button_rect = pygame.Rect(center_x - button_width//2, y_start_main + button_spacing_main, button_width, button_height)
        self.lan_button_rect = pygame.Rect(center_x - button_width//2, y_start_main + 2 * button_spacing_main, button_width, button_height)
        self.online_button_rect = pygame.Rect(center_x - button_width//2, y_start_main + 3 * button_spacing_main, button_width, button_height)
        self.load_button_rect = pygame.Rect(center_x - button_width//2, y_start_main + 4 * button_spacing_main, button_width, button_height)
        
        if self.is_admin:
            self.admin_button_rect = pygame.Rect(center_x - button_width//2, y_start_main + 5 * button_spacing_main, button_width, button_height)
            self.exit_button_rect = pygame.Rect(center_x - button_width//2, y_start_main + 6 * button_spacing_main, button_width, button_height)
        else:
            self.admin_button_rect = None
            self.exit_button_rect = pygame.Rect(center_x - button_width//2, y_start_main + 5 * button_spacing_main, button_width, button_height)
        
        y_start_ai = self.screen_height // 2 - 100
        button_spacing_ai = 75
        self.ai_easy_button_rect = pygame.Rect(center_x - button_width//2, y_start_ai, button_width, button_height)
        self.ai_medium_button_rect = pygame.Rect(center_x - button_width//2, y_start_ai + button_spacing_ai, button_width, button_height)
        self.ai_hard_button_rect = pygame.Rect(center_x - button_width//2, y_start_ai + 2 * button_spacing_ai, button_width, button_height)
        self.ai_back_button_rect = pygame.Rect(center_x - button_width//2, y_start_ai + 3 * button_spacing_ai, button_width, button_height)

        # User Icon
        self.icon_size = 50
        self.user_icon_rect = pygame.Rect(self.screen_width - 70, 20, self.icon_size, self.icon_size)
        self.dropdown_rect = pygame.Rect(self.screen_width - 220, 80, 200, 100)
        self.btn_info_rect = pygame.Rect(self.dropdown_rect.x, self.dropdown_rect.y, 200, 50)
        self.btn_logout_rect = pygame.Rect(self.dropdown_rect.x, self.dropdown_rect.y + 50, 200, 50)
        
        # --- Modal Profile ---
        modal_w, modal_h = 900, 550 
        self.modal_rect = pygame.Rect((self.screen_width - modal_w)//2, (self.screen_height - modal_h)//2, modal_w, modal_h)
        self.btn_close_modal = pygame.Rect(self.modal_rect.right - 40, self.modal_rect.top + 10, 30, 30)
        self.btn_edit_save = pygame.Rect(self.modal_rect.x + 150, self.modal_rect.bottom - 60, 140, 40)
        
        # Layout form bên trái
        start_y = self.modal_rect.y + 150
        
        # (SỬA) Kéo vị trí nhập liệu lại gần hơn (170px từ lề trái modal)
        # "Số điện thoại" dài nhất khoảng 130px, nên 170px là vừa đẹp
        input_x_start = self.modal_rect.x + 170 
        input_width = 280 
        
        self.edit_rects = {
            "fullname": pygame.Rect(input_x_start, start_y, input_width, 40),
            "email": pygame.Rect(input_x_start, start_y + 60, input_width, 40),
            "phone": pygame.Rect(input_x_start, start_y + 120, input_width, 40)
        }

    def load_assets(self):
        font_path = os.path.join("assets", "fonts")
        img_path = os.path.join("assets", "images")
        try:
            self.title_font = pygame.font.Font(os.path.join(font_path, "Roboto-Bold.ttf"), 110)
            self.button_font = pygame.font.Font(os.path.join(font_path, "Roboto-Regular.ttf"), 40)
            self.small_font = pygame.font.Font(os.path.join(font_path, "Roboto-Regular.ttf"), 20)
            self.info_font = pygame.font.Font(os.path.join(font_path, "Roboto-Bold.ttf"), 22)
        except:
            self.title_font = pygame.font.Font(None, 120)
            self.button_font = pygame.font.Font(None, 60)
            self.small_font = pygame.font.Font(None, 20)
            self.info_font = pygame.font.Font(None, 22)
        try:
            self.bg_image = pygame.image.load(os.path.join(img_path, "menu_bg.png"))
            self.bg_image = pygame.transform.scale(self.bg_image, (self.screen_width, self.screen_height))
        except: self.bg_image = None
        try:
            self.user_icon_img = pygame.image.load(os.path.join(img_path, "user_icon.png"))
            self.user_icon_img = pygame.transform.scale(self.user_icon_img, (self.icon_size, self.icon_size))
        except: self.user_icon_img = None

    def draw_button(self, rect, text, base_color, hover_color, mouse_pos, font=None):
        is_hovered = rect.collidepoint(mouse_pos)
        color = hover_color if is_hovered else base_color
        pygame.draw.rect(self.screen, color, rect, border_radius=15)
        font_to_use = font if font else self.button_font
        btn_text = font_to_use.render(text, True, self.COLOR_TEXT_LIGHT)
        text_rect = btn_text.get_rect(center=rect.center)
        self.screen.blit(btn_text, text_rect)

    def draw_profile_modal(self, mouse_pos):
        # Lớp phủ
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0,0,0))
        self.screen.blit(overlay, (0,0))
        
        # --- (MỚI) Bóng đổ cho Modal ---
        shadow_rect = self.modal_rect.copy()
        shadow_rect.move_ip(5, 5)
        pygame.draw.rect(self.screen, (0,0,0,100), shadow_rect, border_radius=20)
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0,0,0))
        self.screen.blit(overlay, (0,0))
        
        pygame.draw.rect(self.screen, (255, 255, 255), self.modal_rect, border_radius=20)
        pygame.draw.rect(self.screen, self.BTN_BLUE, self.modal_rect, 3, border_radius=20)
        
        header = self.info_font.render("THÔNG TIN TÀI KHOẢN", True, self.BTN_BLUE)
        self.screen.blit(header, (self.modal_rect.centerx - header.get_width()//2, self.modal_rect.y + 20))
        
        # --- CỘT TRÁI: Thông tin ---
        mid_x = self.modal_rect.x + 480 # Đẩy đường kẻ sang phải một chút
        pygame.draw.line(self.screen, (200,200,200), (mid_x, self.modal_rect.y + 80), (mid_x, self.modal_rect.bottom - 30), 2)

        username_text = self.info_font.render(f"User: {self.current_user['username']}", True, (50,50,50))
        self.screen.blit(username_text, (self.modal_rect.x + 40, self.modal_rect.y + 90))
        
        elo_text = self.info_font.render(f"ELO: {self.current_user['elo']}", True, (230, 126, 34))
        self.screen.blit(elo_text, (self.modal_rect.x + 280, self.modal_rect.y + 90))

        labels = ["Họ tên:", "Email:", "SĐT:"]
        keys = ["fullname", "email", "phone"]
        start_y = self.modal_rect.y + 150 
        
        for i, label in enumerate(labels):
            lbl_surf = self.info_font.render(label, True, (50,50,50))
            self.screen.blit(lbl_surf, (self.modal_rect.x + 40, start_y + 10))
            
            key = keys[i]
            rect = self.edit_rects[key] 
            rect.y = start_y
            
            if self.is_editing_profile:
                color = self.BTN_BLUE if self.active_edit_key == key else (200,200,200)
                pygame.draw.rect(self.screen, (245,245,245), rect)
                pygame.draw.rect(self.screen, color, rect, 2)
                val = self.edit_data.get(key, "")
                val_surf = self.small_font.render(val, True, (0,0,0))
                
                if val_surf.get_width() > rect.width - 10:
                   val = val[:25] + "..."
                   val_surf = self.small_font.render(val, True, (0,0,0))

                self.screen.blit(val_surf, (rect.x + 10, rect.y + 10))
            else:
                val = self.current_user.get(key, "---")
                if len(val) > 22: val = val[:22] + "..."
                val_surf = self.info_font.render(val, True, (0,0,0))
                # (SỬA) Vẽ text ngay sát nhãn (dùng rect.x + 5)
                self.screen.blit(val_surf, (rect.x + 5, start_y + 10))
            
            start_y += 60

        btn_text = "LƯU" if self.is_editing_profile else "CHỈNH SỬA"
        btn_color = self.BTN_GREEN if self.is_editing_profile else self.BTN_ORANGE
        self.draw_button(self.btn_edit_save, btn_text, btn_color, self.BTN_BLUE, mouse_pos, self.small_font)

        # --- CỘT PHẢI: Lịch sử đấu ---
        history_x_start = mid_x + 20
        history_y = self.modal_rect.y + 80
        
        hist_header = self.info_font.render("LỊCH SỬ ĐẤU", True, (100, 100, 100))
        self.screen.blit(hist_header, (history_x_start, history_y))
        
        header_y = history_y + 40
        # (SỬA) Nới rộng khoảng cách các cột lịch sử
        col1_x = history_x_start 
        col2_x = history_x_start + 140 
        col3_x = history_x_start + 260 

        self.screen.blit(self.small_font.render("Đối thủ", True, (50,50,50)), (col1_x, header_y))
        self.screen.blit(self.small_font.render("KQ", True, (50,50,50)), (col2_x, header_y))
        self.screen.blit(self.small_font.render("Ngày", True, (50,50,50)), (col3_x, header_y))
        
        pygame.draw.line(self.screen, (200,200,200), (col1_x, header_y + 25), (self.modal_rect.right - 20, header_y + 25), 1)
        
        row_y = header_y + 35
        if not self.match_history:
            no_hist = self.small_font.render("(Chưa có trận đấu nào)", True, (150,150,150))
            self.screen.blit(no_hist, (col1_x, row_y))
        else:
            for match in self.match_history: 
                opp, res, date = match
                
                if len(opp) > 11: opp = opp[:10] + "..."
                
                res_short = res
                if "Won" in res: res_short = res.replace(" Won", "")
                
                if "Win" in res or "White" in res: color = self.BTN_GREEN
                elif "Loss" in res or "Black" in res: color = self.BTN_RED
                else: color = self.BTN_GRAY
                
                opp_surf = self.small_font.render(opp, True, (0,0,0))
                res_surf = self.small_font.render(res_short, True, color)
                date_surf = self.small_font.render(date, True, (100,100,100))
                
                self.screen.blit(opp_surf, (col1_x, row_y))
                self.screen.blit(res_surf, (col2_x, row_y))
                self.screen.blit(date_surf, (col3_x, row_y))
                
                row_y += 30
                if row_y > self.modal_rect.bottom - 50: break 

        pygame.draw.rect(self.screen, self.BTN_RED, self.btn_close_modal, border_radius=5)
        x_text = self.small_font.render("X", True, (255,255,255))
        self.screen.blit(x_text, (self.btn_close_modal.centerx - x_text.get_width()//2, self.btn_close_modal.centery - x_text.get_height()//2))

    def draw(self, mouse_pos):
        if self.bg_image: self.screen.blit(self.bg_image, (0, 0))
        else: self.screen.fill(self.COLOR_BG)
        
        if self.menu_state == "main":
            title_text = self.title_font.render("CHESS GAME", True, self.COLOR_TITLE)
            title_rect = title_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 280))
            self.screen.blit(title_text, title_rect)
            self.draw_button(self.vs_player_button_rect, "VS PLAYER", self.BTN_GREEN, self.BTN_GREEN_HOVER, mouse_pos)
            self.draw_button(self.vs_ai_button_rect, "VS AI", self.BTN_BLUE, self.BTN_BLUE_HOVER, mouse_pos)
            self.draw_button(self.lan_button_rect, "LAN MULTIPLAYER", self.BTN_PURPLE, self.BTN_PURPLE_HOVER, mouse_pos)
            self.draw_button(self.online_button_rect, "ONLINE MULTIPLAYER", self.BTN_ORANGE, self.BTN_ORANGE_HOVER, mouse_pos)
            self.draw_button(self.load_button_rect, "LOAD GAME", self.BTN_GRAY, self.BTN_GRAY_HOVER, mouse_pos)
            if self.is_admin and self.admin_button_rect:
                self.draw_button(self.admin_button_rect, "ADMIN PANEL", self.BTN_RED, self.BTN_RED_HOVER, mouse_pos)
            self.draw_button(self.exit_button_rect, "EXIT", self.BTN_GRAY, self.BTN_GRAY_HOVER, mouse_pos)
        elif self.menu_state == "ai_select":
            title_text = self.title_font.render("SELECT DIFFICULTY", True, self.COLOR_TITLE)
            title_rect = title_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 250))
            self.screen.blit(title_text, title_rect)
            self.draw_button(self.ai_easy_button_rect, "EASY", self.BTN_GREEN, self.BTN_GREEN_HOVER, mouse_pos)
            self.draw_button(self.ai_medium_button_rect, "MEDIUM", self.BTN_BLUE, self.BTN_BLUE_HOVER, mouse_pos)
            self.draw_button(self.ai_hard_button_rect, "HARD", self.BTN_RED, self.BTN_RED_HOVER, mouse_pos)
            self.draw_button(self.ai_back_button_rect, "BACK", self.BTN_GRAY, self.BTN_GRAY_HOVER, mouse_pos)

        if self.user_icon_img: self.screen.blit(self.user_icon_img, self.user_icon_rect)
        else:
            pygame.draw.circle(self.screen, self.BTN_BLUE, self.user_icon_rect.center, 25)
            initial = self.current_user['username'][0].upper()
            text = self.small_font.render(initial, True, (255,255,255))
            self.screen.blit(text, (self.user_icon_rect.centerx - text.get_width()//2, self.user_icon_rect.centery - text.get_height()//2))

        if self.show_dropdown:
            pygame.draw.rect(self.screen, (255, 255, 255), self.dropdown_rect, border_radius=10)
            pygame.draw.rect(self.screen, (200, 200, 200), self.dropdown_rect, 2, border_radius=10)
            self.draw_button(self.btn_info_rect, "Thông tin", self.BTN_BLUE, self.BTN_BLUE_HOVER, mouse_pos, self.small_font)
            self.draw_button(self.btn_logout_rect, "Đăng xuất", self.BTN_RED, self.BTN_RED_HOVER, mouse_pos, self.small_font)

        if self.show_profile_modal:
            self.draw_profile_modal(mouse_pos)

        pygame.display.flip()
    
    def handle_click(self, pos):
        # (Giữ nguyên)
        if self.show_profile_modal:
            if self.btn_close_modal.collidepoint(pos):
                self.show_profile_modal = False
                self.is_editing_profile = False
            elif self.btn_edit_save.collidepoint(pos):
                if not self.is_editing_profile:
                    self.is_editing_profile = True
                    self.edit_data = {
                        "fullname": self.current_user.get("fullname", ""),
                        "email": self.current_user.get("email", ""),
                        "phone": self.current_user.get("phone", "")
                    }
                else:
                    success = self.db.update_user_info(
                        self.current_user['id'],
                        self.edit_data["fullname"],
                        self.edit_data["email"],
                        self.edit_data["phone"]
                    )
                    if success:
                        self.current_user.update(self.edit_data)
                        self.is_editing_profile = False
            elif self.is_editing_profile:
                self.active_edit_key = None
                for key, rect in self.edit_rects.items():
                    if rect.collidepoint(pos):
                        self.active_edit_key = key
                        break
            return None

        if self.show_dropdown:
            if self.btn_info_rect.collidepoint(pos):
                self.show_dropdown = False
                self.show_profile_modal = True
                self.match_history = self.db.get_user_history(self.current_user['id'])
                return None
            elif self.btn_logout_rect.collidepoint(pos):
                return "logout"
            if not self.dropdown_rect.collidepoint(pos) and not self.user_icon_rect.collidepoint(pos):
                self.show_dropdown = False

        if self.user_icon_rect.collidepoint(pos):
            self.show_dropdown = not self.show_dropdown
            return None

        if self.menu_state == "main":
            if self.vs_player_button_rect.collidepoint(pos): return "vs_player"
            elif self.vs_ai_button_rect.collidepoint(pos): 
                self.menu_state = "ai_select"
                return "state_change"
            elif self.lan_button_rect.collidepoint(pos): return "lan_multiplayer"
            elif self.online_button_rect.collidepoint(pos): return "online_multiplayer"
            elif self.load_button_rect.collidepoint(pos): return "load_game"
            elif self.exit_button_rect.collidepoint(pos): return "exit"
            elif self.is_admin and self.admin_button_rect and self.admin_button_rect.collidepoint(pos):
                return "admin_panel"
        elif self.menu_state == "ai_select":
            if self.ai_easy_button_rect.collidepoint(pos): return "vs_ai_easy"
            elif self.ai_medium_button_rect.collidepoint(pos): return "vs_ai_medium"
            elif self.ai_hard_button_rect.collidepoint(pos): return "vs_ai_hard"
            elif self.ai_back_button_rect.collidepoint(pos):
                self.menu_state = "main"
                return "state_change"
        return None
    
    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "exit"
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    result = self.handle_click(event.pos)
                    if result == "state_change": continue
                    if result: return result 
                
                if event.type == pygame.KEYDOWN and self.is_editing_profile and self.active_edit_key:
                    if event.key == pygame.K_BACKSPACE:
                        self.edit_data[self.active_edit_key] = self.edit_data[self.active_edit_key][:-1]
                    else:
                        self.edit_data[self.active_edit_key] += event.unicode
            
            self.draw(mouse_pos)
            self.clock.tick(60)
        return "exit"