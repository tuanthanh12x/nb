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
    """
    SỬA LỖI: Lấy cả ID, username và role của tất cả người dùng.
    Trả về danh sách các dictionary, mỗi dictionary chứa đủ 'id', 'username', 'role'.
    """
    users_list = []
    # Thêm 'id' vào câu lệnh SELECT
    sql = "SELECT id, username, role FROM users ORDER BY username"
    try:
        with get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                users_data = cursor.fetchall()
                for u in users_data:
                    users_list.append({"id": u[0], "username": u[1], "role": u[2]})
    except Exception as e:
        print(f"Lỗi khi lấy danh sách người dùng: {e}")

    return users_list
def update_user_password(user_id, new_password):
    """Cập nhật mật khẩu mới cho người dùng theo ID."""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        hashed_pw = hash_password(new_password)
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (hashed_pw, user_id)
        )
        conn.commit()
        conn.close()
        return True, "Cập nhật mật khẩu thành công."
    except Exception as e:
        return False, f"Lỗi khi cập nhật mật khẩu: {e}"