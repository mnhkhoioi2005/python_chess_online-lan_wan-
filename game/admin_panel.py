import pygame
import sys
import os

class AdminPanel:
    def __init__(self, db): 
        self.screen = pygame.display.get_surface()
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        pygame.display.set_caption("Chess Game - Admin Panel")
        
        self.db = db 
        self.users = []
        self.refresh_data()
        
        self.BG_COLOR = (236, 240, 241)
        self.HEADER_BG = (44, 62, 80) # Nền tiêu đề tối
        self.ROW_COLOR_EVEN = (255, 255, 255)
        self.ROW_COLOR_ODD = (236, 240, 241)
        self.TEXT_COLOR = (50, 50, 50)
        self.TEXT_HEADER = (255, 255, 255)
        
        self.BTN_RED = (231, 76, 60)
        self.BTN_BLUE = (52, 152, 219)
        self.BTN_ORANGE = (230, 126, 34)
        self.BTN_BACK = (149, 165, 166)
        self.BTN_GREEN = (46, 204, 113)
        
        self.load_assets()
        self.back_button = pygame.Rect(20, 20, 100, 40)
        self.delete_buttons = [] 
        self.role_buttons = []
        self.edit_buttons = []
        
        # Modal Edit User
        self.show_edit_modal = False
        self.editing_user = None
        self.edit_data = {}
        self.active_edit_field = None
        self.edit_message = ""

    def refresh_data(self):
        self.users = self.db.get_all_users()
    
    def get_user_full_info(self, user_id):
        """Lấy thông tin đầy đủ của user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, elo, role, fullname, email, phone, password FROM users WHERE id=?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0], 'username': row[1], 'elo': row[2], 'role': row[3],
                'fullname': row[4] or '', 'email': row[5] or '', 'phone': row[6] or '',
                'password': row[7] or ''
            }
        return None

    def load_assets(self):
        try:
            base_path = os.path.dirname(os.path.dirname(__file__))
            font_path = os.path.join(base_path, "assets", "fonts")
            self.font_title = pygame.font.Font(os.path.join(font_path, "Roboto-Bold.ttf"), 36)
            self.font_header = pygame.font.Font(os.path.join(font_path, "Roboto-Bold.ttf"), 20)
            self.font_row = pygame.font.Font(os.path.join(font_path, "Roboto-Regular.ttf"), 18)
            self.font_btn = pygame.font.Font(os.path.join(font_path, "Roboto-Bold.ttf"), 16)
        except:
            self.font_title = pygame.font.Font(None, 40)
            self.font_header = pygame.font.Font(None, 22)
            self.font_row = pygame.font.Font(None, 20)
            self.font_btn = pygame.font.Font(None, 18)
    
    def draw_edit_modal(self):
        """Vẽ modal chỉnh sửa user"""
        # Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Modal Box
        modal_width = 600
        modal_height = 550
        modal_x = (self.screen_width - modal_width) // 2
        modal_y = (self.screen_height - modal_height) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)
        
        pygame.draw.rect(self.screen, (255, 255, 255), modal_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.BTN_BLUE, modal_rect, 3, border_radius=15)
        
        # Title
        title = self.font_title.render("CHỈNH SỬA THÔNG TIN", True, self.BTN_BLUE)
        self.screen.blit(title, (modal_rect.centerx - title.get_width()//2, modal_y + 20))
        
        # Close Button
        close_btn = pygame.Rect(modal_rect.right - 40, modal_y + 10, 30, 30)
        pygame.draw.rect(self.screen, self.BTN_RED, close_btn, border_radius=5)
        x_text = self.font_btn.render("X", True, (255, 255, 255))
        self.screen.blit(x_text, (close_btn.centerx - x_text.get_width()//2, close_btn.centery - x_text.get_height()//2))
        
        # Form Fields
        labels = ["Username:", "Mật khẩu:", "ELO:", "Họ tên:", "Email:", "SĐT:"]
        keys = ["username", "password", "elo", "fullname", "email", "phone"]
        
        start_y = modal_y + 80
        field_spacing = 65
        
        self.edit_field_rects = {}
        
        for i, (label, key) in enumerate(zip(labels, keys)):
            y = start_y + i * field_spacing
            
            # Label
            lbl_surf = self.font_row.render(label, True, self.TEXT_COLOR)
            self.screen.blit(lbl_surf, (modal_x + 40, y))
            
            # Input Field
            field_rect = pygame.Rect(modal_x + 180, y - 5, 350, 35)
            self.edit_field_rects[key] = field_rect
            
            border_color = self.BTN_BLUE if self.active_edit_field == key else (200, 200, 200)
            pygame.draw.rect(self.screen, (245, 245, 245), field_rect)
            pygame.draw.rect(self.screen, border_color, field_rect, 2)
            
            # Value
            value = str(self.edit_data.get(key, ''))
            if key == "password" and value:
                value = "*" * len(value)
            
            val_surf = self.font_row.render(value[:30], True, (0, 0, 0))
            self.screen.blit(val_surf, (field_rect.x + 10, field_rect.y + 8))
        
        # Save Button
        save_btn = pygame.Rect(modal_rect.centerx - 80, modal_rect.bottom - 60, 160, 45)
        pygame.draw.rect(self.screen, self.BTN_GREEN, save_btn, border_radius=8)
        save_txt = self.font_header.render("LƯU", True, (255, 255, 255))
        self.screen.blit(save_txt, (save_btn.centerx - save_txt.get_width()//2, save_btn.centery - save_txt.get_height()//2))
        
        # Message
        if self.edit_message:
            msg_color = self.BTN_GREEN if "thành công" in self.edit_message else self.BTN_RED
            msg_surf = self.font_row.render(self.edit_message, True, msg_color)
            self.screen.blit(msg_surf, (modal_rect.centerx - msg_surf.get_width()//2, modal_rect.bottom - 100))
        
        return close_btn, save_btn

    def draw(self):
        self.screen.fill(self.BG_COLOR)
        
        # Title
        title = self.font_title.render("QUẢN LÝ NGƯỜI DÙNG", True, (44, 62, 80))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 25))

        # Nút Back
        pygame.draw.rect(self.screen, self.BTN_BACK, self.back_button, border_radius=5)
        back_txt = self.font_btn.render("BACK", True, (255,255,255))
        self.screen.blit(back_txt, (self.back_button.centerx - back_txt.get_width()//2, self.back_button.centery - back_txt.get_height()//2))
        
        # --- VẼ BẢNG ---
        table_y = 90
        col_widths = [80, 200, 100, 150, 400] # ID, User, ELO, Role, Action
        col_x = [100, 180, 380, 480, 630]
        headers = ["ID", "Username", "ELO", "Role", "Hành động"]
        
        # Header Row
        header_rect = pygame.Rect(50, table_y, self.screen_width - 100, 40)
        pygame.draw.rect(self.screen, self.HEADER_BG, header_rect, border_radius=5)
        
        for i, h in enumerate(headers):
            txt = self.font_header.render(h, True, self.TEXT_HEADER)
            self.screen.blit(txt, (col_x[i], table_y + 10))
            
        # Data Rows
        self.delete_buttons = []
        self.role_buttons = []
        self.edit_buttons = []
        row_y = table_y + 45
        row_height = 45
        
        for index, user in enumerate(self.users):
            user_id, username, elo, role = user
            
            # Background Row (Zebra)
            bg_color = self.ROW_COLOR_ODD if index % 2 == 0 else self.ROW_COLOR_EVEN
            row_rect = pygame.Rect(50, row_y, self.screen_width - 100, row_height)
            pygame.draw.rect(self.screen, bg_color, row_rect)
            
            # Text
            txt_y = row_y + 12
            self.screen.blit(self.font_row.render(str(user_id), True, self.TEXT_COLOR), (col_x[0], txt_y))
            self.screen.blit(self.font_row.render(username, True, self.TEXT_COLOR), (col_x[1], txt_y))
            self.screen.blit(self.font_row.render(str(elo), True, self.TEXT_COLOR), (col_x[2], txt_y))
            
            role_color = (231, 76, 60) if role == 'admin' else self.TEXT_COLOR
            self.screen.blit(self.font_row.render(role.upper(), True, role_color), (col_x[3], txt_y))
            
            # Buttons
            btn_y = row_y + 8
            btn_x = col_x[4]
            
            # Edit Button
            edit_rect = pygame.Rect(btn_x, btn_y, 75, 30)
            pygame.draw.rect(self.screen, self.BTN_GREEN, edit_rect, border_radius=5)
            e_txt = self.font_btn.render("EDIT", True, (255,255,255))
            self.screen.blit(e_txt, (edit_rect.centerx - e_txt.get_width()//2, edit_rect.centery - e_txt.get_height()//2))
            self.edit_buttons.append((edit_rect, user_id))
            
            # Role Button
            role_rect = pygame.Rect(btn_x + 85, btn_y, 100, 30)
            if role == 'user':
                pygame.draw.rect(self.screen, self.BTN_BLUE, role_rect, border_radius=5)
                r_txt = self.font_btn.render("→ADMIN", True, (255,255,255))
                self.role_buttons.append((role_rect, user_id, 'admin'))
            else:
                pygame.draw.rect(self.screen, self.BTN_ORANGE, role_rect, border_radius=5)
                r_txt = self.font_btn.render("→USER", True, (255,255,255))
                self.role_buttons.append((role_rect, user_id, 'user'))
            self.screen.blit(r_txt, (role_rect.centerx - r_txt.get_width()//2, role_rect.centery - r_txt.get_height()//2))
            
            # Delete Button
            del_rect = pygame.Rect(btn_x + 195, btn_y, 70, 30)
            pygame.draw.rect(self.screen, self.BTN_RED, del_rect, border_radius=5)
            d_txt = self.font_btn.render("XÓA", True, (255,255,255))
            self.screen.blit(d_txt, (del_rect.centerx - d_txt.get_width()//2, del_rect.centery - d_txt.get_height()//2))
            self.delete_buttons.append((del_rect, user_id))
            
            row_y += row_height + 2
        
        # Vẽ Modal Edit nếu đang mở
        if self.show_edit_modal:
            close_btn, save_btn = self.draw_edit_modal()
            self.modal_close_btn = close_btn
            self.modal_save_btn = save_btn

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "exit"
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # Nếu đang mở modal
                        if self.show_edit_modal:
                            # Close modal
                            if self.modal_close_btn.collidepoint(event.pos):
                                self.show_edit_modal = False
                                self.edit_message = ""
                                continue
                            
                            # Save changes
                            if self.modal_save_btn.collidepoint(event.pos):
                                try:
                                    conn = self.db.get_connection()
                                    cursor = conn.cursor()
                                    cursor.execute("""
                                        UPDATE users 
                                        SET username=?, password=?, elo=?, fullname=?, email=?, phone=?
                                        WHERE id=?
                                    """, (
                                        self.edit_data['username'],
                                        self.edit_data['password'],
                                        int(self.edit_data['elo']),
                                        self.edit_data['fullname'],
                                        self.edit_data['email'],
                                        self.edit_data['phone'],
                                        self.editing_user['id']
                                    ))
                                    conn.commit()
                                    conn.close()
                                    self.edit_message = "✓ Lưu thành công!"
                                    self.refresh_data()
                                except Exception as e:
                                    self.edit_message = f"✗ Lỗi: {str(e)[:30]}"
                                continue
                            
                            # Click vào field để chỉnh sửa
                            self.active_edit_field = None
                            for key, rect in self.edit_field_rects.items():
                                if rect.collidepoint(event.pos):
                                    self.active_edit_field = key
                                    break
                            continue
                        
                        # Nếu không có modal
                        if self.back_button.collidepoint(event.pos):
                            return "back"
                        
                        # Edit button
                        for btn_rect, user_id in self.edit_buttons:
                            if btn_rect.collidepoint(event.pos):
                                user_info = self.get_user_full_info(user_id)
                                if user_info:
                                    self.editing_user = user_info
                                    self.edit_data = {
                                        'username': user_info['username'],
                                        'password': user_info['password'],
                                        'elo': str(user_info['elo']),
                                        'fullname': user_info['fullname'],
                                        'email': user_info['email'],
                                        'phone': user_info['phone']
                                    }
                                    self.show_edit_modal = True
                                    self.active_edit_field = None
                                    self.edit_message = ""
                                break
                        
                        # Role button
                        for btn_rect, user_id, new_role in self.role_buttons:
                            if btn_rect.collidepoint(event.pos):
                                self.db.update_user_role(user_id, new_role)
                                self.refresh_data()
                                break
                        
                        # Delete button
                        for btn_rect, user_id in self.delete_buttons:
                            if btn_rect.collidepoint(event.pos):
                                self.db.delete_user(user_id)
                                self.refresh_data()
                                break
                
                # Xử lý nhập liệu trong modal
                if event.type == pygame.KEYDOWN and self.show_edit_modal and self.active_edit_field:
                    if event.key == pygame.K_BACKSPACE:
                        self.edit_data[self.active_edit_field] = self.edit_data[self.active_edit_field][:-1]
                    elif event.key == pygame.K_TAB:
                        pass  # Có thể thêm chuyển field sau
                    else:
                        self.edit_data[self.active_edit_field] += event.unicode
            
            self.draw()