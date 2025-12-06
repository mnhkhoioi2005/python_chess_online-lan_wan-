# 🗄️ Kiến Trúc Database cho Online Play

## Tổng Quan

Khi chơi **Online (Internet)**, mỗi người chơi có **DATABASE RIÊNG** trên máy của họ. Không có database chung, không có đồng bộ hóa.

```
┌─────────────────────────────┐        ┌─────────────────────────────┐
│      MÁY HOST               │        │      MÁY GUEST              │
│  (Người tạo phòng)          │        │  (Người vào phòng)          │
├─────────────────────────────┤        ├─────────────────────────────┤
│                             │        │                             │
│  📦 SQL Server DATABASE     │        │  📦 SQL Server DATABASE     │
│     - Users table           │        │     - Users table           │
│       ├─ host_username      │        │       ├─ guest_username     │
│       ├─ ELO: 1500          │        │       ├─ ELO: 1480          │
│       └─ Wins: 10           │        │       └─ Wins: 8            │
│                             │        │                             │
│     - Matches table         │        │     - Matches table         │
│       └─ History của host   │        │       └─ History của guest  │
│                             │        │                             │
└──────────────┬──────────────┘        └──────────────┬──────────────┘
               │                                      │
               │         🌐 INTERNET CONNECTION       │
               │      (Ngrok tunnel on port 12347)   │
               └──────────────────────────────────────┘
```

---

## ❓ Câu Hỏi Thường Gặp

### Q1: Database có đồng bộ giữa 2 máy không?
**Không!** Mỗi máy có database riêng, hoàn toàn độc lập.

### Q2: Nếu host có username "Alice" và guest cũng có username "Alice" thì sao?
**Không sao!** Vì 2 database hoàn toàn khác nhau:
- Host's database: `Alice` với ELO 1500, 10 wins
- Guest's database: `Alice` với ELO 1600, 15 wins

Đây là 2 người khác nhau, chỉ tình cờ cùng tên.

### Q3: Kết quả trận đấu được lưu như thế nào?
Khi game kết thúc, **mỗi người chơi lưu vào database của mình**:

**Host (Alice) thắng:**
```sql
-- Trên máy HOST
INSERT INTO matches (user_id, opponent, result) VALUES (1, 'Online Player', 'win');
UPDATE users SET elo = elo + 25, wins = wins + 1 WHERE id = 1;

-- Trên máy GUEST
INSERT INTO matches (user_id, opponent, result) VALUES (2, 'Online Player', 'loss');
UPDATE users SET elo = elo - 15 WHERE id = 2;
```

### Q4: Tại sao không dùng 1 database chung trên server?
Vì:
1. **Không cần phức tạp**: Game này là peer-to-peer (P2P) với Ngrok, không có dedicated server
2. **Bảo mật**: Mỗi người giữ data riêng, không cần chia sẻ với người lạ
3. **Offline support**: Có thể xem lịch sử của mình ngay cả khi không online
4. **Dễ deploy**: Không cần setup MySQL/PostgreSQL trên VPS

---

## 🔧 Chi Tiết Kỹ Thuật

### 1. Khởi Tạo Database

Khi `main.py` chạy:
```python
from game.database import Database

db = Database()  # Tạo hoặc connect tới chess_game.db (SQLite local)
```

Mỗi máy tự động tạo file `chess_game.db` riêng.

---

### 2. Login và User Data

Khi người chơi login:
```python
success, current_user = db.login_user(username, password)

# current_user = {
#     "id": 1,
#     "username": "Alice",
#     "elo": 1500,
#     "matches": 25,
#     "wins": 10,
#     ...
# }
```

**Quan trọng**: `current_user` là dictionary chứa thông tin từ **database local** của máy đó.

---

### 3. Lưu Kết Quả Trận Online

File `game/online_game.py`:
```python
class OnlineChessGame:
    def __init__(self, ..., current_user, db, ...):
        self.current_user = current_user  # Dict với user info
        self.db = db                      # Database instance (local)
        
    def save_match_result(self, winner_color, result_type):
        user_id = self.current_user.get('id')
        
        # Xác định kết quả từ góc nhìn người chơi này
        if winner_color == self.my_color_full:
            result = 'win'
            elo_change = +25
            won = True
        else:
            result = 'loss'
            elo_change = -15
            won = False
        
        # Lưu vào database LOCAL
        self.db.save_match_result(user_id, "Online Player", result)
        self.db.update_stats(user_id, won, elo_change)
```

