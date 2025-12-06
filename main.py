"""
Game Cờ Vua - Main Entry Point
"""
import pygame
import sys
import os
import json
from game.database import Database 
from game.login_menu import LoginMenu 
from game.menu import MainMenu
from game.chess_gui_game import ChessGUIGame
from game.online_game import OnlineChessGame
from game.lan_menu_integrated import LANMenu
from game.ip_dialog import IPDialog
from game.admin_panel import AdminPanel
from game.online_menu import OnlineMenu

def main():
    # Fix UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        try:
            # Try to set UTF-8 encoding for console
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass
    
    # 1. Khởi động Pygame & Mixer (Âm thanh)
    # Đặt buffer nhỏ để âm thanh không bị trễ
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.init()
    
    # 2. Tạo màn hình 1 lần duy nhất (Các file khác sẽ dùng lại màn hình này)
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Chess Game")
    
    # 3. Kết nối Database (1 lần duy nhất)
    print("Connecting to database...")
    try:
        db = Database()
    except Exception as e:
        print(f"Database connection error: {e}")
        return
    
    # --- VÒNG LẶP ỨNG DỤNG (Application Loop) ---
    while True:
        # Xóa sự kiện cũ
        pygame.event.clear()
        
        # --- BƯỚC 1: MÀN HÌNH ĐĂNG NHẬP ---
        login_menu = LoginMenu(db)
        current_user = login_menu.run() 
        
        if current_user is None: 
            print("Thoát game từ màn hình đăng nhập.")
            pygame.quit()
            sys.exit()
            
        print(f"Đăng nhập thành công: {current_user['username']}")
        
        # --- BƯỚC 2: VÒNG LẶP PHIÊN LÀM VIỆC (Session Loop) ---
        current_state = "main_menu" 
        
        while current_state != "exit" and current_state != "logout":
            try:
                # --- MENU CHÍNH ---
                if current_state == "main_menu":
                    menu = MainMenu(current_user=current_user, db=db) 
                    mode = menu.run()
                    
                    # Điều hướng dựa trên lựa chọn từ Menu
                    if mode == "logout": 
                        current_state = "logout"
                    elif mode == "vs_player":
                        current_state = "vs_player"
                    elif mode in ("vs_ai_easy", "vs_ai_medium", "vs_ai_hard"):
                        current_state = mode 
                    elif mode == "lan_multiplayer":
                        current_state = "lan_multiplayer"
                    elif mode == "online_multiplayer":
                        current_state = "online_multiplayer"
                    elif mode == "load_game":
                        current_state = "load_game"
                    elif mode == "admin_panel":
                        current_state = "admin_panel"
                    else:
                        current_state = "exit"

                # --- ADMIN PANEL ---
                elif current_state == "admin_panel":
                    admin_panel = AdminPanel(db)
                    result = admin_panel.run()
                    current_state = "main_menu" # Quay lại menu khi xong

                # --- CHƠI VS NGƯỜI (OFFLINE) ---
                elif current_state == "vs_player":
                    # Truyền db để lưu kết quả trận đấu
                    game = ChessGUIGame(ai_mode=False, current_user=current_user, db=db)
                    game.run()
                    current_state = "main_menu"

                # --- CHƠI VS AI ---
                elif current_state in ("vs_ai_easy", "vs_ai_medium", "vs_ai_hard"):
                    # Lấy độ khó từ tên state (ví dụ: "easy" từ "vs_ai_easy")
                    difficulty = current_state.split('_')[-1]
                    game = ChessGUIGame(ai_mode=True, difficulty=difficulty, current_user=current_user, db=db) 
                    game.run()
                    current_state = "main_menu"

                # --- TẢI GAME CŨ ---
                elif current_state == "load_game":
                    save_file = 'savegame.json'
                    if os.path.exists(save_file):
                        with open(save_file, 'r') as f:
                            state = json.load(f)
                        # Khôi phục cài đặt
                        ai_mode_loaded = state.get('ai_mode', False) 
                        difficulty_loaded = state.get('difficulty', "medium")
                        
                        game = ChessGUIGame(ai_mode=ai_mode_loaded, difficulty=difficulty_loaded, current_user=current_user, db=db)
                        
                        # Khôi phục bàn cờ
                        game.board.import_state(state)
                        game.update_game_state(None) # Cập nhật lại trạng thái chiếu/hết cờ
                        game.run()
                        current_state = "main_menu"
                    else:
                        print("Không tìm thấy file save.")
                        current_state = "main_menu"

                # --- CHƠI LAN (ONLINE) ---
                elif current_state == "lan_multiplayer":
                    # LanMenu tự vẽ giao diện của nó
                    lan_menu = LANMenu(1280, 720)
                    result = lan_menu.run()
                    current_state = "main_menu"

                # --- CHƠI ONLINE (NGROK) ---
                elif current_state == "online_multiplayer":
                    online_menu = OnlineMenu(current_user)
                    result = online_menu.run()
                    
                    if result:
                        # result chứa client connection và info
                        mode = result.get('mode')
                        client = result.get('client')
                        
                        if mode == 'online_host':
                            # Host: chơi với quân trắng
                            print("Starting game as Host (White)")
                            online_game = OnlineChessGame(
                                server_ip='localhost',
                                is_host=True,
                                current_user=current_user,
                                db=db,
                                client=client
                            )
                            online_game.run()
                            
                            # Cleanup
                            ngrok = result.get('ngrok')
                            server = result.get('server')
                            if ngrok:
                                ngrok.stop_tunnel()
                            if server:
                                server.stop()
                                
                        elif mode == 'online_guest':
                            # Guest: choi voi quan den
                            print("Starting game as Guest (Black)")
                            online_game = OnlineChessGame(
                                server_ip='',  # không cần IP
                                is_host=False,
                                current_user=current_user,
                                db=db,
                                client=client
                            )
                            online_game.run()
                    
                    current_state = "main_menu"

            except Exception as e:
                print(f"Error in game loop: {e}")
                import traceback
                traceback.print_exc()
                current_state = "exit"

        # --- XỬ LÝ THOÁT / ĐĂNG XUẤT ---
        if current_state == "exit":
            print("Exiting game...")
            pygame.quit()
            sys.exit()
        elif current_state == "logout":
            print("Đăng xuất... Quay lại màn hình đăng nhập.")
            continue # Quay lại vòng lặp while True đầu tiên

if __name__ == "__main__":
    main()