import pygame
import sys
import json
from .board import Board
from .gui import ChessGUI
from .network_client import ChessClient
import threading
import time

class OnlineChessGame:
    def __init__(self, server_ip='localhost', is_host=False, current_user=None, db=None, client=None):
        try:
            self.board = Board()
            self.gui = ChessGUI(server_ip)
            self.clock = pygame.time.Clock()
            self.running = True
            self.waiting_for_promotion = False
            self.promotion_move = None
            
            self.valid_moves = []
            self.in_check_square = None
            self.game_over_message = None
            
            self.white_captured_pieces = []
            self.black_captured_pieces = []
            
            self.initial_time = 300 
            self.white_time = self.initial_time
            self.black_time = self.initial_time
            self.last_tick = pygame.time.get_ticks()
            
            # Database & User (MỚI)
            self.current_user = current_user
            self.db = db
            self.is_host = is_host
            
            # Initialize color variables first
            self.my_color_char = None
            self.my_color_full = None # 'white' hoặc 'black'
            self.opponent_connected = False
            self.game_started = False
            
            # Network client (có thể dùng client có sẵn từ OnlineMenu)
            if client:
                self.client = client
                # Lấy color từ client đã connect
                if hasattr(client, 'color') and client.color:
                    self.my_color_full = client.color
                    self.my_color_char = 'w' if self.my_color_full == 'white' else 'b'
                    self.game_started = True
                    self.opponent_connected = True
                    print(f"Initialized with color: {self.my_color_full}")
            else:
                self.client = ChessClient()
                if not self.client.connect(server_ip):
                    print("Failed to connect to server!")
                    self.running = False
                    return
            
            self.server_ip = server_ip
            self.network_status = "Connecting..."
            
            self.client.set_message_callback(self.handle_network_message)
            
        except Exception as e:
            print(f"Error initializing online game: {e}")
            raise
    
    def handle_network_message(self, message):
        """Xử lý tin nhắn từ server (chạy trên thread riêng)"""
        try:
            if message['type'] == 'player_info':
                self.my_color_full = message['color']
                self.my_color_char = 'w' if self.my_color_full == 'white' else 'b'
                print(f"You are playing as {self.my_color_full}")
            
            elif message['type'] == 'game_start':
                self.game_started = True
                self.opponent_connected = True
                self.network_status = "Opponent connected!"
                print("Game started! Both players connected.")
            
            elif message['type'] == 'move':
                from_pos = tuple(message['from_pos'])
                to_pos = tuple(message['to_pos'])
                # (SỬA) Nhận quân phong cấp từ đối thủ
                promotion = message.get('promotion', 'Q') 
                
                # --- Logic kiểm tra ăn quân (để phát âm thanh) ---
                target = self.board.board[to_pos[0]][to_pos[1]]
                is_capture = target is not None
                captured_piece = target
                
                piece = self.board.board[from_pos[0]][from_pos[1]]
                if (piece and piece[1] == 'P' and
                    (to_pos[0], to_pos[1]) == self.board.en_passant_target_square and target is None):
                    is_capture = True
                    direction = -1 if self.my_color_char == 'b' else 1
                    captured_piece_pos = (to_pos[0] + direction, to_pos[1])
                    captured_piece = self.board.board[captured_piece_pos[0]][captured_piece_pos[1]]
                
                # Thực hiện nước đi
                result = self.board.make_move(from_pos, to_pos, promotion)
                
                # Cập nhật GUI
                self.update_game_state(result)
                if is_capture and captured_piece:
                    if captured_piece[0] == 'w': self.white_captured_pieces.append(captured_piece)
                    else: self.black_captured_pieces.append(captured_piece)
                
                # Phát âm thanh
                if result == 'checkmate': self.gui.play_check_sound()
                elif self.board.is_in_check(): self.gui.play_check_sound()
                elif is_capture: self.gui.play_capture_sound()
                else: self.gui.play_move_sound()
                
                print(f"Opponent moved: {from_pos} -> {to_pos}")
            
            elif message['type'] == 'game_over':
                if message['reason'] == 'opponent_disconnected':
                    self.game_over_message = "Opponent Disconnected!"
                    # Người chơi này thắng vì đối thủ mất kết nối
                    self.save_match_result(self.my_color_full, 'disconnect')
                    
                elif message['winner'] == 'you':
                    self.game_over_message = "You Won! Opponent Surrendered."
                    # Người chơi này thắng vì đối thủ đầu hàng
                    self.save_match_result(self.my_color_full, 'surrender')
                else:
                    self.game_over_message = "You Lost! (You Surrendered)"
                    # Người chơi này thua vì đã đầu hàng
                    opponent_color = 'white' if self.my_color_full == 'black' else 'black'
                    self.save_match_result(opponent_color, 'surrender')
        except Exception as e:
            print(f"Error handling network message: {e}")

    def can_move(self):
        """Kiểm tra có thể di chuyển không"""
        if not self.game_started or self.game_over_message:
            return False
        return self.board.current_player == self.my_color_full
    
    def make_move(self, from_pos, to_pos, promotion_piece='Q'):
        """Thực hiện nước đi (của người chơi này)"""
        if not self.can_move():
            print("Not your turn!")
            return False
        
        target_piece = self.board.board[to_pos[0]][to_pos[1]]
        is_capture = target_piece is not None
        captured_piece_for_list = target_piece
        
        piece = self.board.board[from_pos[0]][from_pos[1]]
        if (piece and piece[1] == 'P' and
            (to_pos[0], to_pos[1]) == self.board.en_passant_target_square and
            target_piece is None):
            is_capture = True
            direction = -1 if piece[0] == 'w' else 1
            captured_pawn_pos = (to_pos[0] + direction, to_pos[1])
            captured_piece_for_list = self.board.board[captured_pawn_pos[0]][captured_pawn_pos[1]]

        result = self.board.make_move(from_pos, to_pos, promotion_piece)
        
        if result:
            self.update_game_state(result)
            if is_capture and captured_piece_for_list:
                if captured_piece_for_list[0] == 'w':
                    self.white_captured_pieces.append(captured_piece_for_list)
                else:
                    self.black_captured_pieces.append(captured_piece_for_list)
            
            if result == 'checkmate': self.gui.play_check_sound()
            elif self.board.is_in_check(): self.gui.play_check_sound()
            elif is_capture: self.gui.play_capture_sound()
            else: self.gui.play_move_sound()
            
            self.client.send_move(from_pos, to_pos, promotion_piece)
            return result
        return False
        
    def save_match_result(self, winner_color, result_type='checkmate'):
        """Lưu kết quả trận đấu vào database của người chơi này"""
        if not self.current_user or not self.db:
            return
        
        try:
            # current_user là dict chứa user info
            user_id = self.current_user.get('id')
            username = self.current_user.get('username')
            
            if not user_id:
                print("Cannot save: user_id not found")
                return
            
            # Xác định kết quả từ góc nhìn của người chơi này
            if result_type == 'draw' or result_type == 'stalemate':
                result = 'draw'
                elo_change = 0
                won = False
            elif winner_color == self.my_color_full:
                result = 'win'
                elo_change = 25
                won = True
            else:
                result = 'loss'
                elo_change = -15
                won = False
            
            # Lưu kết quả trận đấu
            self.db.save_match_result(
                user_id=user_id,
                opponent="Online Player",
                result=result
            )
            
            # Cập nhật stats (ELO, số trận, số thắng)
            self.db.update_stats(
                user_id=user_id,
                won=won,
                elo_change=elo_change
            )
            
            print(f"[{username}] Match result saved: {result} (ELO: {elo_change:+d})")
        except Exception as e:
            print(f"Error saving match result: {e}")
            import traceback
            traceback.print_exc()
    
    def update_game_state(self, last_move_result):
        if last_move_result == 'checkmate':
            winner = "White" if self.board.current_player == 'black' else "Black"
            self.game_over_message = f"Checkmate! {winner} wins!"
            
            # Lưu kết quả vào database
            winner_color = 'white' if self.board.current_player == 'black' else 'black'
            self.save_match_result(winner_color, 'checkmate')
            
        elif last_move_result == 'stalemate':
            self.game_over_message = "Stalemate! It's a draw."
            
            # Lưu kết quả hòa
            self.save_match_result(None, 'stalemate')
        
        if self.board.is_in_check():
            self.in_check_square = self.board.get_king_square(self.board.current_player)
        else:
            self.in_check_square = None
        self.valid_moves = []
        
    def check_promotion(self, from_pos, to_pos):
        piece = self.board.board[from_pos[0]][from_pos[1]]
        if piece and piece[1] == 'P':
            if (piece[0] == 'w' and to_pos[0] == 0) or (piece[0] == 'b' and to_pos[0] == 7):
                return True
        return False
    
    def run(self):
        """Chạy game loop (phiên bản online)"""
        print(f"Waiting for game to start... My color: {self.my_color_full}")
        self.last_tick = pygame.time.get_ticks()
        
        while self.running:
            try:
                current_ticks = pygame.time.get_ticks()
                delta_time = (current_ticks - self.last_tick) / 1000.0
                self.last_tick = current_ticks
                if self.game_started and not self.game_over_message:
                    if self.board.current_player == 'white':
                        self.white_time -= delta_time
                        if self.white_time <= 0:
                            self.white_time = 0
                            self.game_over_message = "Time's up! Black wins!"
                    else:
                        self.black_time -= delta_time
                        if self.black_time <= 0:
                            self.black_time = 0
                            self.game_over_message = "Time's up! White wins!"
                
                mouse_pos = pygame.mouse.get_pos()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if self.game_over_message:
                                # Xử lý click vào nút trong màn hình game over
                                if hasattr(self.gui, 'game_over_play_again_rect') and self.gui.game_over_play_again_rect.collidepoint(mouse_pos):
                                    # Online không có chơi lại, chỉ thoát
                                    self.running = False
                                    continue
                                elif hasattr(self.gui, 'game_over_exit_rect') and self.gui.game_over_exit_rect.collidepoint(mouse_pos):
                                    # Thoát về menu chính
                                    self.running = False
                                    continue
                                # Click bất kỳ nơi nào khác cũng không làm gì
                                continue
                            button_action = self.gui.handle_button_click(mouse_pos)
                            if button_action == "exit":
                                self.running = False
                                continue
                            elif button_action == "surrender":
                                self.client.send_surrender()
                                self.game_over_message = "You Surrendered!"
                                print("You surrendered!")
                                continue
                            elif button_action == "undo" or button_action == "save" or button_action == "restart":
                                print("This feature is disabled in online mode.")
                                continue
                            if not self.can_move():
                                print("Wait for your turn or opponent to connect...")
                                continue
                            if self.waiting_for_promotion:
                                selected_piece = self.gui.handle_promotion_click(mouse_pos, self.promotion_rects)
                                if selected_piece:
                                    result = self.make_move(self.promotion_move[0], self.promotion_move[1], selected_piece)
                                    self.waiting_for_promotion = False
                                    self.promotion_move = None
                            else:
                                try:
                                    clicked_square = self.gui.get_square_from_pos(mouse_pos)
                                    if clicked_square:
                                        success = self.gui.handle_mouse_down(mouse_pos, self.board.board, self.my_color_char)
                                        if success:
                                            self.valid_moves = self.board.get_valid_moves(self.gui.selected_square)
                                        else:
                                            self.valid_moves = []
                                except Exception as e:
                                    print(f"Mouse down error: {e}")
                    
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1 and not self.waiting_for_promotion and self.can_move():
                            try:
                                if self.gui.dragging and self.gui.selected_square:
                                    target_square = self.gui.get_square_from_pos(mouse_pos)
                                    if target_square and target_square in self.valid_moves:
                                        if self.check_promotion(self.gui.selected_square, target_square):
                                            piece = self.board.board[self.gui.selected_square[0]][self.gui.selected_square[1]]
                                            self.promotion_rects = self.gui.show_promotion_dialog(piece[0])
                                            self.waiting_for_promotion = True
                                            self.promotion_move = (self.gui.selected_square, target_square)
                                        else:
                                            result = self.make_move(self.gui.selected_square, target_square)
                                    self.gui.dragging = False
                                    self.gui.drag_piece = None
                                    self.gui.selected_square = None
                                    self.valid_moves = []
                            except Exception as e:
                                print(f"Mouse up error: {e}")
                    
                    elif event.type == pygame.MOUSEMOTION:
                        if not self.waiting_for_promotion and self.can_move():
                            try:
                                self.gui.handle_mouse_motion(mouse_pos)
                            except Exception as e:
                                print(f"Mouse motion error: {e}")
                
                try:
                    if not self.game_started:
                        if not self.opponent_connected:
                            self.network_status = "Waiting for opponent..."
                        else:
                            self.network_status = "Game starting..."
                    
                    self.gui.draw(
                        board=self.board.board, 
                        mouse_pos=mouse_pos, 
                        current_player=self.board.current_player,
                        ai_mode=False,
                        move_history=self.board.move_history,
                        valid_moves=self.valid_moves,
                        in_check_square=self.in_check_square,
                        game_over_message=self.game_over_message,
                        ai_thinking= (not self.game_started), # Dùng cờ này để hiện "Waiting..."
                        save_message_timer=0,
                        white_captured=self.white_captured_pieces,
                        black_captured=self.black_captured_pieces,
                        white_time=self.white_time,
                        black_time=self.black_time,
                        player_color=self.my_color_full
                    )
                    
                    if self.waiting_for_promotion:
                        piece = self.board.board[self.promotion_move[0][0]][self.promotion_move[0][1]]
                        self.promotion_rects = self.gui.show_promotion_dialog(piece[0])

                except Exception as e:
                    print(f"Draw error: {e}")
                
                self.clock.tick(60)
                
            except Exception as e:
                print(f"Game loop error: {e}")
                continue
        
        self.client.disconnect()
        print("Online game loop ended!")