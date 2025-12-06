"""
Game Logic chính
"""
from .board import Board

class ChessGame:
    def __init__(self):
        self.board = Board()
        self.game_over = False
    
    def start(self):
        """Bắt đầu game"""
        print("=== GAME CỜ VUA ===")
        print("Nhập nước đi theo format: e2 e4")
        print("Nhập 'quit' để thoát\n")
        
        while not self.game_over:
            self.board.display()
            print(f"\nLượt: {self.board.current_player}")
            
            move = input("Nhập nước đi: ").strip().lower()
            
            if move == 'quit':
                break
            
            if self.process_move(move):
                print("Nước đi hợp lệ!")
            else:
                print("Nước đi không hợp lệ!")
    
    def process_move(self, move_str):
        """Xử lý input nước đi"""
        try:
            parts = move_str.split()
            if len(parts) != 2:
                return False
            
            from_pos = self.parse_position(parts[0])
            to_pos = self.parse_position(parts[1])
            
            return self.board.make_move(from_pos, to_pos)
        except:
            return False
    
    def parse_position(self, pos_str):
        """Chuyển đổi a1 -> (7,0)"""
        col = ord(pos_str[0]) - ord('a')
        row = 8 - int(pos_str[1])
        return (row, col)
