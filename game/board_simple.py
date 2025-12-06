"""
Bàn cờ vua đơn giản với các tính năng cơ bản
"""

class Board:
    def __init__(self):
        self.board = self.create_initial_board()
        self.current_player = 'white'
    
    def create_initial_board(self):
        """Tạo bàn cờ ban đầu"""
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Quân đen (hàng 0,1)
        pieces = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        for i in range(8):
            board[0][i] = f'b{pieces[i]}'  # Hàng 8
            board[1][i] = 'bP'  # Tốt đen hàng 7
            board[6][i] = 'wP'  # Tốt trắng hàng 2
            board[7][i] = f'w{pieces[i]}'  # Hàng 1
        
        return board
    
    def display(self):
        """Hiển thị bàn cờ"""
        print("  a b c d e f g h")
        for i in range(8):
            print(f"{8-i} ", end="")
            for j in range(8):
                piece = self.board[i][j]
                print(f"{piece or '.':<2}", end="")
            print(f" {8-i}")
        print("  a b c d e f g h")
    
    def is_valid_pawn_move(self, from_pos, to_pos, color):
        """Kiểm tra nước đi tốt"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Trắng đi lên (giảm row), đen đi xuống (tăng row)
        direction = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        
        # Di chuyển thẳng
        if from_col == to_col:
            # Di chuyển 1 ô
            if to_row == from_row + direction and not self.board[to_row][to_col]:
                return True
            # Di chuyển 2 ô từ vị trí ban đầu
            if from_row == start_row and to_row == from_row + 2 * direction and not self.board[to_row][to_col]:
                return True
        
        # Ăn chéo
        elif abs(from_col - to_col) == 1 and to_row == from_row + direction:
            if self.board[to_row][to_col]:  # Có quân để ăn
                return True
        
        return False
    
    def is_valid_rook_move(self, from_pos, to_pos):
        """Kiểm tra nước đi xe"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        if from_row != to_row and from_col != to_col:
            return False
        
        return self.is_path_clear(from_pos, to_pos)
    
    def is_valid_knight_move(self, from_pos, to_pos):
        """Kiểm tra nước đi mã"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)
        
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    
    def is_valid_bishop_move(self, from_pos, to_pos):
        """Kiểm tra nước đi tượng"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        if abs(from_row - to_row) != abs(from_col - to_col):
            return False
        
        return self.is_path_clear(from_pos, to_pos)
    
    def is_valid_queen_move(self, from_pos, to_pos):
        """Kiểm tra nước đi hậu"""
        return self.is_valid_rook_move(from_pos, to_pos) or self.is_valid_bishop_move(from_pos, to_pos)
    
    def is_valid_king_move(self, from_pos, to_pos):
        """Kiểm tra nước đi vua"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        return abs(from_row - to_row) <= 1 and abs(from_col - to_col) <= 1
    
    def is_path_clear(self, from_pos, to_pos):
        """Kiểm tra đường đi có bị cản không"""
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
        """Kiểm tra nước đi hợp lệ"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        
        if not piece:
            return False
        
        # Không thể ăn quân cùng màu
        if target and piece[0] == target[0]:
            return False
        
        # Kiểm tra lượt đi
        if (piece[0] == 'w' and self.current_player != 'white') or \
           (piece[0] == 'b' and self.current_player != 'black'):
            return False
        
        # Logic di chuyển cơ bản cho từng quân
        piece_type = piece[1]
        
        if piece_type == 'P':  # Tốt
            return self.is_valid_pawn_move(from_pos, to_pos, piece[0])
        elif piece_type == 'R':  # Xe
            return self.is_valid_rook_move(from_pos, to_pos)
        elif piece_type == 'N':  # Mã
            return self.is_valid_knight_move(from_pos, to_pos)
        elif piece_type == 'B':  # Tượng
            return self.is_valid_bishop_move(from_pos, to_pos)
        elif piece_type == 'Q':  # Hậu
            return self.is_valid_queen_move(from_pos, to_pos)
        elif piece_type == 'K':  # Vua
            return self.is_valid_king_move(from_pos, to_pos)
        
        return False
    
    def promote_pawn(self, pos, new_piece='Q'):
        """Phong cấp tốt"""
        row, col = pos
        piece = self.board[row][col]
        if piece and piece[1] == 'P':
            color = piece[0]
            self.board[row][col] = f'{color}{new_piece}'
            return True
        return False
    
    def make_move(self, from_pos, to_pos, promotion_piece='Q'):
        """Thực hiện nước đi"""
        try:
            if self.is_valid_move(from_pos, to_pos):
                piece = self.board[from_pos[0]][from_pos[1]]
                target = self.board[to_pos[0]][to_pos[1]]
                
                # Debug info
                from_square = f"{chr(ord('a') + from_pos[1])}{8 - from_pos[0]}"
                to_square = f"{chr(ord('a') + to_pos[1])}{8 - to_pos[0]}"
                print(f"Move {piece} from {from_square} to {to_square}")
                if target:
                    print(f"Capture {target}")
                
                # Thực hiện nước đi
                self.board[to_pos[0]][to_pos[1]] = piece
                self.board[from_pos[0]][from_pos[1]] = None
                
                # Kiểm tra phong cấp tốt
                if piece[1] == 'P':
                    if (piece[0] == 'w' and to_pos[0] == 0) or (piece[0] == 'b' and to_pos[0] == 7):
                        self.promote_pawn(to_pos, promotion_piece)
                        print(f"Pawn promoted to {promotion_piece}")
                
                # Đổi lượt
                self.current_player = 'black' if self.current_player == 'white' else 'white'
                print(f"Next turn: {self.current_player}")
                return True
            else:
                return False
        except Exception as e:
            print(f"Error in make_move: {e}")
            return False
