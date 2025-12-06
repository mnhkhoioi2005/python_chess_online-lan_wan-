import pygame
import sys
import os

class ChessGUI:
    def __init__(self, server_ip=None):
        # Main.py đã khởi tạo pygame, nhưng gọi lại để chắc chắn font/sound load được
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.mixer.init()
        
        info = pygame.display.Info()
        self.screen_width = 1280
        self.screen_height = 720
        
        # Lấy màn hình hiện tại
        self.screen = pygame.display.get_surface()
        if self.screen is None:
             self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
             
        pygame.display.set_caption("Cờ Vua")
        
        self.server_ip = server_ip

        # --- MÀU SẮC ---
        self.TEXT_COLOR = (50, 50, 50) 
        self.COLOR_TITLE = (55, 55, 55)
        self.COLOR_TEXT_LIGHT = (255, 255, 255) 
        self.WHITE_SQUARE = (240, 217, 181)
        self.BLACK_SQUARE = (181, 136, 99)
        self.SELECTED_BORDER_COLOR = (0, 150, 255)
        self.VALID_MOVE_COLOR = (100, 100, 100, 100)
        self.CHECK_HIGHLIGHT_COLOR = (255, 0, 0, 150)

        self.BTN_BLUE = (52, 152, 219)
        self.BTN_BLUE_HOVER = (41, 128, 185)
        self.BTN_RED = (231, 76, 60)
        self.BTN_RED_HOVER = (192, 57, 43)
        self.BTN_GRAY = (149, 165, 166)
        self.BTN_GRAY_HOVER = (127, 140, 141)
        self.BTN_YELLOW = (241, 196, 15)
        self.BTN_YELLOW_HOVER = (243, 156, 18)
        self.BTN_GREEN_RESTART = (46, 204, 113)
        self.BTN_GREEN_RESTART_HOVER = (39, 174, 96)

        self.load_assets() 

        # --- THÔNG SỐ BÀN CỜ 2D ---
        self.BOARD_SIZE = self.screen_height - 100 # 620px
        self.SQUARE_SIZE = self.BOARD_SIZE // 8
        self.board_x = 100
        self.board_y = (self.screen_height - self.BOARD_SIZE) // 2 
        
        self.pieces_unicode = {
            'wK': '♔', 'wQ': '♕', 'wR': '♖', 'wB': '♗', 'wN': '♘', 'wP': '♙',
            'bK': '♚', 'bQ': '♛', 'bR': '♜', 'bB': '♝', 'bN': '♞', 'bP': '♟'
        }
        
        self.piece_images = {}
        self.load_piece_images()
        
        # --- LAYOUT PANEL PHẢI (2 CỘT) ---
        panel_x_left = self.board_x + self.BOARD_SIZE + 70 # Cột thông tin
        panel_x_right = panel_x_left + 230 # Cột nút bấm
        
        self.history_x_pos = panel_x_left - 10
        self.history_y_pos = 310 
        self.history_width = 220
        self.history_height = 400
        
        button_width, button_height = 200, 50
        button_spacing = 60
        button_y_start = self.history_y_pos + 40
        
        self.undo_button = pygame.Rect(panel_x_right, button_y_start, button_width, button_height)
        self.restart_button = pygame.Rect(panel_x_right, button_y_start + button_spacing, button_width, button_height)
        self.save_button = pygame.Rect(panel_x_right, button_y_start + 2 * button_spacing, button_width, button_height)
        self.exit_button = pygame.Rect(panel_x_right, button_y_start + 3 * button_spacing, button_width, button_height)
        self.surrender_button = pygame.Rect(panel_x_right, 250, button_width, 40)
        
        self.selected_square = None
        self.dragging = False
        self.drag_piece = None
        self.drag_pos = (0, 0)
        self.promotion_dialog = None
        
        self.valid_moves_highlight = []
        self.in_check_square = None
        self.game_over_message = None
        self.turn_message = "Turn: White"
        self.ai_thinking_message = False

    def load_assets(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        font_path = os.path.join(base_path, "assets", "fonts")
        img_path = os.path.join(base_path, "assets", "images")
        sound_path = os.path.join(base_path, "assets", "sounds")
        try:
            self.font_title = pygame.font.Font(os.path.join(font_path, "Roboto-Bold.ttf"), 36)
            self.font_button_main = pygame.font.Font(os.path.join(font_path, "Roboto-Regular.ttf"), 24)
            self.font_coord = pygame.font.Font(os.path.join(font_path, "Roboto-Regular.ttf"), 18)
            self.font_history = pygame.font.Font(os.path.join(font_path, "Roboto-Regular.ttf"), 16)
            self.font_status = pygame.font.Font(os.path.join(font_path, "Roboto-Bold.ttf"), 28)
            self.font_game_over = pygame.font.Font(os.path.join(font_path, "Roboto-Bold.ttf"), 60)
            self.font_save_msg = pygame.font.Font(os.path.join(font_path, "Roboto-Regular.ttf"), 22)
            self.font_captured_score = pygame.font.Font(os.path.join(font_path, "Roboto-Bold.ttf"), 18)
            self.font_clock = pygame.font.Font(os.path.join(font_path, "Roboto-Bold.ttf"), 48)
            self.font_user_info = pygame.font.Font(os.path.join(font_path, "Roboto-Bold.ttf"), 22)
        except:
            print("Không tìm thấy font. Dùng font mặc định.")
            self.font_title = pygame.font.Font(None, 36)
            self.font_button_main = pygame.font.Font(None, 24)
            self.font_coord = pygame.font.Font(None, 18)
            self.font_history = pygame.font.Font(None, 16)
            self.font_status = pygame.font.Font(None, 28)
            self.font_game_over = pygame.font.Font(None, 60)
            self.font_save_msg = pygame.font.Font(None, 22)
            self.font_captured_score = pygame.font.Font(None, 18)
            self.font_clock = pygame.font.Font(None, 48)
            self.font_user_info = pygame.font.Font(None, 22)
        self.button_font = self.font_button_main 
        self.coord_font = self.font_coord
        self.piece_font = pygame.font.Font(None, 70) 
        try:
            self.bg_image = pygame.image.load(os.path.join(img_path, "game_bg.png"))
            self.bg_image = pygame.transform.scale(self.bg_image, (self.screen_width, self.screen_height))
        except: self.bg_image = None
        try:
            self.sound_move = pygame.mixer.Sound(os.path.join(sound_path, "move.wav"))
            self.sound_capture = pygame.mixer.Sound(os.path.join(sound_path, "capture.wav"))
            self.sound_check = pygame.mixer.Sound(os.path.join(sound_path, "check.wav"))
        except:
            self.sound_move = pygame.mixer.Sound(pygame.compat.BytesIO())
            self.sound_capture = pygame.mixer.Sound(pygame.compat.BytesIO())
            self.sound_check = pygame.mixer.Sound(pygame.compat.BytesIO())
    
    def load_piece_images(self):
        assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'pieces')
        for piece in self.pieces_unicode.keys():
            image_path = os.path.join(assets_path, f'{piece}.png')
            if os.path.exists(image_path):
                try:
                    image = pygame.image.load(image_path).convert_alpha()
                    self.piece_images[piece] = pygame.transform.scale(image, (self.SQUARE_SIZE - 20, self.SQUARE_SIZE - 20))
                except: pass

    def draw_board(self, board):
        if self.bg_image: self.screen.blit(self.bg_image, (0, 0))
        else: self.screen.fill((30, 30, 30))

        # Vẽ nền bàn cờ
        board_surface = pygame.Surface((self.BOARD_SIZE + 10, self.BOARD_SIZE + 10))
        board_surface.set_alpha(220)
        board_surface.fill((235, 235, 235))
        self.screen.blit(board_surface, (self.board_x - 5, self.board_y - 5))

        # Vẽ ô cờ
        for row in range(8):
            for col in range(8):
                x = self.board_x + col * self.SQUARE_SIZE
                y = self.board_y + row * self.SQUARE_SIZE
                rect = pygame.Rect(x, y, self.SQUARE_SIZE, self.SQUARE_SIZE)
                
                color = self.WHITE_SQUARE if (row + col) % 2 == 0 else self.BLACK_SQUARE
                pygame.draw.rect(self.screen, color, rect)
                
                # Highlight Check
                if self.in_check_square == (row, col):
                    s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
                    s.fill(self.CHECK_HIGHLIGHT_COLOR)
                    self.screen.blit(s, (x, y))
                
                # Highlight Selected
                if self.selected_square == (row, col):
                    pygame.draw.rect(self.screen, self.SELECTED_BORDER_COLOR, rect, 4, border_radius=5)
                
                # Highlight Valid Move
                if (row, col) in self.valid_moves_highlight and self.selected_square != (row, col):
                    center_x = x + self.SQUARE_SIZE // 2
                    center_y = y + self.SQUARE_SIZE // 2
                    if board[row][col]: 
                        pygame.draw.circle(self.screen, self.VALID_MOVE_COLOR[:3], (center_x, center_y), self.SQUARE_SIZE // 2 - 5, 5)
                    else: 
                        pygame.draw.circle(self.screen, self.VALID_MOVE_COLOR[:3], (center_x, center_y), 10)

        # Vẽ tọa độ
        for col in range(8):
            l = chr(ord('a') + col)
            t = self.coord_font.render(l, True, self.TEXT_COLOR)
            self.screen.blit(t, (self.board_x + col * self.SQUARE_SIZE + 25, self.board_y + self.BOARD_SIZE + 5))
        for row in range(8):
            n = str(8 - row)
            t = self.coord_font.render(n, True, self.TEXT_COLOR)
            self.screen.blit(t, (self.board_x - 25, self.board_y + row * self.SQUARE_SIZE + 25))

    def draw_pieces(self, board):
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece and not (self.dragging and self.selected_square == (row, col)):
                    x = self.board_x + col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    y = self.board_y + row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    if piece in self.piece_images:
                        image = self.piece_images[piece]
                        image_rect = image.get_rect(center=(x, y))
                        self.screen.blit(image, image_rect)
                    else:
                        # Fallback
                        t = self.piece_font.render(self.pieces_unicode.get(piece, "?"), True, (0,0,0))
                        self.screen.blit(t, (x-20, y-30))

    def draw_dragging_piece(self):
        if self.dragging and self.drag_piece:
            if self.drag_piece in self.piece_images:
                img = self.piece_images[self.drag_piece]
                new_size = self.SQUARE_SIZE + 10
                big_img = pygame.transform.scale(img, (new_size, new_size))
                self.screen.blit(big_img, big_img.get_rect(center=self.drag_pos))
            else:
                t = self.piece_font.render(self.pieces_unicode.get(self.drag_piece, "?"), True, (0,0,0))
                self.screen.blit(t, self.drag_pos)

    def get_square_from_pos(self, pos):
        x, y = pos
        if x < self.board_x or x >= self.board_x + 8 * self.SQUARE_SIZE or \
           y < self.board_y or y >= self.board_y + 8 * self.SQUARE_SIZE:
            return None
        col = (x - self.board_x) // self.SQUARE_SIZE
        row = (y - self.board_y) // self.SQUARE_SIZE
        return (row, col)

    def handle_mouse_down(self, pos, board, current_player_color):
        square = self.get_square_from_pos(pos)
        if square:
            row, col = square
            piece = board[row][col]
            if piece and piece[0] == current_player_color:
                self.selected_square = square
                self.dragging = True
                self.drag_piece = piece
                self.drag_pos = pos
                return True
        return False
    
    def handle_mouse_motion(self, pos):
        if self.dragging:
            self.drag_pos = pos

    def handle_button_click(self, pos):
        if self.exit_button.collidepoint(pos): return "exit"
        elif self.surrender_button.collidepoint(pos): return "surrender"
        elif self.undo_button.collidepoint(pos): return "undo"
        elif self.save_button.collidepoint(pos): return "save"
        elif self.restart_button.collidepoint(pos): return "restart"
        return None
    
    def show_promotion_dialog(self, color):
        pieces = ['Q', 'R', 'B', 'N']
        piece_names = ['Hậu', 'Xe', 'Tượng', 'Mã']
        dialog_width = 400
        dialog_height = 180
        dialog_x = (self.screen_width - dialog_width) // 2
        dialog_y = (self.screen_height - dialog_height) // 2
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        pygame.draw.rect(self.screen, (255, 255, 255), (dialog_x, dialog_y, dialog_width, dialog_height), border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), (dialog_x, dialog_y, dialog_width, dialog_height), 2, border_radius=10)
        title = self.font_title.render("Chọn quân phong cấp:", True, (0, 0, 0))
        title_rect = title.get_rect(center=(dialog_x + dialog_width//2, dialog_y + 30))
        self.screen.blit(title, title_rect)
        piece_size = 60
        start_x = dialog_x + 50
        y = dialog_y + 80
        rects = []
        for i, (piece, name) in enumerate(zip(pieces, piece_names)):
            x = start_x + i * 80
            rect = pygame.Rect(x, y, piece_size, piece_size)
            rects.append((rect, piece))
            pygame.draw.rect(self.screen, (240, 240, 240), rect, border_radius=5)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1, border_radius=5)
            piece_key = f'{color}{piece}'
            if piece_key in self.piece_images:
                image = pygame.transform.scale(self.piece_images[piece_key], (piece_size-10, piece_size-10))
                image_rect = image.get_rect(center=rect.center)
                self.screen.blit(image, image_rect)
            name_text = self.font_history.render(name, True, (0, 0, 0))
            name_rect = name_text.get_rect(center=(x + piece_size//2, y + piece_size + 15))
            self.screen.blit(name_text, name_rect)
        pygame.display.flip()
        return rects

    def handle_promotion_click(self, pos, rects):
        for rect, piece in rects:
            if rect.collidepoint(pos): return piece
        return None

    def format_move(self, move):
        figurine_map = {'wK': 'K', 'wQ': 'Q', 'wR': 'R', 'wB': 'B', 'wN': 'N', 'wP': '', 'bK': 'K', 'bQ': 'Q', 'bR': 'R', 'bB': 'B', 'bN': 'N', 'bP': ''}
        piece_symbol = figurine_map.get(move['piece'], '')
        if move['piece'][1] == 'P': piece_symbol = ""
        to_square = f"{chr(ord('a') + move['to_pos'][1])}{8 - move['to_pos'][0]}"
        capture_symbol = "x" if move['captured_piece'] else ""
        if move['piece'][1] == 'P' and capture_symbol:
            from_col = f"{chr(ord('a') + move['from_pos'][1])}"
            piece_symbol = from_col
        if move['piece'][1] == 'K':
            if abs(move['to_pos'][1] - move['from_pos'][1]) == 2:
                if move['to_pos'][1] == 6: return "O-O"
                if move['to_pos'][1] == 2: return "O-O-O"
        return f"{piece_symbol}{capture_symbol}{to_square}"

    def draw_ip_info(self):
        # Disabled for online mode - IP info not needed
        pass

    def draw_status_messages(self, player_color=None):
        x_pos = self.history_x_pos 
        y_pos = 210 
        if player_color:
            c = "WHITE" if player_color == 'white' else "BLACK"
            s = self.font_status.render(f"You are: {c}", True, self.BTN_BLUE)
            self.screen.blit(s, (x_pos, y_pos))
            y_pos += 30 
        if self.ai_thinking_message:
            t = self.font_status.render("AI is thinking...", True, self.BTN_BLUE)
            self.screen.blit(t, (x_pos, y_pos))
        elif self.turn_message:
            t = self.font_status.render(self.turn_message, True, self.TEXT_COLOR)
            self.screen.blit(t, (x_pos, y_pos))

    def draw_game_over_overlay(self):
        """Vẽ màn hình kết quả trận đấu đẹp với nút Chơi lại và Thoát"""
        # Overlay tối
        o = pygame.Surface((self.screen_width, self.screen_height))
        o.set_alpha(200)
        o.fill((0, 0, 0))
        self.screen.blit(o, (0, 0))
        
        # Box kết quả
        box_width = 600
        box_height = 400
        box_x = (self.screen_width - box_width) // 2
        box_y = (self.screen_height - box_height) // 2
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        # Vẽ box với shadow
        shadow_rect = box_rect.copy()
        shadow_rect.move_ip(8, 8)
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=20)
        
        pygame.draw.rect(self.screen, (255, 255, 255), box_rect, border_radius=20)
        pygame.draw.rect(self.screen, self.BTN_BLUE, box_rect, 5, border_radius=20)
        
        # Title
        title_text = self.font_game_over.render("TRẬN ĐẤU KẾT THÚC", True, self.BTN_BLUE)
        title_rect = title_text.get_rect(center=(box_rect.centerx, box_y + 60))
        self.screen.blit(title_text, title_rect)
        
        # Result message
        result_color = self.BTN_GREEN_RESTART if "wins" in self.game_over_message.lower() or "won" in self.game_over_message.lower() else self.BTN_GRAY
        if "draw" in self.game_over_message.lower() or "stalemate" in self.game_over_message.lower():
            result_color = self.BTN_YELLOW
        
        result_text = self.font_title.render(self.game_over_message, True, result_color)
        result_rect = result_text.get_rect(center=(box_rect.centerx, box_rect.centery - 20))
        self.screen.blit(result_text, result_rect)
        
        # Buttons
        button_width = 220
        button_height = 60
        button_y = box_rect.bottom - 100
        button_spacing = 40
        
        # Play Again Button
        play_again_rect = pygame.Rect(
            box_rect.centerx - button_width - button_spacing//2,
            button_y,
            button_width,
            button_height
        )
        mouse_pos = pygame.mouse.get_pos()
        play_color = self.BTN_GREEN_RESTART_HOVER if play_again_rect.collidepoint(mouse_pos) else self.BTN_GREEN_RESTART
        pygame.draw.rect(self.screen, play_color, play_again_rect, border_radius=12)
        play_text = self.font_button_main.render("CHƠI LẠI", True, (255, 255, 255))
        play_text_rect = play_text.get_rect(center=play_again_rect.center)
        self.screen.blit(play_text, play_text_rect)
        
        # Exit Button
        exit_rect = pygame.Rect(
            box_rect.centerx + button_spacing//2,
            button_y,
            button_width,
            button_height
        )
        exit_color = self.BTN_RED_HOVER if exit_rect.collidepoint(mouse_pos) else self.BTN_RED
        pygame.draw.rect(self.screen, exit_color, exit_rect, border_radius=12)
        exit_text = self.font_button_main.render("THOÁT", True, (255, 255, 255))
        exit_text_rect = exit_text.get_rect(center=exit_rect.center)
        self.screen.blit(exit_text, exit_text_rect)
        
        # Lưu rect để xử lý click
        self.game_over_play_again_rect = play_again_rect
        self.game_over_exit_rect = exit_rect
        
    def draw_save_message(self):
        x = self.save_button.left; y = self.save_button.bottom + 10
        t = self.font_save_msg.render("Game Saved!", True, self.BTN_YELLOW)
        pygame.draw.rect(self.screen, (50,50,50), (x, y, 150, 30), border_radius=5)
        self.screen.blit(t, (x+10, y+5))

    def play_move_sound(self): self.sound_move.play()
    def play_capture_sound(self): self.sound_capture.play()
    def play_check_sound(self): self.sound_check.play()

    def draw_captured_pieces(self, white_list, black_list):
        # Không hiển thị quân cờ bị bắt
        pass

    def draw_clocks(self, white_time, black_time, current_player):
        x = self.history_x_pos; w = self.history_width; h = 70
        rb = pygame.Rect(x, 50, w, h)
        cb = (255,255,255) if current_player == 'black' else (200,200,200)
        pygame.draw.rect(self.screen, cb, rb, border_radius=10)
        mb, sb = divmod(int(black_time), 60)
        tb = self.font_clock.render(f"{mb:02}:{sb:02}", True, (0,0,0))
        self.screen.blit(tb, tb.get_rect(center=rb.center))
        rw = pygame.Rect(x, 130, w, h)
        cw = (255,255,255) if current_player == 'white' else (200,200,200)
        pygame.draw.rect(self.screen, cw, rw, border_radius=10)
        mw, sw = divmod(int(white_time), 60)
        tw = self.font_clock.render(f"{mw:02}:{sw:02}", True, (0,0,0))
        self.screen.blit(tw, tw.get_rect(center=rw.center))

    def draw_move_history(self, move_history):
        hx = self.history_x_pos; hy = self.history_y_pos; hw = self.history_width; hh = self.history_height
        t = self.font_title.render("Move History", True, self.TEXT_COLOR)
        self.screen.blit(t, (hx, hy - 50))
        pygame.draw.rect(self.screen, (255,255,255), (hx, hy, hw, hh), border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), (hx, hy, hw, hh), 2, border_radius=10)
        max_l = 15
        start = max(0, len(move_history) - max_l)
        y_off = 10
        for i, m in enumerate(move_history[start:]):
            num = start + i + 1
            piece = m['piece'][1] if m['piece'][1] != 'P' else ''
            fr = f"{chr(ord('a')+m['from_pos'][1])}{8-m['from_pos'][0]}"
            to = f"{chr(ord('a')+m['to_pos'][1])}{8-m['to_pos'][0]}"
            txt = f"{num}. {piece}{fr}-{to}"
            col = (0,0,0) if m['player'] == 'white' else (100,100,100)
            s = self.font_history.render(txt, True, col)
            draw_x = hx + 10 if m['player'] == 'white' else hx + 110
            self.screen.blit(s, (draw_x, hy + y_off))
            if m['player'] == 'black': y_off += 20

    def draw_button_styled(self, rect, text, color, hover, pos):
        c = hover if rect.collidepoint(pos) else color
        pygame.draw.rect(self.screen, c, rect, border_radius=10)
        t = self.button_font.render(text, True, (255,255,255))
        self.screen.blit(t, t.get_rect(center=rect.center))

    def draw_buttons(self, ai_mode=False):
        # Nút Switch View bị xóa
        self.draw_button_styled(self.undo_button, "UNDO", self.BTN_BLUE, self.BTN_BLUE_HOVER, pygame.mouse.get_pos())
        self.draw_button_styled(self.restart_button, "RESTART", self.BTN_GREEN_RESTART, self.BTN_GREEN_RESTART_HOVER, pygame.mouse.get_pos())
        self.draw_button_styled(self.save_button, "SAVE GAME", self.BTN_YELLOW, self.BTN_YELLOW_HOVER, pygame.mouse.get_pos())
        self.draw_button_styled(self.exit_button, "EXIT", self.BTN_GRAY, self.BTN_GRAY_HOVER, pygame.mouse.get_pos())
        if ai_mode:
            self.draw_button_styled(self.surrender_button, "SURRENDER", self.BTN_RED, self.BTN_RED_HOVER, pygame.mouse.get_pos())

    def draw(self, board, mouse_pos, current_player, ai_mode=False, move_history=None,
             valid_moves=None, in_check_square=None, game_over_message=None, ai_thinking=False,
             save_message_timer=0, white_captured=None, black_captured=None,
             white_time=0, black_time=0, player_color=None, current_user=None):
        
        self.valid_moves_highlight = valid_moves if valid_moves else []
        self.in_check_square = in_check_square
        self.game_over_message = game_over_message
        self.ai_thinking_message = ai_thinking
        if not game_over_message:
            self.turn_message = f"Turn: {'White' if current_player == 'white' else 'Black'}"
        else:
            self.turn_message = ""

        self.draw_board(board)
        self.draw_pieces(board)
        self.draw_dragging_piece()
        self.draw_buttons(ai_mode)
        self.draw_ip_info()
        self.draw_status_messages(player_color)
        self.draw_clocks(white_time, black_time, current_player)
        self.draw_captured_pieces(white_captured, black_captured)
        
        if current_user:
            t = self.font_user_info.render(f"Player: {current_user['username']}", True, self.TEXT_COLOR)
            self.screen.blit(t, (self.screen_width - 250, 20))

        if move_history: self.draw_move_history(move_history)
        if self.game_over_message: self.draw_game_over_overlay()
        if save_message_timer > 0: self.draw_save_message()
        
        pygame.display.flip()