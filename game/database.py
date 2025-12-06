import pyodbc
import hashlib
from datetime import datetime

# Cấu hình SQL Server
SQL_SERVER_CONFIG = {
    "server": "DESKTOP-VA8HIUM",
    "database": "ChessDB",
    "use_windows_auth": True,  # Đổi thành True để dùng Windows Authentication
    "username": "sa",
    "password": "luukhoi1562005"
}

class Database:
    def __init__(self):
        if SQL_SERVER_CONFIG["use_windows_auth"]:
             self.conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER_CONFIG["server"]};DATABASE={SQL_SERVER_CONFIG["database"]};Trusted_Connection=yes;'
        else:
            self.conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER_CONFIG["server"]};DATABASE={SQL_SERVER_CONFIG["database"]};UID={SQL_SERVER_CONFIG["username"]};PWD={SQL_SERVER_CONFIG["password"]};'
        self.create_tables()

    def get_connection(self):
        return pyodbc.connect(self.conn_str)

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
            CREATE TABLE users (
                id INT PRIMARY KEY IDENTITY(1,1),
                username NVARCHAR(50) UNIQUE NOT NULL,
                password NVARCHAR(64) NOT NULL,
                elo INT DEFAULT 1200,
                matches_played INT DEFAULT 0,
                wins INT DEFAULT 0,
                role NVARCHAR(20) DEFAULT 'user',
                fullname NVARCHAR(100) DEFAULT '',
                email NVARCHAR(100) DEFAULT '',
                phone NVARCHAR(20) DEFAULT ''
            )
        ''')
        
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='matches' AND xtype='U')
            CREATE TABLE matches (
                id INT PRIMARY KEY IDENTITY(1,1),
                user_id INT NOT NULL,
                opponent NVARCHAR(50) NOT NULL,
                result NVARCHAR(20) NOT NULL,
                played_at DATETIME DEFAULT GETDATE()
            )
        ''')
        
        conn.commit()
        conn.close()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, fullname="", email="", phone=""):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            role = 'admin' if count == 0 else 'user'
            
            cursor.execute("INSERT INTO users (username, password, role, fullname, email, phone) VALUES (?, ?, ?, ?, ?, ?)",
                         (username, password, role, fullname, email, phone))
            conn.commit()
            conn.close()
            return True, f"Đăng ký thành công! ({role})"
        except pyodbc.IntegrityError:
            return False, "Tên đăng nhập đã tồn tại!"
        except Exception as e:
            return False, f"Lỗi: {e}"

    def login_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        # (SỬA) So sánh mật khẩu gốc không hash (KHÔNG AN TOÀN - chỉ dùng cho testing!)
        # hashed_pw = self.hash_password(password)
        
        cursor.execute("""
            SELECT id, username, elo, matches_played, wins, role, fullname, email, phone 
            FROM users WHERE username=? AND password=?
        """, (username, password))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user_data = {
                "id": row[0], "username": row[1], "elo": row[2],
                "matches": row[3], "wins": row[4], "role": row[5],
                "fullname": row[6] if row[6] else "",
                "email": row[7] if row[7] else "",
                "phone": row[8] if row[8] else ""
            }
            return True, user_data
        return False, None

    def update_user_info(self, user_id, fullname, email, phone):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET fullname=?, email=?, phone=? WHERE id=?", (fullname, email, phone, user_id))
            conn.commit()
            conn.close()
            return True
        except: 
            return False

    def update_user_role(self, user_id, new_role):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
            conn.commit()
            conn.close()
            return True
        except: 
            return False

    def get_all_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, elo, role FROM users")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_user(self, user_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except: 
            return False

    def update_stats(self, user_id, won=False, elo_change=0):
        conn = self.get_connection()
        cursor = conn.cursor()
        if won:
            cursor.execute("UPDATE users SET matches_played = matches_played + 1, wins = wins + 1, elo = elo + ? WHERE id = ?", (elo_change, user_id))
        else:
            cursor.execute("UPDATE users SET matches_played = matches_played + 1, elo = elo + ? WHERE id = ?", (elo_change, user_id))
        conn.commit()
        conn.close()

    def save_match_result(self, user_id, opponent, result):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO matches (user_id, opponent, result) VALUES (?, ?, ?)", (user_id, opponent, result))
        conn.commit()
        conn.close()

    def get_user_history(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT opponent, result, played_at FROM matches WHERE user_id=? ORDER BY played_at DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        formatted_rows = []
        for row in rows:
            opp, res, date_obj = row
            date_str = date_obj.strftime('%Y-%m-%d %H:%M') if date_obj else ''
            formatted_rows.append((opp, res, date_str))
        return formatted_rows
        
    def export_state(self): 
        return {}
