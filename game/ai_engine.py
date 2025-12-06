import chess
import chess.engine
import subprocess
import os
import platform
import sys

class AIEngine:
    def __init__(self, difficulty="medium"):
        self.engine = None
        self.difficulty = difficulty
        self.board = chess.Board() # (MỚI) Giữ trạng thái bàn cờ riêng để đồng bộ
        
    def start_engine(self):
        try:
            print("Starting Stockfish engine...")
            
            if sys.platform.startswith('win'):
                paths = [
                    "stockfish.exe",
                    r"C:\stockfish\stockfish.exe",
                    # Tìm trong thư mục dự án
                    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stockfish", "stockfish.exe"),
                    # Thêm các tên file phổ biến khác
                    "stockfish_15_x64_avx2.exe",
                    "stockfish-windows-x86-64-avx2.exe"
                ]
            else:
                paths = ["/usr/games/stockfish", "/usr/bin/stockfish", "stockfish"]
            
            # Tìm file exe trong thư mục stockfish của dự án (ưu tiên)
            project_stockfish = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stockfish")
            if os.path.exists(project_stockfish):
                for file in os.listdir(project_stockfish):
                    if "stockfish" in file.lower() and file.endswith(".exe"):
                        paths.insert(0, os.path.join(project_stockfish, file))

            for path in paths:
                try:
                    print(f"Trying to load engine from: {path}")
                    if os.path.exists(path) or shutil.which(path): # Kiểm tra file tồn tại
                        self.engine = chess.engine.SimpleEngine.popen_uci(path)
                        print(f"✅ Stockfish started successfully! ({path})")
                        
                        # Cài đặt độ khó
                        difficulty_map = {"easy": 1, "medium": 5, "hard": 20} # (SỬA) Giảm skill level xuống chút cho mượt
                        skill_level = difficulty_map.get(self.difficulty, 5)
                        self.engine.configure({"Skill Level": skill_level})
                        print(f"AI Skill Level set to: {skill_level}")
                        return True
                except Exception as e:
                    print(f"Failed to load {path}: {e}")
                    continue
            
            print("❌ Could not start Stockfish engine. Please check 'stockfish' folder.")
            return False
            
        except Exception as e:
            print(f"Critical error starting Stockfish: {e}")
            return False
    
    def stop_engine(self):
        if self.engine:
            try:
                self.engine.quit()
            except:
                pass
    
    def get_best_move(self, fen_position):
        if not self.engine:
            print("Engine not running!")
            return None
        
        try:
            # Cập nhật bàn cờ nội bộ
            self.board.set_fen(fen_position)
            
            # Cài đặt thời gian suy nghĩ
            time_map = {"easy": 0.1, "medium": 0.5, "hard": 1.0}
            time_limit = time_map.get(self.difficulty, 0.5)
            
            # (QUAN TRỌNG) Kiểm tra game over trước khi hỏi AI
            if self.board.is_game_over():
                print("Game over detected by AI engine.")
                return None

            # Yêu cầu AI đi
            result = self.engine.play(self.board, chess.engine.Limit(time=time_limit))
            
            if result.move:
                return str(result.move)
            else:
                print("AI returned no move (Resign or Error)")
                return None

        except Exception as e:
            print(f"AI calculation error: {e}")
            # Thử khởi động lại engine nếu bị crash
            self.stop_engine()
            self.start_engine()
            return None
    
    def convert_move_to_coords(self, move_str):
        """Chuyển đổi move string (e2e4) thành tọa độ"""
        if not move_str or len(move_str) < 4:
            return None, None
        
        try:
            from_square = move_str[:2]
            to_square = move_str[2:4]
            
            def square_to_coords(square):
                col = ord(square[0]) - ord('a')
                row = 8 - int(square[1])
                return (row, col)
            
            from_pos = square_to_coords(from_square)
            to_pos = square_to_coords(to_square)
            
            return from_pos, to_pos
        except Exception as e:
            print(f"Move conversion error: {e}")
            return None, None
import shutil # Thêm import này ở đầu file nếu chưa có