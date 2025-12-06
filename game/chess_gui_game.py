import pygame
import sys
import json
from .board import Board
from .gui import ChessGUI
from .ai_engine import AIEngine
import threading
import time

class ChessGUIGame:
    # (SỬA) Nhận thêm tham số db
    def __init__(self, ai_mode=False, difficulty="medium", current_user=None, db=None):
        try:
            self.board = Board()
            self.gui = ChessGUI()
            self.clock = pygame.time.Clock()
            self.running = True
            self.waiting_for_promotion = False
            self.promotion_move = None
            
            self.valid_moves = []
            self.in_check_square = None
            self.game_over_message = None
            self.ai_thinking = False
            self.save_message_timer = 0
            self.match_saved = False # Cờ để tránh lưu trùng lặp
            
            self.initial_ai_mode = ai_mode
            self.initial_difficulty = difficulty
            self.current_user = current_user
            self.db = db # (MỚI) Lưu db
            
            self.white_captured_pieces = []
            self.black_captured_pieces = []
            self.initial_time = 300 
            self.white_time = self.initial_time
            self.black_time = self.initial_time
            self.last_tick = pygame.time.get_ticks()
            
            self.ai_mode = ai_mode
            self.ai_engine = None
            if self.ai_mode:
                self.ai_engine = AIEngine(difficulty=self.initial_difficulty) 
                if not self.ai_engine.start_engine():
                    self.ai_mode = False
        except Exception as e:
            print(f"Error initializing game: {e}")
            raise
    
    def save_match_result(self, result_type):
        """(MỚI) Lưu kết quả trận đấu"""
        if self.match_saved or not self.current_user or not self.db:
            return

        user_id = self.current_user['id']
        opponent = "AI (" + self.initial_difficulty + ")" if self.ai_mode else "Player 2"
        
        # Xác định thắng thua
        final_result = "Draw"
        elo_change = 0
        
        if result_type == "checkmate":
            # Nếu lượt hiện tại là Trắng => Trắng bị chiếu => Đen thắng
            winner_color = 'black' if self.board.current_player == 'white' else 'white'
            
            # User luôn là Trắng khi đánh với AI
            if self.ai_mode:
                if winner_color == 'white':
                    final_result = "Win"
                    elo_change = 20
                else:
                    final_result = "Loss"
                    elo_change = -10
            else:
                # PvP Local: Ai thắng thì cũng ghi là thắng (vì chung máy)
                # Hoặc chỉ lưu cho người đăng nhập
                final_result = f"{winner_color.title()} Won"
                
        elif result_type == "stalemate":
            final_result = "Draw"
            elo_change = 5
        elif result_type == "surrender":
            final_result = "Loss"
            elo_change = -10

        # Lưu vào DB
        self.db.save_match_result(user_id, opponent, final_result)
        if self.ai_mode: # Chỉ tính ELO khi đánh với AI
            self.db.update_stats(user_id, final_result == "Win", elo_change)
        
        self.match_saved = True
        print(f"Match saved: {final_result}")

    def make_move(self, from_pos, to_pos, promotion_piece='Q'):
        target_piece = self.board.board[to_pos[0]][to_pos[1]]
        is_capture = target_piece is not None
        piece = self.board.board[from_pos[0]][from_pos[1]]
        captured_piece_for_list = None
        if (piece and piece[1] == 'P' and
            (to_pos[0], to_pos[1]) == self.board.en_passant_target_square and
            target_piece is None):
            is_capture = True
            direction = -1 if piece[0] == 'w' else 1
            captured_pawn_pos = (to_pos[0] + direction, to_pos[1])
            captured_piece_for_list = self.board.board[captured_pawn_pos[0]][captured_pawn_pos[1]]
        else:
            captured_piece_for_list = target_piece
        result = self.board.make_move(from_pos, to_pos, promotion_piece)
        self.update_game_state(result)
        if is_capture and captured_piece_for_list:
            if captured_piece_for_list[0] == 'w':
                self.white_captured_pieces.append(captured_piece_for_list)
            else:
                self.black_captured_pieces.append(captured_piece_for_list)
        
        # (SỬA) Gọi lưu kết quả
        if result == 'checkmate':
            self.gui.play_check_sound()
            self.save_match_result("checkmate")
        elif result == 'stalemate':
            self.save_match_result("stalemate")
        elif self.board.is_in_check():
            self.gui.play_check_sound()
        elif is_capture:
            self.gui.play_capture_sound()
        elif result:
            self.gui.play_move_sound()
        return result

    def update_game_state(self, last_move_result):
        if last_move_result == 'checkmate':
            winner = "White" if self.board.current_player == 'black' else "Black"
            self.game_over_message = f"Checkmate! {winner} wins!"
        elif last_move_result == 'stalemate':
            self.game_over_message = "Stalemate! It's a draw."
        if self.board.is_in_check():
            self.in_check_square = self.board.get_king_square(self.board.current_player)
        else:
            self.in_check_square = None
        self.valid_moves = []
        
    # (Các hàm make_ai_move, check_promotion, restart_game giữ nguyên...)
    # ... (Do giới hạn ký tự, bạn giữ nguyên các hàm không thay đổi) ...
    def make_ai_move(self):
        if not self.ai_mode or not self.ai_engine or self.ai_thinking: return
        def ai_move_thread():
            self.ai_thinking = True
            fen = self.board.get_fen()
            move_str = self.ai_engine.get_best_move(fen)
            if move_str:
                from_pos, to_pos = self.ai_engine.convert_move_to_coords(move_str)
                if from_pos and to_pos:
                    if self.check_promotion(from_pos, to_pos): result = self.make_move(from_pos, to_pos, 'Q')
                    else: result = self.make_move(from_pos, to_pos)
            self.ai_thinking = False
        threading.Thread(target=ai_move_thread, daemon=True).start()

    def check_promotion(self, from_pos, to_pos):
        piece = self.board.board[from_pos[0]][from_pos[1]]
        if piece and piece[1] == 'P':
            if (piece[0] == 'w' and to_pos[0] == 0) or (piece[0] == 'b' and to_pos[0] == 7): return True
        return False

    def restart_game(self):
        self.board = Board()
        self.waiting_for_promotion = False
        self.promotion_move = None
        self.valid_moves = []
        self.in_check_square = None
        self.game_over_message = None
        self.ai_thinking = False
        self.save_message_timer = 0
        self.match_saved = False # Reset cờ
        self.white_captured_pieces = []
        self.black_captured_pieces = []
        self.white_time = self.initial_time
        self.black_time = self.initial_time
        self.last_tick = pygame.time.get_ticks()
        self.ai_mode = self.initial_ai_mode
        if self.ai_engine: self.ai_engine.stop_engine()
        if self.ai_mode:
            self.ai_engine = AIEngine(difficulty=self.initial_difficulty)
            self.ai_engine.start_engine()
        self.update_game_state(None)
        self.gui.play_move_sound()

    def rebuild_captured_lists(self):
        self.white_captured_pieces = []
        self.black_captured_pieces = []
        for move in self.board.move_history:
            captured = move.get('captured_piece')
            if captured:
                if captured[0] == 'w': self.white_captured_pieces.append(captured)
                else: self.black_captured_pieces.append(captured)

    def run(self):
        print("Game started! First turn: white")
        if self.ai_mode:
            print(f"AI Mode: You are WHITE, AI is BLACK (Difficulty: {self.ai_engine.difficulty})")
        self.update_game_state(None)
        self.last_tick = pygame.time.get_ticks()
        while self.running:
            try:
                current_ticks = pygame.time.get_ticks()
                delta_time = (current_ticks - self.last_tick) / 1000.0
                self.last_tick = current_ticks
                if not self.game_over_message and not self.ai_thinking:
                    if self.board.current_player == 'white':
                        self.white_time -= delta_time
                        if self.white_time <= 0:
                            self.white_time = 0
                            self.game_over_message = "Time's up! Black wins!"
                            self.save_match_result("checkmate") # Time out = Lose
                    else:
                        self.black_time -= delta_time
                        if self.black_time <= 0:
                            self.black_time = 0
                            self.game_over_message = "Time's up! White wins!"
                            self.save_match_result("checkmate")
                mouse_pos = pygame.mouse.get_pos()
                if self.save_message_timer > 0: self.save_message_timer -= 1
                current_player_color = 'w' if self.board.current_player == 'white' else 'b'
                if (self.ai_mode and current_player_color == 'b' and 
                    not self.ai_thinking and not self.waiting_for_promotion and
                    not self.game_over_message):
                    self.make_ai_move()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if self.game_over_message:
                                # Xử lý click vào nút trong màn hình game over
                                if hasattr(self.gui, 'game_over_play_again_rect') and self.gui.game_over_play_again_rect.collidepoint(mouse_pos):
                                    # Chơi lại
                                    self.restart_game()
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
                                if self.ai_mode:
                                    self.game_over_message = "You surrendered! AI wins!"
                                    self.save_match_result("surrender") # Lưu kết quả
                                else:
                                    winner = "Black" if self.board.current_player == 'white' else "White"
                                    self.game_over_message = f"{self.board.current_player} surrendered! {winner} wins!"
                                continue
                            # (Các nút khác giữ nguyên...)
                            elif button_action == "undo":
                                if self.ai_mode:
                                    self.board.undo_last_move()
                                    self.board.undo_last_move()
                                else: self.board.undo_last_move()
                                self.rebuild_captured_lists()
                                self.update_game_state(None)
                                self.gui.play_move_sound()
                                continue
                            elif button_action == "save":
                                state = self.board.export_state()
                                state['ai_mode'] = self.ai_mode
                                state['white_time'] = self.white_time
                                state['black_time'] = self.black_time
                                if self.ai_mode: state['difficulty'] = self.ai_engine.difficulty
                                try:
                                    with open('savegame.json', 'w') as f: json.dump(state, f, indent=4)
                                    print("Game saved")
                                    self.save_message_timer = 180
                                except Exception as e: print(f"Error saving: {e}")
                                continue
                            elif button_action == "restart":
                                self.restart_game()
                                continue
                            if self.waiting_for_promotion:
                                selected_piece = self.gui.handle_promotion_click(mouse_pos, self.promotion_rects)
                                if selected_piece:
                                    result = self.make_move(self.promotion_move[0], self.promotion_move[1], selected_piece)
                                    self.waiting_for_promotion = False
                                    self.promotion_move = None
                            else:
                                if self.ai_mode and current_player_color == 'b': continue
                                try:
                                    clicked_square = self.gui.get_square_from_pos(mouse_pos)
                                    if clicked_square:
                                        success = self.gui.handle_mouse_down(mouse_pos, self.board.board, current_player_color)
                                        if success: self.valid_moves = self.board.get_valid_moves(self.gui.selected_square)
                                        else: self.valid_moves = []
                                except Exception as e: print(f"Mouse down error: {e}")
                    elif event.type == pygame.MOUSEBUTTONUP:
                        # (Giữ nguyên logic kéo thả)
                        if event.button == 1 and not self.waiting_for_promotion:
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
                            except Exception as e: print(f"Mouse up error: {e}")
                    elif event.type == pygame.MOUSEMOTION:
                        if not self.waiting_for_promotion: self.gui.handle_mouse_motion(mouse_pos)
                
                try:
                    player_color_offline = 'white' if self.ai_mode else None
                    self.gui.draw(
                        board=self.board.board, 
                        mouse_pos=mouse_pos, 
                        current_player=self.board.current_player,
                        ai_mode=self.ai_mode, 
                        move_history=self.board.move_history,
                        valid_moves=self.valid_moves,
                        in_check_square=self.in_check_square,
                        game_over_message=self.game_over_message,
                        ai_thinking=self.ai_thinking,
                        save_message_timer=self.save_message_timer,
                        white_captured=self.white_captured_pieces,
                        black_captured=self.black_captured_pieces,
                        white_time=self.white_time,
                        black_time=self.black_time,
                        player_color=player_color_offline,
                        current_user=self.current_user
                    )
                    if self.waiting_for_promotion:
                        piece = self.board.board[self.promotion_move[0][0]][self.promotion_move[0][1]]
                        self.promotion_rects = self.gui.show_promotion_dialog(piece[0])
                except Exception as e: print(f"Draw error: {e}")
                self.clock.tick(60)
            except Exception as e:
                print(f"Game loop error: {e}")
                continue
        if self.ai_engine: self.ai_engine.stop_engine()
        print("Game loop ended!")