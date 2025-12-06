"""
Bàn cờ vua - ĐÃ NÂNG CẤP (Full tính năng + Fix lỗi ăn Vua)
"""
import json

class Board:
    def __init__(self):
        self.board = self.create_initial_board()
        self.current_player = 'white'
        self.move_history = []
        
        # Cờ Nhập thành
        self.has_moved_white_king = False
        self.has_moved_white_rook_a = False
        self.has_moved_white_rook_h = False
        self.has_moved_black_king = False
        self.has_moved_black_rook_a = False
        self.has_moved_black_rook_h = False

        # Cờ Bắt Tốt qua đường
        self.en_passant_target_square = None 
    
    def create_initial_board(self):
        board = [[None for _ in range(8)] for _ in range(8)]
        pieces = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        for i in range(8):
            board[0][i] = f'b{pieces[i]}'
            board[1][i] = 'bP'
            board[6][i] = 'wP'
            board[7][i] = f'w{pieces[i]}'
        return board
    
    def display(self):
        print("  a b c d e f g h")
        for i in range(8):
            print(f"{8-i} ", end="")
            for j in range(8):
                piece = self.board[i][j]
                print(f"{piece or '.':<2}", end="")
            print(f" {8-i}")
        print("  a b c d e f g h")
    
    def is_valid_pawn_move(self, from_pos, to_pos, color):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        direction = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        
        # Di chuyển thẳng (không được có quân cản)
        if from_col == to_col:
            # Di chuyển 1 ô
            if to_row == from_row + direction:
                if self.board[to_row][to_col]:  # CÓ QUÂN → KHÔNG đi được
                    return False
                return True
            # Di chuyển 2 ô (từ vị trí ban đầu)
            if from_row == start_row and to_row == from_row + 2 * direction:
                # Phải kiểm tra cả 2 ô
                if self.board[from_row + direction][from_col]:  # Ô giữa có quân
                    return False
                if self.board[to_row][to_col]:  # Ô đích có quân
                    return False
                return True
        # Ăn chéo (phải có quân ĐỊCH, không phải quân cùng màu)
        elif abs(from_col - to_col) == 1 and to_row == from_row + direction:
            target = self.board[to_row][to_col]
            # Ăn quân thường - PHẢI là quân địch
            if target:
                # Kiểm tra quân đích phải khác màu
                if target[0] != color:
                    return True
                else:
                    return False  # Cùng màu → không ăn được
            # Ăn en passant
            if (to_row, to_col) == self.en_passant_target_square:
                return True
        return False
    
    def is_valid_rook_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        if from_row != to_row and from_col != to_col:
            return False
        return self.is_path_clear(from_pos, to_pos)
    
    def is_valid_knight_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    
    def is_valid_bishop_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        if abs(from_row - to_row) != abs(from_col - to_col):
            return False
        return self.is_path_clear(from_pos, to_pos)
    
    def is_valid_queen_move(self, from_pos, to_pos):
        return self.is_valid_rook_move(from_pos, to_pos) or self.is_valid_bishop_move(from_pos, to_pos)
    
    def is_valid_king_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        # Di chuyển bình thường: 1 ô theo bất kỳ hướng nào
        if abs(from_row - to_row) <= 1 and abs(from_col - to_col) <= 1:
            return True
        # Di chuyển 2 ô KHÔNG được phép ở đây - sẽ được kiểm tra riêng trong nhập thành
        return False
    
    def is_path_clear(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        current_row, current_col = from_row + row_step, from_col + col_step
        while (current_row, current_col) != (to_row, to_col):
            if self.board[current_row][current_col]:
                return False
            current_row += row_step
            current_col += col_step
        return True
    
    def is_valid_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        
        if not piece:
            return False
        
        # Không thể ăn quân cùng màu
        if target and piece[0] == target[0]:
            return False
            
        # --- (FIX) KHÔNG ĐƯỢC ĂN VUA ---
        if target and target[1] == 'K':
            return False
        # -------------------------------
        
        if (piece[0] == 'w' and self.current_player != 'white') or \
           (piece[0] == 'b' and self.current_player != 'black'):
            return False
            
        if not self.is_valid_move_basic(from_pos, to_pos):
            return False
        
        # Kiểm tra nhập thành (Vua di chuyển 2 ô)
        if piece[1] == 'K' and abs(from_col - to_col) == 2:
            # Phải kiểm tra xem nhập thành có hợp lệ không
            color = piece[0]
            if to_col > from_col:  # Nhập thành gần (Kingside)
                if not self.can_castle_kingside(color):
                    return False
            else:  # Nhập thành xa (Queenside)
                if not self.can_castle_queenside(color):
                    return False
            return True
            
        if self.would_be_in_check(from_pos, to_pos, piece[0]):
            return False
        return True
    
    def promote_pawn(self, pos, new_piece='Q'):
        row, col = pos
        piece = self.board[row][col]
        if piece and piece[1] == 'P':
            color = piece[0]
            self.board[row][col] = f'{color}{new_piece}'
            return True
        return False
    
    def get_king_square(self, color):
        king = f'{color}K'
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == king:
                    return (row, col)
        return None
    
    def is_square_attacked(self, pos, by_color):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece[0] == by_color:
                    if self.can_attack((row, col), pos):
                        return True
        return False
    
    def can_attack(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        if not piece:
            return False
        piece_type = piece[1]
        if piece_type == 'P':
            direction = -1 if piece[0] == 'w' else 1
            return (to_row == from_row + direction and abs(from_col - to_col) == 1)
        elif piece_type == 'R':
            return self.is_valid_rook_move(from_pos, to_pos)
        elif piece_type == 'N':
            return self.is_valid_knight_move(from_pos, to_pos)
        elif piece_type == 'B':
            return self.is_valid_bishop_move(from_pos, to_pos)
        elif piece_type == 'Q':
            return self.is_valid_queen_move(from_pos, to_pos)
        elif piece_type == 'K':
            return self.is_valid_king_move(from_pos, to_pos)
        return False
    
    def is_in_check(self, color=None):
        if color is None:
            color = 'w' if self.current_player == 'white' else 'b'
        king_pos = self.get_king_square(color)
        if not king_pos:
            return False
        enemy_color = 'b' if color == 'w' else 'w'
        return self.is_square_attacked(king_pos, enemy_color)
    
    def would_be_in_check(self, from_pos, to_pos, color):
        piece = self.board[from_pos[0]][from_pos[1]]
        target = self.board[to_pos[0]][to_pos[1]]
        
        is_en_passant = False
        captured_pawn_pos = None
        if piece[1] == 'P' and (to_pos[0], to_pos[1]) == self.en_passant_target_square and target is None:
            is_en_passant = True
            direction = 1 if piece[0] == 'w' else -1 
            captured_pawn_pos = (to_pos[0] + direction, to_pos[1])
            target = self.board[captured_pawn_pos[0]][captured_pawn_pos[1]]
            
        self.board[to_pos[0]][to_pos[1]] = piece
        self.board[from_pos[0]][from_pos[1]] = None
        if is_en_passant:
            self.board[captured_pawn_pos[0]][captured_pawn_pos[1]] = None

        in_check = self.is_in_check(color)
        
        self.board[from_pos[0]][from_pos[1]] = piece
        self.board[to_pos[0]][to_pos[1]] = None
        if is_en_passant:
            self.board[captured_pawn_pos[0]][captured_pawn_pos[1]] = target
        else:
            self.board[to_pos[0]][to_pos[1]] = target
        
        return in_check
    
    def get_all_valid_moves(self, color):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece[0] == color:
                    piece_moves = self.get_valid_moves((row, col))
                    for move in piece_moves:
                        moves.append(((row, col), move))
        return moves

    def get_valid_moves(self, from_pos):
        moves = []
        from_row, from_col = from_pos
        piece = self.board[from_row][from_col]
        if not piece:
            return []
        color = piece[0]
        for to_row in range(8):
            for to_col in range(8):
                if (from_row, from_col) == (to_row, to_col):
                    continue
                if self.is_valid_move(from_pos, (to_row, to_col)):
                    moves.append((to_row, to_col))
        if piece[1] == 'K':
            if self.can_castle_kingside(color):
                moves.append((from_row, from_col + 2))
            if self.can_castle_queenside(color):
                moves.append((from_row, from_col - 2))
        return moves

    def can_castle_kingside(self, color):
        if self.is_in_check(color):
            return False
        if color == 'w':
            if self.has_moved_white_king or self.has_moved_white_rook_h:
                return False
            row, king_col = 7, 4
            if self.board[row][king_col + 1] or self.board[row][king_col + 2]:
                return False
            if self.is_square_attacked((row, king_col + 1), 'b') or self.is_square_attacked((row, king_col + 2), 'b'):
                return False
        else:
            if self.has_moved_black_king or self.has_moved_black_rook_h:
                return False
            row, king_col = 0, 4
            if self.board[row][king_col + 1] or self.board[row][king_col + 2]:
                return False
            if self.is_square_attacked((row, king_col + 1), 'w') or self.is_square_attacked((row, king_col + 2), 'w'):
                return False
        return True

    def can_castle_queenside(self, color):
        if self.is_in_check(color):
            return False
        if color == 'w':
            if self.has_moved_white_king or self.has_moved_white_rook_a:
                return False
            row, king_col = 7, 4
            if self.board[row][king_col - 1] or self.board[row][king_col - 2] or self.board[row][king_col - 3]:
                return False
            if self.is_square_attacked((row, king_col - 1), 'b') or self.is_square_attacked((row, king_col - 2), 'b'):
                return False
        else:
            if self.has_moved_black_king or self.has_moved_black_rook_a:
                return False
            row, king_col = 0, 4
            if self.board[row][king_col - 1] or self.board[row][king_col - 2] or self.board[row][king_col - 3]:
                return False
            if self.is_square_attacked((row, king_col - 1), 'w') or self.is_square_attacked((row, king_col - 2), 'w'):
                return False
        return True

    def is_valid_move_basic(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        if not piece:
            return False
        if target and piece[0] == target[0]:
            return False
        piece_type = piece[1]
        if piece_type == 'P':
            return self.is_valid_pawn_move(from_pos, to_pos, piece[0])
        elif piece_type == 'R':
            return self.is_valid_rook_move(from_pos, to_pos)
        elif piece_type == 'N':
            return self.is_valid_knight_move(from_pos, to_pos)
        elif piece_type == 'B':
            return self.is_valid_bishop_move(from_pos, to_pos)
        elif piece_type == 'Q':
            return self.is_valid_queen_move(from_pos, to_pos)
        elif piece_type == 'K':
            return self.is_valid_king_move(from_pos, to_pos)
        return False
    
    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
        return len(self.get_all_valid_moves(color)) == 0
    
    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False
        return len(self.get_all_valid_moves(color)) == 0

    def make_move(self, from_pos, to_pos, promotion_piece='Q'):
        old_en_passant_target = self.en_passant_target_square
        self.en_passant_target_square = None
        
        try:
            if self.is_valid_move(from_pos, to_pos):
                piece = self.board[from_pos[0]][from_pos[1]]
                target = self.board[to_pos[0]][to_pos[1]]
                from_row, from_col = from_pos
                to_row, to_col = to_pos
                
                is_castling_move = False
                is_en_passant = False
                
                if piece[1] == 'P' and (to_row, to_col) == old_en_passant_target and target is None:
                    is_en_passant = True
                    direction = -1 if piece[0] == 'w' else 1
                    captured_pawn_pos = (to_row + direction, to_col)
                    target = self.board[captured_pawn_pos[0]][captured_pawn_pos[1]]
                    print(f"En Passant! Capturing {target}")

                elif piece[1] == 'K' and abs(from_col - to_col) == 2:
                    is_castling_move = True
                    if to_col > from_col:
                        rook = self.board[from_row][7]
                        self.board[from_row][5] = rook
                        self.board[from_row][7] = None
                    else:
                        rook = self.board[from_row][0]
                        self.board[from_row][3] = rook
                        self.board[from_row][0] = None
                
                move_data = {
                    'from_pos': from_pos,
                    'to_pos': to_pos,
                    'piece': piece,
                    'captured_piece': target,
                    'player': self.current_player,
                    'is_castling': is_castling_move,
                    'is_en_passant': is_en_passant,
                    'old_en_passant_target': old_en_passant_target,
                    'castling_flags_before_move': self.get_castling_flags()
                }
                self.move_history.append(move_data)
                
                self.board[to_pos[0]][to_pos[1]] = piece
                self.board[from_pos[0]][from_pos[1]] = None
                if is_en_passant:
                    self.board[captured_pawn_pos[0]][captured_pawn_pos[1]] = None
                
                self.update_castling_flags(from_pos, piece)
                
                if piece[1] == 'P' and abs(from_row - to_row) == 2:
                    direction = -1 if piece[0] == 'w' else 1
                    self.en_passant_target_square = (to_row + direction, to_col)
                    print(f"En Passant target set at: {self.en_passant_target_square}")

                if piece[1] == 'P':
                    if (piece[0] == 'w' and to_pos[0] == 0) or (piece[0] == 'b' and to_pos[0] == 7):
                        self.promote_pawn(to_pos, promotion_piece)
                
                self.current_player = 'black' if self.current_player == 'white' else 'white'
                
                current_color = 'w' if self.current_player == 'white' else 'b'
                if self.is_checkmate(current_color):
                    return 'checkmate'
                elif self.is_stalemate(current_color):
                    return 'stalemate'
                
                return True
            else:
                return False
        except Exception as e:
            print(f"Error in make_move: {e}")
            return False
            
    def update_castling_flags(self, from_pos, piece):
        from_row, from_col = from_pos
        if piece == 'wK':
            self.has_moved_white_king = True
        elif piece == 'bK':
            self.has_moved_black_king = True
        elif piece == 'wR':
            if from_row == 7 and from_col == 0:
                self.has_moved_white_rook_a = True
            elif from_row == 7 and from_col == 7:
                self.has_moved_white_rook_h = True
        elif piece == 'bR':
            if from_row == 0 and from_col == 0:
                self.has_moved_black_rook_a = True
            elif from_row == 0 and from_col == 7:
                self.has_moved_black_rook_h = True

    def undo_last_move(self):
        if not self.move_history:
            return False
        
        last_move = self.move_history.pop()
        
        from_pos = last_move['from_pos']
        to_pos = last_move['to_pos']
        moved_piece = last_move['piece']
        captured_piece = last_move['captured_piece']
        is_castling = last_move.get('is_castling', False)
        is_en_passant = last_move.get('is_en_passant', False)
        
        self.en_passant_target_square = last_move.get('old_en_passant_target')
        
        self.board[from_pos[0]][from_pos[1]] = moved_piece
        
        if is_en_passant:
            direction = -1 if moved_piece[0] == 'w' else 1
            captured_pawn_pos = (to_pos[0] + direction, to_pos[1])
            self.board[captured_pawn_pos[0]][captured_pawn_pos[1]] = captured_piece
            self.board[to_pos[0]][to_pos[1]] = None
        else:
            self.board[to_pos[0]][to_pos[1]] = captured_piece
        
        if is_castling:
            if to_pos[1] > from_pos[1]:
                rook = self.board[from_pos[0]][5]
                self.board[from_pos[0]][7] = rook
                self.board[from_pos[0]][5] = None
            else:
                rook = self.board[from_pos[0]][3]
                self.board[from_pos[0]][0] = rook
                self.board[from_pos[0]][3] = None
        
        self.current_player = last_move['player']
        self.restore_castling_flags(last_move.get('castling_flags_before_move'))
        
        return True

    def get_castling_flags(self):
        return {
            'wK': self.has_moved_white_king,
            'wRa': self.has_moved_white_rook_a,
            'wRh': self.has_moved_white_rook_h,
            'bK': self.has_moved_black_king,
            'bRa': self.has_moved_black_rook_a,
            'bRh': self.has_moved_black_rook_h,
        }

    def restore_castling_flags(self, flags):
        if flags:
            self.has_moved_white_king = flags['wK']
            self.has_moved_white_rook_a = flags['wRa']
            self.has_moved_white_rook_h = flags['wRh']
            self.has_moved_black_king = flags['bK']
            self.has_moved_black_rook_a = flags['bRa']
            self.has_moved_black_rook_h = flags['bRh']

    def export_state(self):
        state = {
            'board': self.board,
            'current_player': self.current_player,
            'move_history': self.move_history,
            'castling_flags': self.get_castling_flags(),
            'en_passant_target_square': self.en_passant_target_square
        }
        return state

    def import_state(self, state):
        try:
            self.board = state['board']
            self.current_player = state['current_player']
            self.move_history = state['move_history']
            self.restore_castling_flags(state['castling_flags'])
            self.en_passant_target_square = state['en_passant_target_square']
            print("Game state loaded successfully.")
            return True
        except Exception as e:
            print(f"Error loading game state: {e}")
            return False
    
    def get_fen(self):
        fen_parts = []
        for row in self.board:
            empty_count = 0
            row_str = ""
            for cell in row:
                if cell is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    piece_map = {
                        'wP': 'P', 'wR': 'R', 'wN': 'N', 'wB': 'B', 'wQ': 'Q', 'wK': 'K',
                        'bP': 'p', 'bR': 'r', 'bN': 'n', 'bB': 'b', 'bQ': 'q', 'bK': 'k'
                    }
                    row_str += piece_map.get(cell, cell)
            if empty_count > 0:
                row_str += str(empty_count)
            fen_parts.append(row_str)
        board_fen = "/".join(fen_parts)
        active_color = "w" if self.current_player == 'white' else "b"
        return f"{board_fen} {active_color} KQkq - 0 1"