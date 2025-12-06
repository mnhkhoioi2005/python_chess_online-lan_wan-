# 🌐 Hướng Dẫn Chơi Online với Ngrok

## 📋 Mục Lục
1. [Cài Đặt](#cài-đặt)
2. [Cách Chơi - Host Game](#host-game)
3. [Cách Chơi - Join Game](#join-game)
4. [Database và Đăng Nhập](#database-và-đăng-nhập)
5. [Troubleshooting](#troubleshooting)
6. [Giải Thích Kỹ Thuật](#giải-thích-kỹ-thuật)

---

## 🔧 Cài Đặt

### Bước 1: Cài dependencies mới

```bash
pip install -r requirements.txt
```

Hoặc cài thủ công:
```bash
pip install pyperclip requests
```

### Bước 2: Cài đặt Ngrok

#### Windows:
1. Tải Ngrok: https://ngrok.com/download
2. Giải nén file zip
3. Đặt `ngrok.exe` vào thư mục có trong PATH hoặc vào thư mục game
4. Đăng ký tài khoản miễn phí: https://dashboard.ngrok.com/signup
5. Lấy auth token từ dashboard
6. Chạy lệnh:
   ```bash
   ngrok authtoken YOUR_TOKEN_HERE
   ```

#### Kiểm tra cài đặt:
```bash
ngrok --version
```

---

## 🎮 Host Game (Người Tạo Phòng)

### Cách 1: Từ trong game

1. Chạy game: `python main.py`
2. Đăng nhập
3. Click **"🌐 ONLINE (Internet)"**
4. Click **"🎮 Host Game"**
5. Đợi Ngrok khởi động (khoảng 3-5 giây)
6. Màn hình sẽ hiển thị URL như: `0.tcp.ngrok.io:12345`
7. Click nút **"📋 Copy URL"** hoặc chọn URL bằng chuột
8. Gửi URL cho bạn bè qua Zalo/Discord/Messenger
9. Đợi bạn join vào → Game tự động bắt đầu!

### Cách 2: Dùng script tiện ích

```bash
python start_online_server.py
```

Script này sẽ:
- Tự động khởi động server
- Tự động tạo Ngrok tunnel
- Hiển thị URL để gửi cho bạn bè
- Giữ server chạy liên tục

**Sau đó:**
1. Bạn vào game → Chọn "Host Game"
2. Bạn bè dùng URL để join

---

## 🔗 Join Game (Người Vào Phòng)

1. Nhận URL từ host (ví dụ: `0.tcp.ngrok.io:12345`)
2. Chạy game: `python main.py`
3. Đăng nhập
4. Click **"🌐 ONLINE (Internet)"**
5. Click **"🔗 Join Game"**
6. Nhập URL vào ô (hoặc Ctrl+V paste)
7. Click **OK** hoặc nhấn **Enter**
8. Đợi kết nối → Game tự động bắt đầu!

---

## 🎯 Lưu Ý Quan Trọng

### ✅ Ưu điểm Ngrok:
- ✅ Miễn phí
- ✅ Không cần VPS
- ✅ Không cần Port Forwarding
- ✅ Chơi được qua Internet (không cần cùng WiFi)
- ✅ Setup nhanh (2 phút)

### ⚠️ Giới hạn:
- ⚠️ Ngrok miễn phí: 40 requests/phút
- ⚠️ URL thay đổi mỗi lần khởi động lại
- ⚠️ Session timeout sau 2 giờ (phải restart)
- ⚠️ Cần internet ổn định

### 💡 Tips:
- Host nên để game chạy liên tục (không tắt)
- URL chỉ dùng 1 lần (mỗi lần host lại URL khác)
- Nếu mất kết nối, cả 2 phải restart game

---

## 🐛 Troubleshooting

### Lỗi: "Không tìm thấy Ngrok"

**Nguyên nhân:** Ngrok chưa cài hoặc chưa có trong PATH

**Giải pháp:**
```bash
# Kiểm tra Ngrok
ngrok --version

# Nếu lỗi, tải lại từ: https://ngrok.com/download
# Đặt ngrok.exe vào thư mục game hoặc C:\Windows\System32
```

### Lỗi: "Không thể tạo Ngrok tunnel"

**Nguyên nhân:** Chưa đăng ký hoặc chưa auth

**Giải pháp:**
```bash
# 1. Đăng ký tại: https://dashboard.ngrok.com/signup
# 2. Lấy auth token
# 3. Chạy:
ngrok authtoken YOUR_TOKEN
```

### Lỗi: "Kết nối thất bại" khi Join

**Nguyên nhân:** 
- URL sai
- Host đã tắt game
- Ngrok tunnel đã timeout

**Giải pháp:**
- Kiểm tra lại URL (copy chính xác)
- Host restart game và gửi URL mới
- Thử lại sau vài giây

### Lỗi: "Timeout chờ game start"

**Nguyên nhân:** Server không phản hồi

**Giải pháp:**
- Kiểm tra internet
- Restart cả host và guest
- Thử lại với URL mới

---

## 🔬 Giải Thích Kỹ Thuật

### Kiến trúc hệ thống:

```
┌─────────────────┐                           ┌─────────────────┐
│   YOUR PC       │                           │   FRIEND'S PC   │
│                 │                           │                 │
│  Lobby Server   │                           │   Game Client   │
│  (localhost)    │                           │                 │
└────────┬────────┘                           └────────┬────────┘
         │                                             │
         ↓                                             ↓
    Ngrok Client                                       │
         │                                             │
         └──────────────────┬──────────────────────────┘
                           ↓
                   ┌──────────────────┐
                   │  NGROK SERVER    │
                   │  (Cloud)         │
                   │                  │
                   │  Public URL:     │
                   │  0.tcp.ngrok.io  │
                   └──────────────────┘
```

### Cách hoạt động:

1. **Host khởi động:**
   - `LobbyServer` chạy trên `localhost:12347`
   - `NgrokHelper` tạo tunnel → Public URL
   - Host client kết nối đến localhost

2. **Guest join:**
   - Nhập URL public từ host
   - `OnlineClient` kết nối qua Ngrok
   - Ngrok forward traffic về localhost của host

3. **Game play:**
   - Mọi move được gửi qua `OnlineClient`
   - Server forward giữa 2 players
   - Real-time communication qua socket

### Xử lý đa luồng:

- **Server Thread:** Chạy `SimpleLobbyServer` 
- **Ngrok Thread:** Tự động trong background
- **Receive Thread:** Nhận messages từ server
- **Main Thread:** UI và game logic

### Thread-safe:

- Sử dụng `threading.Lock()` cho shared data
- Message queue để tránh race condition
- Proper cleanup khi disconnect

---

## 📚 Files Liên Quan

| File | Chức năng |
|------|-----------|
| `game/ngrok_helper.py` | Quản lý Ngrok tunnel |
| `game/lobby_server.py` | Server trung tâm |
| `game/online_client.py` | Client kết nối |
| `game/online_menu.py` | UI menu online |
| `game/input_dialog.py` | Dialog nhập URL |
| `game/host_waiting_screen.py` | Màn hình chờ của host |
| `start_online_server.py` | Script tiện ích |

---

## 🎓 Trình Bày Cho Thầy

### Điểm nổi bật:

1. **Tunneling & NAT Traversal:**
   - Giải quyết vấn đề IP private
   - Không cần VPS hay Port Forwarding
   - Ngrok là Reverse Proxy thực tế

2. **Xử lý đa luồng:**
   - Mỗi client 1 thread riêng
   - Thread-safe với Lock
   - Non-blocking I/O

3. **UI/UX:**
   - Dialog nhập URL trong Pygame
   - Copy/Paste URL
   - Real-time feedback

4. **Production-ready:**
   - Error handling
   - Timeout handling
   - Reconnection logic
   - Cleanup resources

### So sánh với LAN:

| Tính năng | LAN | Online (Ngrok) |
|-----------|-----|----------------|
| Phạm vi | Cùng WiFi | Toàn cầu |
| Setup | Dễ | Cực dễ |
| IP Discovery | Broadcast | Public URL |
| NAT/Firewall | Vấn đề | Giải quyết |
| Chi phí | Free | Free |

---

## 🗄️ Database và Đăng Nhập

### Database Architecture

**QUAN TRỌNG:** Mỗi máy có **database riêng**, không đồng bộ với nhau!

```
┌─────────────────┐          ┌─────────────────┐
│   MÁY HOST      │          │   MÁY GUEST     │
├─────────────────┤          ├─────────────────┤
│ Database riêng  │  ❌ NO   │ Database riêng  │
│ - Alice         │   SYNC   │ - Bob           │
│ - ELO: 1500     │   ←→     │ - ELO: 1480     │
│ - Wins: 10      │          │ - Wins: 8       │
└─────────────────┘          └─────────────────┘
```

### Cách Hoạt Động

1. **Login**: Mỗi người đăng nhập vào database **local** của mình
2. **Online Play**: Chỉ có board state và moves được gửi qua mạng
3. **Save Results**: Khi game kết thúc, mỗi người lưu kết quả vào database **riêng của mình**

### Ví Dụ Cụ Thể

**Trước game:**
- Host (Alice): ELO 1500, 10 wins
- Guest (Bob): ELO 1480, 8 wins

**Sau game (Alice thắng):**

Trên máy HOST:
```sql
-- Alice's database
INSERT INTO matches (user_id, opponent, result) VALUES (1, 'Online Player', 'win');
UPDATE users SET elo = elo + 25, wins = wins + 1 WHERE id = 1;
-- Alice giờ: ELO 1525, 11 wins
```

Trên máy GUEST:
```sql
-- Bob's database  
INSERT INTO matches (user_id, opponent, result) VALUES (2, 'Online Player', 'loss');
UPDATE users SET elo = elo - 15 WHERE id = 2;
-- Bob giờ: ELO 1465, 8 wins
```

### Username Trùng Nhau?

**Không vấn đề!** Vì database riêng:
- HOST có user "Alice" (ELO 1500)
- GUEST cũng có user "Alice" (ELO 1600)
- → Đây là 2 người khác nhau!

### Match History

Khi xem lịch sử trận đấu, opponent sẽ hiển thị là **"Online Player"** vì:
- Không biết username thật của đối thủ
- Bảo mật thông tin người chơi
- Đơn giản hóa logic

### Ưu Điểm của Kiến Trúc Này

✅ **Đơn giản**: Không cần setup database server  
✅ **Bảo mật**: Mật khẩu không gửi qua mạng  
✅ **Offline**: Xem stats ngay cả khi không online  
✅ **Scalable**: Không có bottleneck ở server  

### Hạn Chế

❌ **Không có Global Leaderboard**: Không thể so sánh ELO giữa người chơi khác máy  
❌ **Username có thể trùng**: 2 người có thể cùng tên (nhưng database khác nhau)

📖 **Chi tiết đầy đủ**: Xem file `DATABASE_ARCHITECTURE.md`

---

## ❓ FAQ

**Q: Có cần Internet nhanh không?**
A: Không, chỉ cần ổn định. Tốc độ 1-2 Mbps là đủ.

**Q: Có giới hạn số người chơi không?**
A: Hiện tại 1vs1. Có thể mở rộng thêm.

**Q: Có lưu game online không?**
A: Có! Kết quả tự động lưu vào database local của mỗi người.

**Q: Database có đồng bộ không?**
A: Không. Mỗi máy có database riêng, lưu kết quả độc lập.

**Q: Có chat trong game không?**
A: Đã có infrastructure, dễ dàng thêm.

**Q: Có thể dùng URL cũ không?**
A: Không. Mỗi lần host phải lấy URL mới.

---

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra [Troubleshooting](#troubleshooting)
2. Xem log trong console
3. Restart game và thử lại

---

**Chúc chơi game vui vẻ! 🎮♟️**