**Khi game kết thúc:**
1. Host gọi `save_match_result()` → lưu vào database của host
2. Guest gọi `save_match_result()` → lưu vào database của guest
3. 2 lần gọi này **độc lập**, không ảnh hưởng nhau

---

### 4. Opponent Name trong History

Khi xem lịch sử trận đấu:
```python
matches = db.get_user_history(user_id)

# Kết quả:
# [
#   ('Online Player', 'win',  '2024-01-15 14:30'),
#   ('Online Player', 'loss', '2024-01-15 13:00'),
#   ('Bob',           'win',  '2024-01-14 10:00'),  # LAN game
# ]
```

Tất cả trận online đều hiển thị opponent là `"Online Player"` vì:
- Không biết username thật của đối thủ (database riêng)
- Đơn giản hóa logic (không cần sync username)

---

## 🎯 Ưu Điểm của Kiến Trúc Này

### ✅ Đơn Giản
- Không cần setup database server (MySQL, PostgreSQL)
- Không cần viết API backend
- Mỗi máy tự quản lý data của mình

### ✅ Bảo Mật
- Mật khẩu không được gửi qua mạng
- User data không lưu trên server của người khác

### ✅ Offline-First
- Có thể xem stats và history ngay cả khi không online
- Database vẫn hoạt động khi chơi với AI hoặc LAN

### ✅ Scalable
- Không có bottleneck ở database server
- Mỗi match chỉ cần 2 máy connect với nhau (P2P)

---

## ⚠️ Hạn Chế

### ❌ Không có Leaderboard Toàn Cầu
**Vấn đề**: Không thể so sánh ELO giữa người chơi khác máy

**Giải pháp tương lai**: 
- Có thể thêm backend API (Flask/FastAPI) để:
  - Gửi match results lên server
  - Tạo leaderboard toàn cầu
  - Xác thực người chơi

### ❌ Username Có Thể Trùng
**Vấn đề**: 2 người có thể cùng tên "Alice" trên 2 máy khác nhau

**Giải pháp hiện tại**: 
- Chấp nhận (vì database riêng)
- Trong game hiển thị "Online Player" thay vì username thật

---

## 📊 So Sánh với LAN Mode

| Feature              | LAN Mode              | Online Mode             |
|----------------------|-----------------------|-------------------------|
| **Network**          | Same WiFi             | Internet (Ngrok)        |
| **Database**         | Local SQLite          | Local SQLite            |
| **Username Sync**    | Không (cũng local)    | Không (cũng local)      |
| **ELO Update**       | Mỗi máy tự update     | Mỗi máy tự update       |
| **Opponent Display** | Username của đối thủ? | "Online Player"         |

**Kết luận**: Database architecture giống nhau! Chỉ khác network layer.

---

## 🚀 Hướng Mở Rộng (Future Work)

### Option 1: Thêm Backend API
```
1. Deploy Flask/FastAPI server trên VPS
2. Mỗi máy gửi match results lên server:
   POST /api/matches
   {
     "username": "Alice",
     "opponent": "Bob",
     "result": "win",
     "timestamp": "2024-01-15T14:30:00Z"
   }
3. Server tạo global leaderboard
```

### Option 2: Blockchain (Overkill nhưng cool)
```
1. Lưu match results lên blockchain (Ethereum, Polygon)
2. Smart contract verify kết quả
3. Leaderboard on-chain
```

### Option 3: Firebase Realtime Database
```
1. Thay SQLite bằng Firebase
2. Auto-sync giữa devices
3. Có built-in authentication
```

---

## 📝 Tóm Tắt

```
QUAN TRỌNG NHẤT:

📌 Mỗi máy = 1 database riêng
📌 Kết quả trận đấu lưu LOCAL (không gửi đi đâu)
📌 ELO update LOCAL (mỗi người tự tính)
📌 Không có sync, không có server chung
```

**Đây là kiến trúc "decentralized" (phi tập trung) - đơn giản nhưng đủ dùng cho project học đường!**

---

## 💡 Giải Thích cho Thầy

> "Em implement theo kiến trúc peer-to-peer (P2P) với local database trên mỗi client. Khi 2 người chơi online, chỉ có dữ liệu game state (board state, moves) được gửi qua mạng thông qua Ngrok tunnel. Còn user data và match history được lưu độc lập trên mỗi máy. Điều này đảm bảo privacy và giảm dependency vào central server, phù hợp với scope của project."

---

**File:** `DATABASE_ARCHITECTURE.md`  
**Last Updated:** 2024  
**Author:** GitHub Copilot (Claude Sonnet 4.5)
