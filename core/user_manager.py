import hashlib
from db.db import get_conn  # dùng file db.py đã tạo từ trước

def hash_password(password):
    """Mã hóa mật khẩu bằng SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password, role):
    conn = get_conn()
    cursor = conn.cursor()

    # Kiểm tra người dùng đã tồn tại chưa
    cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Tên người dùng đã tồn tại"

    hashed = hash_password(password)
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
            (username, hashed, role)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Lỗi: {str(e)}"

    conn.close()
    return True, "Thêm người dùng thành công"

def delete_user(username):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = %s", (username,))
    conn.commit()
    conn.close()

def validate_user(username, password):
    conn = get_conn()
    cursor = conn.cursor()
    hashed = hash_password(password)

    cursor.execute(
        "SELECT role FROM users WHERE username = %s AND password_hash = %s",
        (username, hashed)
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        return True, result[0]  # trả về True và vai trò
    return False, None

def get_all_users():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users ORDER BY username")
    users = cursor.fetchall()
    conn.close()
    return [{"username": u[0], "role": u[1]} for u in users]
