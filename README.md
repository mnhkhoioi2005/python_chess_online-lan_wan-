# Game Cờ Vua Python

Game cờ vua với giao diện đồ họa pygame, có thể kéo thả quân cờ.

## ✨ Tính Năng

- 🎮 **VS Player**: Chơi 2 người trên 1 máy
- 🤖 **VS AI**: 3 độ khó (Easy, Medium, Hard)
- 🏠 **LAN Multiplayer**: Chơi trong mạng nội bộ
- 🌐 **Online**: Chơi qua Internet với Ngrok
- 💾 **Save/Load Game**: Lưu và tải lại trận đấu
- 👤 **User System**: Đăng nhập, ELO rating
- 📊 **Admin Panel**: Quản lý users
- 🎨 **UI đẹp**: Giao diện hiện đại với Pygame

## 🚀 Cài Đặt

```bash
# Clone repo
git clone <repo-url>
cd python_chess-main

# Cài dependencies
pip install -r requirements.txt

# Chạy game
python main.py
```

## 🌐 Chơi Online (MỚI!)

### Quick Start:
1. Cài Ngrok: https://ngrok.com/download
2. Chạy: `ngrok authtoken YOUR_TOKEN`
3. Host: `python main.py` → Chọn "🌐 ONLINE" → "Host Game"
4. Copy URL gửi bạn
5. Guest: Paste URL và chơi!

📖 **Chi tiết:** Xem [QUICK_START.md](QUICK_START.md)

📚 **Hướng dẫn đầy đủ:** Xem [ONLINE_GUIDE.md](ONLINE_GUIDE.md)

## 🎯 Hướng Dẫn Sử Dụng

### Chạy game:
```bash
python main.py
```

### Các chế độ chơi:
- **VS Player**: Chơi 2 người offline
- **VS AI**: Chọn độ khó (Easy/Medium/Hard)
- **LAN**: Chơi trong mạng WiFi
- **Online**: Chơi qua Internet (Ngrok)
- **Load Game**: Tải lại game đã lưu

## 📁 Cấu Trúc Project

```
├── main.py                 # Entry point
├── start_online_server.py  # Script khởi động server online
├── game/
│   ├── board.py           # Logic bàn cờ
│   ├── chess_gui_game.py  # Game UI
│   ├── database.py        # SQL Server DB
│   ├── menu.py            # Main menu
│   ├── online_menu.py     # Online menu (MỚI)
│   ├── lobby_server.py    # Server online (MỚI)
│   ├── online_client.py   # Client online (MỚI)
│   ├── ngrok_helper.py    # Ngrok integration (MỚI)
│   └── ...
├── assets/                # Fonts, images, sounds
└── stockfish/             # AI engine source
```

## 🔧 Requirements

- Python 3.7+
- pygame
- pyperclip (cho online)
- requests (cho online)
- pyodbc (SQL Server)
- ngrok (cho online - tải riêng)

## 🎓 Tính Năng Kỹ Thuật

### Xử Lý Đa Luồng:
- Server: Mỗi client 1 thread riêng
- Client: Thread nhận data riêng biệt
- Thread-safe với `threading.Lock()`

### Online Architecture:
```
Host PC → Lobby Server (localhost)
           ↓
       Ngrok Tunnel
           ↓
    Public URL (Internet)
           ↓
       Guest PC
```

### Database:
- SQL Server với pyodbc
- User authentication
- ELO rating system
- Match history

## 📝 License

MIT License

## 👨‍💻 Author

Chess Game Project - HK7

