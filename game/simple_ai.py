import random

class SimpleAI:
    def __init__(self):
        pass
    
    def get_all_possible_moves(self, board, color):
        """Lấy tất cả nước đi có thể của một màu"""
        moves = []
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece and piece[0] == color:
                    # Kiểm tra tất cả ô có thể đi đến
                    for to_row in range(8):
                        for to_col in range(8):
                            if (row, col) != (to_row, to_col):
                                moves.append(((row, col), (to_row, to_col)))
        return moves
    
    def get_best_move(self, board, current_player):
        """Trả về nước đi tốt nhất (random trong demo này)"""
        color = 'b' if current_player == 'black' else 'w'
        possible_moves = self.get_all_possible_moves(board, color)
        
        if possible_moves:
            # Chọn random một nước đi (có thể cải thiện logic sau)
            return random.choice(possible_moves)
        
        return None
